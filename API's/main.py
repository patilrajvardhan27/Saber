"""
Saber BldgAuditTool – FastAPI backend
Run: uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — must be set before any other matplotlib import
import pandas as pd
import io
import os
import sys
import math
import glob as glob_module
import asyncio
from concurrent.futures import ThreadPoolExecutor

# ── Pandas 2.2+ frequency-alias compatibility patch ───────────────────────────
# BldgAuditToolPackage uses deprecated aliases ('M', '24H', 'Q', etc.) that were
# removed in pandas 2.2. Patch resample / date_range before the package is imported.
_FREQ_MAP = {
    "M": "ME", "Q": "QE", "A": "YE", "Y": "YE",
    "BM": "BME", "BQ": "BQE", "BA": "BYE",
    "H": "h", "T": "min", "S": "s",
}

import re as _re

def _fix_freq(f):
    if not isinstance(f, str):
        return f
    # Exact alias match first (e.g. "M" → "ME")
    if f in _FREQ_MAP:
        return _FREQ_MAP[f]
    # Compound alias: leading digits + unit (e.g. "24H" → "24h", "2M" → "2ME")
    m = _re.fullmatch(r"(\d+)([A-Za-z]+)", f)
    if m:
        unit = _FREQ_MAP.get(m.group(2), m.group(2))
        return m.group(1) + unit
    return f

_orig_df_resample  = pd.DataFrame.resample
_orig_ser_resample = pd.Series.resample
_orig_date_range   = pd.date_range

def _df_resample(self, rule, *a, **kw):
    return _orig_df_resample(self, _fix_freq(rule), *a, **kw)

def _ser_resample(self, rule, *a, **kw):
    return _orig_ser_resample(self, _fix_freq(rule), *a, **kw)

def _date_range(*a, **kw):
    if "freq" in kw:
        kw["freq"] = _fix_freq(kw["freq"])
    return _orig_date_range(*a, **kw)

pd.DataFrame.resample = _df_resample  # type: ignore[method-assign]
pd.Series.resample    = _ser_resample  # type: ignore[method-assign]
pd.date_range         = _date_range  # type: ignore[assignment]
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="Saber BldgAuditTool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLDG_AUDIT_DIR = os.path.normpath(os.path.join(BASE_DIR, "../BldgAuditToolSimple_v1"))
PROJECTS_DIR = os.path.join(BLDG_AUDIT_DIR, "Projects")
sys.path.insert(0, BLDG_AUDIT_DIR)

# The measure-evaluation code (MeasureClass / MeasureOptions) loads the cost/option
# CSVs with paths relative to the working directory, e.g. os.path.join("Measures", ...).
# The desktop GUI runs with its working directory at the package root, so mirror that
# here. The baseline analysis pipeline uses only absolute paths, so this is safe.
os.chdir(BLDG_AUDIT_DIR)

# ── InverseModel safety patches ────────────────────────────────────────────────
# Bug 1: model.py fit() swallows curve_fit failures but leaves self.p unset;
#        fit_model() then crashes with AttributeError at `self.p_init = self.p`.
# Bug 2: fit_model() can return a bare False / short tuple (not a tuple, or fewer
#        than 4 items) when curve_fit fails, but the current package always unpacks
#        4 values from it (has_fit, model_type, model_parameters, model_r2 — the R²
#        was added by the "Edited to make the R2 value correct" changes). A short
#        return then raises "not enough values to unpack (expected 4, got 3)".
try:
    import numpy as _np_patch
    from BldgAuditToolPackage.model import InverseModel as _InverseModel

    _orig_inv_fit = _InverseModel.fit

    def _safe_inv_fit(self):
        try:
            _orig_inv_fit(self)
        except Exception:
            pass
        if not hasattr(self, 'p'):
            if hasattr(self, 'temperature') and hasattr(self, 'eui'):
                avg_temp = float(_np_patch.nanmean(self.temperature))
                avg_eui  = float(_np_patch.nanmean(self.eui))
            else:
                avg_temp, avg_eui = 50.0, 0.0
            self.p   = _np_patch.array([avg_temp - 5.0, avg_temp + 5.0, avg_eui, 0.0, 0.0])
            self.e   = _np_patch.zeros((5, 5))
            self.hcp, self.ccp, self.base, self.hsl, self.csl = self.p
            self.p_base = 1.0
            self.p_hsl  = 1.0
            self.p_csl  = 1.0
            self.has_fit = False

    _InverseModel.fit = _safe_inv_fit

    _orig_inv_fit_model = _InverseModel.fit_model

    # Always hand back a 4-tuple (has_fit, model_type, model_parameters, model_r2)
    # so BuildTemperatureBasedModel's `a, b, c, d = fit_model()` never crashes.
    def _safe_inv_fit_model(self, has_fit=False, threshold=0.1):
        no_fit = (False, "No fit", getattr(self, 'p', _np_patch.zeros(5)), 0.0)
        try:
            result = _orig_inv_fit_model(self, has_fit, threshold)
            if not isinstance(result, tuple):
                return no_fit
            if len(result) == 4:
                return result
            if len(result) == 3:
                # Older 3-value return shape — append a zero R² to make it 4.
                return (result[0], result[1], result[2], 0.0)
            return no_fit
        except Exception:
            return no_fit

    _InverseModel.fit_model = _safe_inv_fit_model
except Exception:
    pass

# Bug 3: when the model comes back as "No fit", BuildTemperatureBasedModel still
#        calls Plot_Matplotlib(...).plot_graph_cp(). In graph.py "No fit" matches no
#        model-type branch, so eui_values stays None and r_squared is never assigned,
#        making the title line raise NameError and 500 the whole analysis. The change-
#        point PNG is optional (main.py's _b64 already returns None for a missing
#        file), so a plotting failure must not abort the run — swallow it.
try:
    from BldgAuditToolPackage.graph import Plot_Matplotlib as _PlotMatplotlib

    _orig_plot_cp = _PlotMatplotlib.plot_graph_cp

    def _safe_plot_cp(self, *args, **kwargs):
        try:
            return _orig_plot_cp(self, *args, **kwargs)
        except Exception:
            return 0.0  # caller discards the return; just don't crash the analysis

    _PlotMatplotlib.plot_graph_cp = _safe_plot_cp
except Exception:
    pass
# ──────────────────────────────────────────────────────────────────────────────

# ── PlotInverseModelComparison shape-mismatch patch ─────────────────────────────
# PlotInverseModelComparison compares MonthlyEndUseBreakdown.csv (one row per
# distinct calendar month present in the downloaded NOAA weather data) against
# dfutilDataSorted (one row per utility bill, normally 12). If the weather download
# doesn't cover all 12 calendar months (e.g. the most recent months aren't published
# by NOAA yet), df_MonthlyEndUse has fewer rows than dfutilDataSorted, and
# `ThermPred - np.array(ThermMean)` raises "operands could not be broadcast together
# with shapes (N,) (12,)", 500-ing /run-analysis and /run-analysis-manual.
#
# Fix: these utility-vs-model comparison plots (NaturalGasMonthlyBreakdown.png /
# ElectricityMonthlyBreakdown.png) are optional — _b64() already returns None for a
# missing file — so swallow any error here and skip them rather than failing the run.
try:
    from BldgAuditToolPackage.PostProcessing import PlotResults as _PlotResults

    _orig_plot_inverse_cmp = _PlotResults.PlotInverseModelComparison

    def _safe_plot_inverse_cmp(self, *args, **kwargs):
        try:
            return _orig_plot_inverse_cmp(self, *args, **kwargs)
        except Exception:
            return None

    _PlotResults.PlotInverseModelComparison = _safe_plot_inverse_cmp
except Exception:
    pass
# ──────────────────────────────────────────────────────────────────────────────

# ── PlotEEMEndUseComparison shape-mismatch patch ────────────────────────────────
# PlotEEMEndUseComparison (used by /run-ecm) compares the baseline's
# MonthlyEndUseBreakdown.csv against the EEM package's MonthlyEndUseBreakdown.csv
# row-for-row (ThermPred - ThermPred_EEM, ElecPred - ElecPred_EEM). If the two runs'
# NOAA weather downloads cover a different number of calendar months, the two CSVs
# have different row counts and this raises "operands could not be broadcast
# together with shapes (M,) (N,)", 500-ing /run-ecm.
#
# Fix: these EEM-vs-baseline comparison plots (NaturalGasMonthlyEEMComp.png /
# ElectricityMonthlyEEMComp.png) are optional — _b64_ecm() already returns None for
# a missing file — so swallow any error here and skip them rather than failing the run.
try:
    from BldgAuditToolPackage.PostProcessing import PlotResults as _PlotResults2

    _orig_plot_eem_cmp = _PlotResults2.PlotEEMEndUseComparison

    def _safe_plot_eem_cmp(self, *args, **kwargs):
        try:
            return _orig_plot_eem_cmp(self, *args, **kwargs)
        except Exception:
            return None

    _PlotResults2.PlotEEMEndUseComparison = _safe_plot_eem_cmp
except Exception:
    pass
# ──────────────────────────────────────────────────────────────────────────────

# ── BuildChangePointModel weather-alignment patch ──────────────────────────────
# AnalyzeUtilityData builds self.df_month = df_weather.resample("M").mean() and then
# treats it positionally: BuildTemperatureBasedModel pairs df_month["Temp_F"] with
# the utility records for the change-point fit/scatter, and BuildDegreeDayBasedModel
# derives its temperature masks from df_month too. All of this assumes df_month has
# exactly one row per utility record, in the same order.
#
# The weather coverage NOAA returns is not guaranteed to land on whole calendar
# months, so resample("M") can produce an extra (or missing) monthly bucket. The
# resulting length mismatch makes matplotlib's scatter raise
# "x and y must be the same size", which surfaces as an HTTP 500 ("Analysis failed:
# x and y must be the same size") on /run-analysis and /run-analysis-manual.
#
# Fix: after the model is constructed, rebuild self.df_month["Temp_F"] by looking up
# the monthly mean temperature for each utility record's (Year, Month). Months with
# no weather match fall back to the overall mean so every utility row keeps a
# temperature and all downstream arrays stay the same length. Inside this class
# df_month is only ever read as ["Temp_F"].values, so replacing the frame is safe.
try:
    import numpy as _np_align
    from BldgAuditToolPackage.AnalyzeUtilityData import BuildChangePointModel as _BCPM

    _orig_bcpm_init = _BCPM.__init__

    def _aligned_bcpm_init(self, *args, **kwargs):
        _orig_bcpm_init(self, *args, **kwargs)
        try:
            monthly = self.df_month
            temp_by_ym = pd.Series(
                monthly["Temp_F"].values,
                index=pd.MultiIndex.from_arrays(
                    [monthly.index.year, monthly.index.month], names=["Year", "Month"]
                ),
            )
            temp_by_ym = temp_by_ym[~temp_by_ym.index.duplicated()]
            overall_mean = float(_np_align.nanmean(monthly["Temp_F"].values))
            keys = zip(self.dfutilDataSorted["Year"].astype(int),
                       self.dfutilDataSorted["Month"].astype(int))
            aligned = [temp_by_ym.get(k, overall_mean) for k in keys]
            # Guard against a present-but-NaN monthly mean so no row is left as NaN.
            aligned = [overall_mean if v != v else float(v) for v in aligned]
            self.df_month = pd.DataFrame({"Temp_F": aligned})
        except Exception:
            # If anything goes wrong, leave df_month untouched (original behaviour).
            pass

    _BCPM.__init__ = _aligned_bcpm_init
except Exception:
    pass
# ──────────────────────────────────────────────────────────────────────────────

# UPLOADS_DIR is where user-uploaded utility CSVs and project folders are stored.
# On Fly.io this is a persistent volume (/data/uploads); locally it falls back to PROJECTS_DIR.
UPLOADS_DIR = os.environ.get("UPLOADS_DIR", PROJECTS_DIR)
os.makedirs(UPLOADS_DIR, exist_ok=True)

_executor = ThreadPoolExecutor(max_workers=2)

# ── In-memory cache for baseline analysis results (keyed by project_name) ──────
_analysis_cache: dict[str, dict] = {}

# ── In-memory cache for uploaded pkl DataFrames (keyed by project_name) ────────
_pkl_df_cache: dict[str, "pd.DataFrame"] = {}

# ── PKL field mapping ──────────────────────────────────────────────────────────
PROP_KEY_MAP: dict[str, str] = {
    "ProjectName":        "projectName",
    "BuildingType":       "buildingType",
    "Location":           "location",
    "Shape":              "shapeType",
    "x1":                 "x1",
    "x2":                 "x2",
    "y1":                 "y1",
    "y2":                 "y2",
    "FloorArea":          "floorArea",
    "FloorQty":           "flrQty",
    "WallHeight":         "wallHt",
    "WindowHeight":       "windowHt",
    "WWR_Front":          "wwrFront",
    "WWR_Left":           "wwrLeft",
    "WWR_Back":           "wwrBack",
    "WWR_Right":          "wwrRight",
    "overhangdepth":      "overhang",
    "nWindow":            "nWindow",
    "R-WallInsulation":   "wallInsulation",
    "R-CeilingInsulation":"ceilingInsulation",
    "R-SlabInsulation":   "slabInsulation",
    "Foundation":         "foundation",
    "ExtWallConst":       "extWallConst",
    "ExtRoofConst":       "extRoofConst",
    "ACH50":              "ach50",
    "Tsph":               "tsph",
    "Tspc":               "tspc",
    "DHWSystemType":      "dhwSystemType",
    "DHWTankVol":         "dhwTankVol",
    "EPD":                "epd",
    "GPD":                "gpd",
    "LPD":                "lpd",
    "HeatingEquipment":   "heatingEqp",
    "CoolingEquipment":   "coolingEqp",
    "CoolingEff":         "coolingEff",
    "HeatingEff":         "heatingEff",
    "CoolingEffCustom":   "coolingEffCustom",
    "HeatingEffCustom":   "heatingEffCustom",
    "nNightSetbackHours": "nNightSetbackHours",
    "NightSetback":       "nightSetback",
    "Daylighting":        "daylighting",
    "SwampCooler":        "swampCooler",
    "Economizer":         "economizer",
    "LEDCurrent":         "led",
    "LEDECM":             "ecmLED",
    "EquipLoadRed":       "ecmReduceEquipLoad",
    "OccupancySensor":    "ecmOccupancySensor",
    "nHoursLighting":     "nHoursLighting",   # hours per day — critical for lighting calc
}

LIST_FIELDS: dict[str, str] = {
    "Orientation":    "orientation",
    "WindowMaterial": "windowMaterial",
}


# Frontend display names → exact names in Materials-WindowMaterial.csv
_WIN_MAT_MAP: dict[str, str] = {
    "Low-e Double Pane Clear Air Filled":       "Low e Double Pane Medium SHGC Air filled",
    "Low-e Double Pane Clear Argon Filled":     "Low e Double Pane Medium SHGC Argon filled",
    "Low-e Double Pane Insulated Air Filled":   "Low e Double Pane Medium SHGC Air filled Insulated",
    "Low-e Double Pane Insulated Argon Filled": "Low e Double Pane Medium SHGC Argon filled Insulated",
    "Low-e Triple Pane Clear Air Filled":       "Low e Triple Pane Low SHGC Air filled",
    "Low-e Triple Pane Clear Argon Filled":     "Low e Triple Pane Low SHGC Argon filled",
    "Low-e Triple Pane Insulated Air Filled":   "Low e Triple Pane Low SHGC Air filled Insulated",
    "Low-e Triple Pane Insulated Argon Filled": "Low e Triple Pane Low SHGC Argon filled Insulated",
}


# ── WindowMaterial baseline-name patch ─────────────────────────────────────────
# The EEM window option always comes from Materials-WindowMaterial.csv (canonical
# names), and the ECM selection already maps the chosen upgrade through _WIN_MAT_MAP
# above. The building's CURRENT window material, however, is stored straight from the
# frontend form, where the low-e options use friendlier display labels (e.g.
# "Low-e Double Pane Clear Air Filled"). Those labels aren't in the CSV, so the
# package's ImplementMeasures.WindowMaterial() baseline lookup
#   WindowConstOptions.loc[WindowConstOptions.WindowMaterial==WindowConstOrg,"Uvalue"].iloc[0]
# returns an empty Series and raises "single positional indexer is out-of-bounds",
# 500-ing the whole ECM run. ("Single Pane Clear"/"Double Pane Clear" map 1:1 to the
# CSV, which is why only low-e baselines hit this.)
#
# Fix: canonicalise both the original and EEM names through _WIN_MAT_MAP before the
# lookup so a display-name baseline resolves to its CSV row. Mapping is idempotent —
# already-canonical names pass straight through — so this also covers cached df_input
# and any -Baseline.pkl already saved with display names.
try:
    from BldgAuditToolPackage.EEMIndMeasureAnalysisObject import ImplementMeasures as _ImplementMeasures

    _orig_window_material = _ImplementMeasures.WindowMaterial

    def _safe_window_material(self, WindowConstOrg, WindowConstEEM):
        return _orig_window_material(
            self,
            _WIN_MAT_MAP.get(WindowConstOrg, WindowConstOrg),
            _WIN_MAT_MAP.get(WindowConstEEM, WindowConstEEM),
        )

    _ImplementMeasures.WindowMaterial = _safe_window_material
except Exception:
    pass


# ── Weather-download writable-directory patch ──────────────────────────────────
# NOAAData.download_weather_NOAA() saves NOAA station files to the *current working
# directory* using bare relative names (NOAA_Data.py: open('<station>-<year>.gz','wb'),
# gzip.open(...), os.remove(...)). At runtime cwd is BLDG_AUDIT_DIR
# (/opt/saber/BldgAuditToolSimple_v1), which the service user can't reliably write, so the
# download fails with "[Errno 13] Permission denied: '…-….gz'" and 500s the analysis/ECM.
#
# Fix: run the whole download inside a private temp dir (under /tmp, always writable by the
# service) so the transient .gz/.csv land there and are cleaned up — independent of
# /opt/saber permissions. os.chdir is process-global, so a module lock serialises
# downloads and cwd is restored in finally, keeping the steady-state working directory
# (needed for the package's relative Measures/Inputs reads) unchanged. download_weather_NOAA
# does no other relative-path I/O, so redirecting only its cwd is safe.
try:
    import tempfile as _tempfile_w, shutil as _shutil_w, threading as _threading_w
    from BldgAuditToolPackage.NOAA_Data import NOAAData as _NOAAData

    _weather_cwd_lock = _threading_w.Lock()
    _orig_download_weather = _NOAAData.download_weather_NOAA

    def _safe_download_weather(self):
        with _weather_cwd_lock:
            prev_cwd = os.getcwd()
            tmpdir = _tempfile_w.mkdtemp(prefix="noaa_weather_")
            try:
                os.chdir(tmpdir)
                return _orig_download_weather(self)
            finally:
                os.chdir(prev_cwd)
                _shutil_w.rmtree(tmpdir, ignore_errors=True)

    _NOAAData.download_weather_NOAA = _safe_download_weather
except Exception:
    pass


def _default_ceiling_const() -> str:
    """The floor-construction name the CeilingInsulation measure expects in df_input.

    CeilingConst is a fixed construction (the single row in
    Inputs/InputCSVData/Construction-Floor.csv) that PKL-based projects always carry,
    but the manual entry form never collects it. MeasureClass.SetMeasure reads it for
    the ceiling ECM (df_input[PropKey=="CeilingConst"]), so a form-built df_input
    without it raises "single positional indexer is out-of-bounds" at the .iloc[0].
    Read the value the package itself will look up (positionally, so a BOM/renamed
    header can't break it) so the two never drift; fall back to the known constant.
    """
    try:
        fc = pd.read_csv(os.path.join(BLDG_AUDIT_DIR, "Inputs", "InputCSVData", "Construction-Floor.csv"))
        return str(fc.iloc[0, 0])
    except Exception:
        return "Floor construction Reversed"


def _normalize_eff(value: str) -> str:
    """Convert display efficiency labels to the numeric strings the analysis package expects.

    Examples:
      "AFUE 90%"   → "0.9"
      "SEER2 13.4" → "13.4"
      "HSPF2 7.5"  → "7.5"
      "COP 1.0"    → "1.0"
    """
    import re as _re2
    if not isinstance(value, str):
        return value
    # AFUE XX% → XX/100
    m = _re2.match(r"AFUE\s+([\d.]+)%", value, _re2.IGNORECASE)
    if m:
        return str(float(m.group(1)) / 100)
    # SEER2/SEER/HSPF2/HSPF/COP followed by a number
    m = _re2.match(r"(?:SEER2?|HSPF2?|COP)\s+([\d.]+)", value, _re2.IGNORECASE)
    if m:
        return m.group(1)
    return value


def _ensure_cost_data(project_path: str) -> None:
    """Copy CostData into a project folder if it doesn't already exist."""
    dest = os.path.join(project_path, "CostData")
    if os.path.isdir(dest):
        return
    import shutil
    sources = glob_module.glob(os.path.join(PROJECTS_DIR, "*", "CostData"))
    if sources:
        shutil.copytree(sources[0], dest)


def _val(df: pd.DataFrame, key: str) -> str:
    rows = df.loc[df["PropKey"] == key, "PropValue"]
    if rows.empty:
        return ""
    v = rows.iloc[0]
    return "" if pd.isna(v) else str(v)


# ── PKL upload ─────────────────────────────────────────────────────────────────
@app.post("/upload-pkl")
async def upload_pkl(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith("-Baseline.pkl"):
        raise HTTPException(
            status_code=400,
            detail="Only files named <project>-Baseline.pkl are accepted (e.g. LakewoodTestCase-Baseline.pkl).",
        )

    contents = await file.read()
    try:
        df = pd.read_pickle(io.BytesIO(contents))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {exc}")

    if not isinstance(df, pd.DataFrame) or "PropKey" not in df.columns:
        raise HTTPException(status_code=422, detail="File does not contain expected PropKey/PropValue structure.")

    # Derive project name from the file's stem (strip "-Baseline.pkl") — nothing written to disk
    basename = os.path.basename(file.filename)
    project_name: str = _val(df, "ProjectName") or basename[: -len("-Baseline.pkl")]

    # Cache df in memory only — no files saved locally
    _pkl_df_cache[project_name] = df

    fields: dict[str, object] = {}
    for prop_key, form_key in PROP_KEY_MAP.items():
        fields[form_key] = _val(df, prop_key)
    for prop_key, form_key in LIST_FIELDS.items():
        raw = _val(df, prop_key)
        fields[form_key] = [raw] if raw else []

    populated_keys = [k for k, v in fields.items() if v]
    return {
        "fields": fields,
        "count": len(populated_keys),
        "populated_keys": populated_keys,
        "project_name": project_name,
    }


# ── Manual utility data entry ──────────────────────────────────────────────────
class UtilityDataManualRequest(BaseModel):
    year1: int
    year2: int | None = None
    year3: int | None = None
    rows: list[dict]  # 12 dicts: kwh1, therms1, kwh2, therms2, kwh3, therms3


@app.post("/save-utility-data/{project_name}")
async def save_utility_data(project_name: str, req: UtilityDataManualRequest):
    import calendar

    if len(req.rows) != 12:
        raise HTTPException(status_code=400, detail="Exactly 12 monthly rows are required.")

    project_path = os.path.join(UPLOADS_DIR, project_name)
    os.makedirs(project_path, exist_ok=True)

    y1 = req.year1
    y2 = req.year2 if req.year2 else y1
    y3 = req.year3 if req.year3 else y1

    def _num(v):
        if v is None or v == "":
            return float("nan")
        try:
            return float(v)
        except (TypeError, ValueError):
            return float("nan")

    data: dict[str, list] = {
        f"Year 1 - kWh{y1}": [],
        f"Year 1 - Therms{y1}": [],
        f"Year 2 - kWh{y2}": [],
        f"Year 2 - Therms{y2}": [],
        f"Year 3 - kWh{y3}": [],
        f"Year 3 - Therms{y3}": [],
        "BillDays": [],
    }

    for i, row in enumerate(req.rows):
        month = i + 1
        data[f"Year 1 - kWh{y1}"].append(_num(row.get("kwh1")))
        data[f"Year 1 - Therms{y1}"].append(_num(row.get("therms1")))
        data[f"Year 2 - kWh{y2}"].append(_num(row.get("kwh2")))
        data[f"Year 2 - Therms{y2}"].append(_num(row.get("therms2")))
        data[f"Year 3 - kWh{y3}"].append(_num(row.get("kwh3")))
        data[f"Year 3 - Therms{y3}"].append(_num(row.get("therms3")))
        provided = _num(row.get("billDays"))
        data["BillDays"].append(provided if not math.isnan(provided) else calendar.monthrange(y1, month)[1])

    df = pd.DataFrame(data, index=range(1, 13))
    save_path = os.path.join(project_path, f"{project_name}_UtilityData.csv")
    df.to_csv(save_path)

    return {"status": "ok", "saved_as": f"{project_name}_UtilityData.csv"}


# ── Utility CSV upload ─────────────────────────────────────────────────────────
@app.post("/upload-utility/{project_name}")
async def upload_utility(project_name: str, file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    project_path = os.path.join(UPLOADS_DIR, project_name)
    os.makedirs(project_path, exist_ok=True)

    # Always save as {ProjectName}_UtilityData.csv (what the analysis engine expects)
    save_path = os.path.join(project_path, f"{project_name}_UtilityData.csv")
    with open(save_path, "wb") as fout:
        fout.write(contents)

    return {"status": "ok", "saved_as": f"{project_name}_UtilityData.csv"}


# ── Run analysis ───────────────────────────────────────────────────────────────
def _run_analysis_sync(project_name: str, df_input: "pd.DataFrame | None" = None) -> dict:
    """Runs the full BldgAuditTool analysis pipeline in a temp directory. Nothing is saved locally."""
    import tempfile, shutil, base64
    from BldgAuditToolPackage.AnalyzeUtilityData import (
        GetWeather,
        BuildChangePointModel,
    )
    from BldgAuditToolPackage.RunSimulationCase import GetMonthlyEndUseBreakdown
    from BldgAuditToolPackage.PostProcessing import PlotResults

    if df_input is None:
        raise ValueError("No building data provided — please upload a PKL file first.")

    bldg_location = _val(df_input, "Location")
    if not bldg_location:
        raise ValueError("Building location is missing from the PKL file.")

    # EnergyAnalysis reads PropKey == "EPD"/"GPD" via .iloc[0]; a missing row raises
    # IndexError. PKLs/forms post-migration include them, but guard against older
    # PKLs that predate the EPD/GPD migration. EPD defaults to 1.0 W/ft²; GPD stays
    # empty (treated as "no gas cooking", which skips NG disaggregation).
    for _pk, _default in (("EPD", "1.0"), ("GPD", None)):
        if not (df_input["PropKey"] == _pk).any():
            df_input = pd.concat(
                [df_input, pd.DataFrame([{"PropKey": _pk, "PropValue": _default}])],
                ignore_index=True,
            )

    # All file I/O happens inside a temp directory that is deleted when done
    tmp = tempfile.mkdtemp()
    # The package writes every plot into a "Results" subfolder of the run dir
    # (e.g. graph.py / PostProcessing.py savefig to <ProjectPath>/Results/...).
    results_dir = os.path.join(tmp, "Results")
    os.makedirs(results_dir, exist_ok=True)
    try:
        util_path = os.path.join(tmp, f"{project_name}_UtilityData.csv")

        # Check UPLOADS_DIR (persistent volume / user uploads) first, then
        # fall back to PROJECTS_DIR (pre-seeded repo data, e.g. LakewoodTestCase).
        # Never fall back to a *different* project's data.
        _upload_csv  = os.path.join(UPLOADS_DIR,   project_name, f"{project_name}_UtilityData.csv")
        _seeded_csv  = os.path.join(PROJECTS_DIR,  project_name, f"{project_name}_UtilityData.csv")
        if os.path.exists(_upload_csv):
            shutil.copy(_upload_csv, util_path)
            has_utility_data = True
        elif os.path.exists(_seeded_csv):
            shutil.copy(_seeded_csv, util_path)
            has_utility_data = True
        else:
            # No utility data — write a zero-value stub so the pipeline can still run.
            # The change-point model will produce "No fit" / zero parameters, which is
            # handled gracefully by BuildDegreeDayBasedModel (NaN→0 replacement on its
            # last line) and by Energy (zero change-points → zero heating/cooling).
            import csv as _csv
            bill_days = [31,28,31,30,31,30,31,31,30,31,30,31]
            with open(util_path, "w", newline="") as _f:
                w = _csv.writer(_f)
                w.writerow(["", "Year 1 - kWh2024", "Year 1 - Therms2024", "BillDays"])
                for i, bd in enumerate(bill_days, start=1):
                    w.writerow([i, 0, 0, bd])
            has_utility_data = False

        # CostData: copy from an existing project so any cost-data lookups during the run resolve
        cost_sources = glob_module.glob(os.path.join(PROJECTS_DIR, "*", "CostData"))
        if cost_sources:
            shutil.copytree(cost_sources[0], os.path.join(tmp, "CostData"))

        # 1. Download weather data (saved to tmp, deleted with it)
        df_weather, weather_station_name = GetWeather(tmp, project_name, bldg_location)

        # 2. Build change-point models
        cpm = BuildChangePointModel(tmp, project_name, df_input, df_weather)
        (model_type_cooling, model_params_cooling,
         model_type_heating, model_params_heating) = cpm.BuildTemperatureBasedModel()
        dd_results, dfutil_sorted = cpm.BuildDegreeDayBasedModel(
            model_type_cooling, model_params_cooling, model_type_heating, model_params_heating
        )
        best_model = cpm.ChooseBestModel(dd_results, model_params_heating, model_params_cooling, tmp)

        # 3. Monthly end-use breakdown. GetMonthlyEndUseBreakdown writes
        #    MonthlyEndUseBreakdown.csv (and BestModelParams.csv) into the run dir
        #    and mutates best_model in place (adds BLC_Heating_*/BLC_Cooling_EL,
        #    nHours*, EPD). It no longer returns the DataFrame, so read it back.
        GetMonthlyEndUseBreakdown(best_model, df_weather, df_input, tmp)
        df_monthly = pd.read_csv(os.path.join(tmp, "MonthlyEndUseBreakdown.csv"))

        # 4. Generate plots. PlotResults reads MonthlyEndUseBreakdown.csv from the
        #    run dir and writes every PNG into <run_dir>/Results/.
        plotter = PlotResults(True, tmp)
        plotter.PlotWeather(df_weather, weather_station_name)
        plotter.PlotEndUseBreakdown(tmp)
        if has_utility_data:
            plotter.PlotInverseModelComparison(tmp, dfutil_sorted)

        # 5. Encode each PNG as base64 (files stay in tmp/Results and are deleted below)
        def _b64(name: str) -> str | None:
            path = os.path.join(results_dir, name)
            if not os.path.exists(path):
                return None
            with open(path, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

        all_pngs = [os.path.basename(p) for p in glob_module.glob(os.path.join(results_dir, "*.png"))]
        weather_plot = f"WeatherPlot_{weather_station_name}.png"
        elec_temp = next((f for f in all_pngs if f.startswith("Electricity_") and f.endswith("_TempBasedChngPtModel.png")), None)
        ff_temp   = next((f for f in all_pngs if f.startswith("Fossil Fuel_")  and f.endswith("_TempBasedChngPtModel.png")), None)
        elec_dd   = next((f for f in ["Electricity_Cooling_DDBasedChngPtModel.png", "Electricity_Heating_DDBasedChngPtModel.png"]
                          if os.path.exists(os.path.join(results_dir, f))), None)

        plots = {
            "weather":         _b64(weather_plot),
            "elec_temp_model": _b64(elec_temp) if elec_temp else None,
            "ff_temp_model":   _b64(ff_temp)   if ff_temp   else None,
            "ff_dd_model":     _b64("FossilFuel_Heating_DDBasedChngPtModel.png"),
            "elec_dd_model":   _b64(elec_dd)   if elec_dd   else None,
            "end_use":         _b64("EndUseBreakdown.png"),
            "ng_monthly":      _b64("NaturalGasMonthlyBreakdown.png"),
            "elec_monthly":    _b64("ElectricityMonthlyBreakdown.png"),
        }

        # 6. Cache in-memory results for ECM evaluation.
        # Use "EL-" / "NG-" to match only end-use columns (e.g. "EL-Space Cooling"),
        # not degree-day columns ("HDD_EL"). The BLC coefficients needed by the ECM
        # measures (BLC_Heating_NG/BLC_Heating_EL/BLC_Cooling_EL) were already added to
        # best_model in place by GetMonthlyEndUseBreakdown → GetAllModelParams.
        best_model["OrgTotalElectricity"] = df_monthly.loc[:, df_monthly.columns.str.contains("EL-")].sum().sum() / 3.412
        best_model["OrgTotalNaturalGas"]  = df_monthly.loc[:, df_monthly.columns.str.contains("NG-")].sum().sum() / 100

        _analysis_cache[project_name] = {
            "df_weather": df_weather,
            "df_input": df_input,
            "best_model": best_model,
            "df_monthly": df_monthly,
            "dfutil_sorted": dfutil_sorted,
        }

        return {"status": "success", "plots": plots, "weather_station": weather_station_name}

    finally:
        shutil.rmtree(tmp, ignore_errors=True)  # delete everything in the temp dir


@app.post("/run-analysis/{project_name}")
async def run_analysis(project_name: str):
    # Use the cached df from the pkl upload; _run_analysis_sync borrows utility CSV if needed
    df_input = _pkl_df_cache.get(project_name)

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(_executor, _run_analysis_sync, project_name, df_input)
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


# ── ECM evaluation ────────────────────────────────────────────────────────────
class EcmRequest(BaseModel):
    ecm_wall_insulation: str = ""
    ecm_infiltration: str = ""
    ecm_ceiling_insulation: str = ""
    ecm_window_material: str = ""
    ecm_occupancy_sensor: str = "No"
    ecm_led: str = ""
    ecm_daylighting: str = "No"
    ecm_economizer: str = "No"
    ecm_cooling_eff: str = ""   # e.g. "SEER2 13.4" — normalized to float in backend
    ecm_heating_eff: str = ""   # e.g. "AFUE 90%"   — normalized to float in backend
    kwh_rate: float = 0.12
    therm_rate: float = 1.20
    discount_rate: float = 3.0
    lifetime: int = 20
    form_data: dict = {}


# Maps each frontend ECM request field to the MeasurePackage option group plus the
# label the frontend's results table expects (see ECMStep.tsx MEASURE_LABELS).
_ECM_MEASURE_GROUPS = {
    "WallInsOptions":         "WallInsulation",
    "InfilOptions":           "Infiltration",
    "CeilInsOptions":         "CeilingInsulation",
    "WindowMatOptions":       "WindowMaterial",
    "DaylightingOptions":     "DaylightingSensor",
    "OccSensorOptions":       "OccupancySensor",
    "PercentageLEDOptions":   "LEDLighting",
    "ReduceEquipLoadOptions": "ReduceEquipmentLoad",
    "EconomizerOptions":      "Economizer",
    "CoolingEqpOptions":      "CoolingEff",
    "HeatingEqpOptions":      "HeatingEff",
}


def _build_measure_types(df_input: "pd.DataFrame", project_path: str) -> dict:
    """Build the MeasureTypes option lists exactly as GUI_Functionality.SetECMBaseProperty
    does: filter each option list against the current building, then prepend the current
    value as index 0. Reads SummaryResults.csv from project_path and the option CSVs from
    the package's Measures/ directory (relative to the working dir, which is BLDG_AUDIT_DIR)."""
    from BldgAuditToolPackage.MeasureClass import MeasureOptions
    from BldgAuditToolPackage.MeasureSort import VariableFilter, AddCurrentOptionasMeasure

    opt = MeasureOptions(project_path)
    refs = {
        "WallInsOptions":         opt.WallInsulation,
        "CeilInsOptions":         opt.CeilingInsulation,
        "InfilOptions":           opt.Infiltration,
        "WindowMatOptions":       opt.WindowMaterial,
        "DaylightingOptions":     opt.DaylightingControls,
        "OccSensorOptions":       opt.OccupancySensorControls,
        "PercentageLEDOptions":   opt.PercentageLED,
        "ReduceEquipLoadOptions": opt.ReduceEquipmentLoad,
        "EconomizerOptions":      opt.Economizer,
        "NightSetbackOptions":    opt.NightSetback,
        "HoursNightSetbackOptions": opt.HoursNightSetback,
        "HeatingEqpOptions":      opt.HeatingEquipment,
        "CoolingEqpOptions":      opt.CoolingEquipment,
        "DHWEqpOptions":          opt.DHWEquipment,
    }
    measure_types: dict = {}
    for name, func in refs.items():
        # Build each group independently so an option set that can't be built for this
        # building (e.g. HVAC with incomplete equipment data) doesn't block the others.
        try:
            filtered = VariableFilter(df_input, func())
            measure_types[name] = AddCurrentOptionasMeasure(df_input, func()[0].PropName, filtered)
        except Exception:
            measure_types[name] = None
    return measure_types


def _run_ecm_sync(project_name: str, req: EcmRequest) -> dict:
    import tempfile, shutil as _shutil, base64, copy
    from BldgAuditToolPackage.RunSimulationCase import GetSummaryResults
    from BldgAuditToolPackage.MeasurePackageClass import MeasurePackage, MeasurePackageUtilities
    from BldgAuditToolPackage.PostProcessing import PlotResults

    if project_name not in _analysis_cache:
        raise RuntimeError("Baseline analysis not found — please re-generate results first.")

    cache = _analysis_cache[project_name]
    df_weather = cache["df_weather"]
    df_input   = cache["df_input"].copy().reset_index(drop=True)
    df_monthly = cache["df_monthly"]
    best_model = copy.deepcopy(cache["best_model"])

    # Cost metrics drive the operating-cost / LCC math inside the package flow.
    r_disc = req.discount_rate / 100.0
    uspw = (1 - (1 + r_disc) ** (-req.lifetime)) / r_disc if r_disc != 0 else float(req.lifetime)
    cost_metrics = {"kWhRate": req.kwh_rate, "ThermRate": req.therm_rate, "USPW": uspw}

    project_path = tempfile.mkdtemp()
    try:
        # 1. Recreate the baseline artifacts the measure-package flow reads from ProjectPath:
        #    MonthlyEndUseBreakdown.csv + BestModelParams.csv come straight from the cached
        #    baseline; SummaryResults.csv is derived from them (adds Electricity/NaturalGas/TOC).
        df_monthly.to_csv(os.path.join(project_path, "MonthlyEndUseBreakdown.csv"), index=False)
        pd.DataFrame([best_model]).to_csv(os.path.join(project_path, "BestModelParams.csv"), index=False)
        GetSummaryResults(project_path, cost_metrics)

        baseline_sum = pd.read_csv(os.path.join(project_path, "SummaryResults.csv"))
        org_kwh    = float(baseline_sum["Electricity"].iloc[0])
        org_therms = float(baseline_sum["NaturalGas"].iloc[0])
        org_lcc    = float(baseline_sum["TOC"].iloc[0])

        # 2. Build the option lists, then map each selected ECM request to a PackageID index.
        measure_types = _build_measure_types(df_input, project_path)

        def _find(group: str, predicate) -> "int | None":
            options = measure_types.get(group)
            if not options:
                return None
            for i, m in enumerate(options):
                try:
                    if predicate(m):
                        return i
                except (ValueError, TypeError):
                    continue
            return None

        def _num(v):
            try:
                return float(v)
            except (ValueError, TypeError):
                return None

        # (group, predicate) for every selectable measure the frontend exposes.
        selections: list[tuple[str, int]] = []
        skipped: list[str] = []

        def _select(group: str, predicate, what: str):
            idx = _find(group, predicate)
            # idx 0 is the current/baseline option. idx None means the package filtered the
            # selection out because it isn't an upgrade over the building's current value
            # (the package's VariableFilter only keeps options better than the baseline).
            # Either way there is nothing to run, so skip the measure instead of failing the
            # whole package — and record it so the response can explain what was ignored.
            if idx is None:
                skipped.append(what)
                return
            if idx == 0:
                return
            selections.append((group, idx))

        if req.ecm_wall_insulation:
            _select("WallInsOptions", lambda m: str(m.PropValue) == req.ecm_wall_insulation, "wall insulation")
        if req.ecm_infiltration and _num(req.ecm_infiltration) is not None:
            # ACH50 only improves when it goes DOWN; a higher value is leakier, not an upgrade.
            # The package can't filter numeric options reliably, so reject non-improvements here.
            base_ach = _num(_val(df_input, "ACH50"))
            sel_ach  = _num(req.ecm_infiltration)
            if base_ach is not None and sel_ach >= base_ach:
                skipped.append("infiltration")
            else:
                _select("InfilOptions", lambda m: _num(m.PropValue) == sel_ach, "infiltration")
        if req.ecm_ceiling_insulation:
            _select("CeilInsOptions", lambda m: str(m.PropValue) == req.ecm_ceiling_insulation, "ceiling insulation")
        if req.ecm_window_material:
            win = _WIN_MAT_MAP.get(req.ecm_window_material, req.ecm_window_material)
            _select("WindowMatOptions", lambda m: str(m.PropValue) == win, "window material")
        if req.ecm_daylighting == "Yes":
            _select("DaylightingOptions", lambda m: str(m.PropValue) == "Yes", "daylighting controls")
        if req.ecm_occupancy_sensor == "Yes":
            _select("OccSensorOptions", lambda m: str(m.PropValue) == "Yes", "occupancy sensors")
        if req.ecm_economizer == "Yes":
            _select("EconomizerOptions", lambda m: str(m.PropValue) == "Yes", "economizer")
        if req.ecm_led and _num(req.ecm_led) is not None:
            # LED fraction only improves when it goes UP (more LEDs = less lighting energy).
            base_led = _num(_val(df_input, "LEDCurrent")) or 0.0
            sel_led  = _num(req.ecm_led)
            if sel_led <= base_led:
                skipped.append("LED fraction")
            else:
                _select("PercentageLEDOptions", lambda m: _num(m.PropValue) == sel_led, "LED fraction")

        if req.ecm_cooling_eff:
            clg_eqp = _val(df_input, "CoolingEquipment").replace(" ", "")
            clg_eff = _num(_normalize_eff(req.ecm_cooling_eff))
            if clg_eqp and clg_eqp != "NoCooling" and clg_eff:
                _select("CoolingEqpOptions",
                        lambda m: clg_eqp in m.PropName.replace(" ", "") and _num(m.PropValue) == clg_eff,
                        "cooling efficiency")
        if req.ecm_heating_eff:
            htg_eqp = _val(df_input, "HeatingEquipment").replace(" ", "")
            htg_eff = _num(_normalize_eff(req.ecm_heating_eff))
            if htg_eqp and htg_eqp != "NoHeating" and htg_eff:
                _select("HeatingEqpOptions",
                        lambda m: htg_eqp in m.PropName.replace(" ", "") and _num(m.PropValue) == htg_eff,
                        "heating efficiency")

        util = MeasurePackageUtilities(measure_types)

        def _run_package(selected: list[tuple[str, int]]) -> tuple["MeasurePackage", "pd.DataFrame"]:
            pkg = MeasurePackage()
            pkg.PackageID = {name: 0 for name in measure_types}
            for grp, idx in selected:
                pkg.PackageID[grp] = idx
            util.CreateRunDirectory(pkg, df_input.copy(), project_path)
            util.RunPackage(pkg, cost_metrics, df_weather)
            results = util.UpdatePackageResults(pkg, baseline_sum)
            return pkg, results

        # 3. Per-measure rows: run each selected measure on its own so the frontend can show
        #    its individual cost and energy savings against the baseline.
        measures_rows = []
        for grp, idx in selections:
            single_pkg, single_res = _run_package([(grp, idx)])
            option = measure_types[grp][idx]
            current = measure_types[grp][0]
            unit_value = (
                0.0 if (isinstance(option.UnitValue, str) and "autosize" in option.UnitValue)
                else float(option.UnitValue)
            )
            measures_rows.append({
                "Measure":             _ECM_MEASURE_GROUPS.get(grp, grp),
                "OrgPropValue":        current.PropValue,
                "NewPropValue":        option.PropValue,
                "InitFixedCost":       float(option.FixedCost),
                "InitVarCost":         float(option.UnitVarCost) * unit_value,
                "OrgTotalElectricity": org_kwh,
                "EEMTotalElectricity": float(single_res["Electricity"].iloc[0]),
                "OrgTotalNaturalGas":  org_therms,
                "EEMTotalNaturalGas":  float(single_res["NaturalGas"].iloc[0]),
            })

        # 4. Combined package: headline metrics + the monthly comparison the frontend plots.
        if selections:
            combined_pkg, combined_res = _run_package(selections)
            eem_kwh    = float(combined_res["Electricity"].iloc[0])
            eem_therms = float(combined_res["NaturalGas"].iloc[0])
            tic        = float(combined_res["TIC"].iloc[0])
            lcc        = float(combined_res["LCC"].iloc[0])
            comp_dir   = combined_pkg.OutputDir
            df_eem_monthly = pd.read_csv(os.path.join(comp_dir, "MonthlyEndUseBreakdown.csv"))
        else:
            # Nothing selected → no savings; compare baseline against itself for the plots.
            eem_kwh, eem_therms = org_kwh, org_therms
            tic, lcc = 0.0, org_lcc
            comp_dir = project_path
            df_eem_monthly = df_monthly.copy()

        plotter = PlotResults(True, project_path)
        plotter.PlotEEMEndUseComparison(comp_dir, df_eem_monthly)

        kwh_pct    = 100.0 * (org_kwh - eem_kwh) / org_kwh if org_kwh else 0.0
        therms_pct = 100.0 * (org_therms - eem_therms) / org_therms if org_therms else 0.0

        def _b64_ecm(name: str) -> "str | None":
            path = os.path.join(comp_dir, name)
            if not os.path.exists(path):
                return None
            with open(path, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

        return {
            "status": "success",
            "metrics": {
                "tic": round(tic, 2),
                "lcc": round(lcc, 2),
                "org_lcc": round(org_lcc, 2),
                "kwh_pct_savings": round(kwh_pct, 1),
                "therms_pct_savings": round(therms_pct, 1),
                "org_kwh": round(org_kwh, 1),
                "eem_kwh": round(eem_kwh, 1),
                "org_therms": round(org_therms, 1),
                "eem_therms": round(eem_therms, 1),
            },
            "plots": {
                "elec_monthly_comp": _b64_ecm("ElectricityMonthlyEEMComp.png"),
                "ng_monthly_comp":   _b64_ecm("NaturalGasMonthlyEEMComp.png"),
            },
            "measures": measures_rows,
            "skipped": skipped,
        }
    finally:
        _shutil.rmtree(project_path, ignore_errors=True)  # delete temp dir


@app.post("/run-ecm/{project_name}")
async def run_ecm(project_name: str, req: EcmRequest):
    loop = asyncio.get_event_loop()

    # Rebuild analysis cache if it was lost (e.g. server restart) using form_data
    if project_name not in _analysis_cache:
        if not req.form_data:
            raise HTTPException(status_code=400, detail="Baseline analysis not found. Please re-generate results first.")
        try:
            # Re-run analysis silently to repopulate the cache
            manual_req = ManualAnalysisRequest(form_data=req.form_data)
            await run_analysis_manual(project_name, manual_req)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to rebuild baseline analysis: {exc}")

    try:
        result = await loop.run_in_executor(_executor, _run_ecm_sync, project_name, req)
        return result
    except Exception as exc:
        import traceback
        raise HTTPException(status_code=500, detail=f"ECM evaluation failed: {exc}\n{traceback.format_exc()}")


# ── Export PKL ────────────────────────────────────────────────────────────────
class ExportPklRequest(BaseModel):
    form_data: dict


@app.post("/export-pkl/{project_name}")
async def export_pkl_handler(project_name: str, req: ExportPklRequest):
    """Generate a {project_name}-Baseline.pkl from frontend form data and return it for download."""
    from fastapi.responses import Response as FastAPIResponse

    REVERSE_MAP = {v: k for k, v in PROP_KEY_MAP.items()}
    REVERSE_LIST = {v: k for k, v in LIST_FIELDS.items()}

    rows = []
    fd = req.form_data

    for form_key, prop_key in REVERSE_MAP.items():
        value = fd.get(form_key, "")
        rows.append({"PropKey": prop_key, "PropValue": value if value != "" else None})

    for form_key, prop_key in REVERSE_LIST.items():
        value = fd.get(form_key, [])
        if isinstance(value, list):
            value = value[0] if value else ""
        rows.append({"PropKey": prop_key, "PropValue": value if value != "" else None})

    # Match real PKL projects, which always carry the CeilingConst constant the
    # CeilingInsulation ECM measure reads (the form doesn't collect it).
    if not any(r["PropKey"] == "CeilingConst" for r in rows):
        rows.append({"PropKey": "CeilingConst", "PropValue": _default_ceiling_const()})

    # Baseline EquipLoadRed is always 0% (see run_analysis_manual); never persist the
    # ECM field's "%"-suffixed value into the baseline PKL or it won't parse on reload.
    for _i, _r in enumerate(rows):
        if _r["PropKey"] == "EquipLoadRed":
            rows[_i] = {**_r, "PropValue": "0"}

    df = pd.DataFrame(rows, columns=["PropKey", "PropValue"])

    buf = io.BytesIO()
    df.to_pickle(buf)
    buf.seek(0)

    safe_name = project_name.replace(" ", "").replace("/", "").replace("..", "")
    return FastAPIResponse(
        content=buf.read(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}-Baseline.pkl"'},
    )


# ── Manual (form-based) analysis ──────────────────────────────────────────────
class ManualAnalysisRequest(BaseModel):
    form_data: dict


@app.post("/run-analysis-manual/{project_name}")
async def run_analysis_manual(project_name: str, req: ManualAnalysisRequest):
    """Build a DataFrame from form data in memory and run the analysis pipeline."""
    REVERSE_MAP = {v: k for k, v in PROP_KEY_MAP.items()}
    REVERSE_LIST = {v: k for k, v in LIST_FIELDS.items()}
    _EFF_FIELDS = {"heatingEff", "coolingEff", "heatingEffCustom", "coolingEffCustom"}

    rows = []
    fd = req.form_data

    for form_key, prop_key in REVERSE_MAP.items():
        value = fd.get(form_key, "")
        if form_key in _EFF_FIELDS and isinstance(value, str):
            value = _normalize_eff(value)
        rows.append({"PropKey": prop_key, "PropValue": value if value != "" else None})

    for form_key, prop_key in REVERSE_LIST.items():
        value = fd.get(form_key, [])
        if isinstance(value, list):
            value = value[0] if value else ""
        rows.append({"PropKey": prop_key, "PropValue": value if value != "" else None})

    # Apply defaults for keys required by EEMIndMeasureAnalysisObject.__init__
    _DEFAULTS = {
        "Shape":             "Rectangle",
        "x1":                "10", "x2": "0", "y1": "10", "y2": "0",
        "WallHeight":        "10",
        "WindowHeight":      "3",
        "FloorArea":         "1000",
        "FloorQty":          "1",
        "EPD":               "1.0",
    }
    for i, row in enumerate(rows):
        if row["PropKey"] in _DEFAULTS and row["PropValue"] in (None, ""):
            rows[i] = {**row, "PropValue": _DEFAULTS[row["PropKey"]]}

    # nHoursLighting is hours/day. PKL value is preserved via PROP_KEY_MAP;
    # inject 6 hrs/day only when absent or empty (pure manual entry without a PKL).
    _nh_rows = [r for r in rows if r["PropKey"] == "nHoursLighting"]
    if not _nh_rows or str(_nh_rows[0].get("PropValue", "")) in ("", "nan", "None"):
        rows = [r for r in rows if r["PropKey"] != "nHoursLighting"]
        rows.append({"PropKey": "nHoursLighting", "PropValue": "6"})

    # CeilingConst isn't a form field; PKL projects store it as a constant. Inject it
    # when absent so the CeilingInsulation ECM measure can read it (see
    # _default_ceiling_const) instead of crashing on an empty .iloc[0].
    if not any(r["PropKey"] == "CeilingConst" for r in rows):
        rows.append({"PropKey": "CeilingConst", "PropValue": _default_ceiling_const()})

    # "Reduce Equipment Load" is an ECM-only measure; a building's CURRENT equipment-load
    # reduction is always 0% (the frontend enforces "baseline is always 0%"). But
    # PROP_KEY_MAP maps the baseline prop EquipLoadRed to the ECM field, so the ECM
    # selection (e.g. "10%") would otherwise land in the baseline prop and crash
    # EnergyAnalysis' `.astype(float)` on the trailing "%". Pin the baseline to a plain
    # "0"; the ECM run sets its own value when that measure is evaluated.
    for _i, _r in enumerate(rows):
        if _r["PropKey"] == "EquipLoadRed":
            rows[_i] = {**_r, "PropValue": "0"}

    # Build the combined WWR dict row expected by EEMIndMeasureAnalysisObject
    def _get_row(key: str):
        for r in rows:
            if r["PropKey"] == key:
                v = r["PropValue"]
                return float(v) if v not in (None, "") else 0.0
        return 0.0

    rows.append({
        "PropKey": "WWR",
        "PropValue": {
            "Front": _get_row("WWR_Front"),
            "Left":  _get_row("WWR_Left"),
            "Back":  _get_row("WWR_Back"),
            "Right": _get_row("WWR_Right"),
        },
    })

    df = pd.DataFrame(rows, columns=["PropKey", "PropValue"])

    # Strip only characters that could cause path traversal; preserve spaces so the
    # name matches the utility CSV filename on disk.
    safe_name = project_name.replace("..", "").replace("/", "").replace("\\", "").strip()
    if not safe_name:
        raise HTTPException(status_code=400, detail="Project name is required.")

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(_executor, _run_analysis_sync, safe_name, df)
        result["project_name"] = safe_name
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


# ── List available projects ───────────────────────────────────────────────────
@app.get("/list-projects")
async def list_projects():
    """Return all project folders that have a pkl file and a utility CSV."""
    if not os.path.exists(PROJECTS_DIR):
        return {"projects": []}
    projects = []
    for folder in sorted(os.listdir(PROJECTS_DIR)):
        folder_path = os.path.join(PROJECTS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        has_pkl = bool(glob_module.glob(os.path.join(folder_path, "*-Baseline.pkl")))
        has_util = os.path.exists(os.path.join(folder_path, f"{folder}_UtilityData.csv"))
        if has_pkl and has_util:
            projects.append(folder)
    return {"projects": projects}


# ── Load project from server folder ──────────────────────────────────────────
@app.post("/load-project/{project_name}")
async def load_project(project_name: str):
    """Read the pkl from an existing project folder and return form fields."""
    project_path = os.path.join(PROJECTS_DIR, project_name)
    pkl_candidates = glob_module.glob(os.path.join(project_path, "*-Baseline.pkl"))
    if not pkl_candidates:
        raise HTTPException(status_code=404, detail=f"No pkl file found in project '{project_name}'.")

    df = pd.read_pickle(pkl_candidates[0])
    _pkl_df_cache[project_name] = df

    fields: dict[str, object] = {}
    for prop_key, form_key in PROP_KEY_MAP.items():
        fields[form_key] = _val(df, prop_key)
    for prop_key, form_key in LIST_FIELDS.items():
        raw = _val(df, prop_key)
        fields[form_key] = [raw] if raw else []

    populated_keys = [k for k, v in fields.items() if v]
    return {
        "fields": fields,
        "count": len(populated_keys),
        "populated_keys": populated_keys,
        "project_name": project_name,
    }


# ── Serve result plots ─────────────────────────────────────────────────────────
@app.get("/results/{project_name}/plot/{filename:path}")
async def get_plot(project_name: str, filename: str):
    # Prevent directory traversal
    safe_name = os.path.basename(filename)
    plot_path = os.path.join(PROJECTS_DIR, project_name, safe_name)
    if not os.path.exists(plot_path):
        raise HTTPException(status_code=404, detail=f"Plot '{safe_name}' not found.")
    return FileResponse(plot_path, media_type="image/png")

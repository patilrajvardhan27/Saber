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

# ── InverseModel safety patches ────────────────────────────────────────────────
# Bug 1: model.py fit() swallows curve_fit failures but leaves self.p unset;
#        fit_model() then crashes with AttributeError at `self.p_init = self.p`.
# Bug 2: fit_model() returns bare False (not a tuple) when R² < threshold, but
#        BuildTemperatureBasedModel always unpacks 3 values from the result.
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

    def _safe_inv_fit_model(self, has_fit=False, threshold=0.1):
        try:
            result = _orig_inv_fit_model(self, has_fit, threshold)
            if not isinstance(result, tuple):
                return (False, "No fit", getattr(self, 'p', _np_patch.zeros(5)))
            return result
        except Exception:
            return (False, "No fit", getattr(self, 'p', _np_patch.zeros(5)))

    _InverseModel.fit_model = _safe_inv_fit_model
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
    "EquipPowerDensity":  "epd",
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
        GetMonthlyEndUseBreakdown,
    )
    from BldgAuditToolPackage.PostProcessing import PlotResults

    if df_input is None:
        raise ValueError("No building data provided — please upload a PKL file first.")

    bldg_location = _val(df_input, "Location")
    if not bldg_location:
        raise ValueError("Building location is missing from the PKL file.")

    # All file I/O happens inside a temp directory that is deleted when done
    tmp = tempfile.mkdtemp()
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

        # CostData: symlink or copy from an existing project (needed by EvaluateMeasure)
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
        best_model = cpm.ChooseBestModel(dd_results, model_params_heating, model_params_cooling)

        # 3. Monthly end-use breakdown
        df_monthly = GetMonthlyEndUseBreakdown(best_model, df_weather, df_input, False)

        # 4. Generate plots into tmp
        plotter = PlotResults(True, tmp)
        plotter.PlotWeather(df_weather, weather_station_name)
        plotter.PlotEndUseBreakdown(df_monthly.clip(lower=0))
        if has_utility_data:
            plotter.PlotInverseModelComparison(df_monthly, dfutil_sorted)

        # 5. Encode each PNG as base64 (files stay in tmp and are deleted below)
        def _b64(name: str) -> str | None:
            path = os.path.join(tmp, name)
            if not os.path.exists(path):
                return None
            with open(path, "rb") as f:
                return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

        all_pngs = [os.path.basename(p) for p in glob_module.glob(os.path.join(tmp, "*.png"))]
        weather_plot = f"WeatherPlot_{weather_station_name}.png"
        elec_temp = next((f for f in all_pngs if f.startswith("Electricity_") and f.endswith("_TempBasedChngPtModel.png")), None)
        ff_temp   = next((f for f in all_pngs if f.startswith("Fossil Fuel_")  and f.endswith("_TempBasedChngPtModel.png")), None)
        elec_dd   = next((f for f in ["Electricity_Cooling_DDBasedChngPtModel.png", "Electricity_Heating_DDBasedChngPtModel.png"]
                          if os.path.exists(os.path.join(tmp, f))), None)

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

        # 6. Cache in-memory results for ECM evaluation
        # Use "EL-" / "NG-" to match only end-use columns (e.g. "EL-Space Cooling"),
        # not BLC coefficients ("BLC_Heat_EL") or degree-day columns ("HDD_EL").
        best_model["OrgTotalElectricity"] = df_monthly.loc[:, df_monthly.columns.str.contains("EL-")].sum().sum() / 3.412
        best_model["OrgTotalNaturalGas"]  = df_monthly.loc[:, df_monthly.columns.str.contains("NG-")].sum().sum() / 100
        best_model["BLC_Heat_EL"] = float(df_monthly["BLC_Heat_EL"].mean())
        best_model["BLC_Heat_NG"] = float(df_monthly["BLC_Heat_NG"].mean())
        best_model["BLC_Cool_EL"] = float(df_monthly["BLC_Cool_EL"].mean())

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


def _run_ecm_sync(project_name: str, req: EcmRequest) -> dict:
    from BldgAuditToolPackage.EEMIndMeasureAnalysisObject import EvaluateMeasure
    from BldgAuditToolPackage.PostProcessing import PlotResults
    import copy

    if project_name not in _analysis_cache:
        raise RuntimeError("Baseline analysis not found — please upload the PKL file first.")

    cache = _analysis_cache[project_name]
    df_weather = cache["df_weather"]
    df_input_org = cache["df_input"]
    df_monthly_org = cache["df_monthly"]
    best_model_orig = cache["best_model"]

    # ECM evaluation uses a temp directory — nothing saved locally
    import tempfile, shutil as _shutil
    tmp_ecm = tempfile.mkdtemp()
    cost_sources = glob_module.glob(os.path.join(PROJECTS_DIR, "*", "CostData"))
    if cost_sources:
        _shutil.copytree(cost_sources[0], os.path.join(tmp_ecm, "CostData"))
    project_path = tmp_ecm

    # Ensure geometry fields required by EvaluateMeasure.__init__ are present and valid
    def _patch_df(df: "pd.DataFrame") -> "pd.DataFrame":
        df = df.copy()
        _GEO_DEFAULTS = {
            "Shape":       "Rectangle",
            "x1": "10", "x2": "0", "y1": "10", "y2": "0",
            "WallHeight":  "10",
            "WindowHeight": "3",
            "FloorArea":   "1000",
            "FloorQty":    "1",
        }
        for prop_key, default in _GEO_DEFAULTS.items():
            mask = df["PropKey"] == prop_key
            if not mask.any():
                df = pd.concat([df, pd.DataFrame([{"PropKey": prop_key, "PropValue": default}])], ignore_index=True)
            elif df.loc[mask, "PropValue"].iloc[0] in (None, ""):
                df.loc[mask, "PropValue"] = default
        # Force Shape to Rectangle (package only supports Rectangle for ECM)
        df.loc[df["PropKey"] == "Shape", "PropValue"] = "Rectangle"
        # nHoursLighting is hours/day (not hours/year). PKL stores the correct value;
        # inject 6 hrs/day as a fallback only when the key is absent or empty.
        _nh = df.loc[df["PropKey"] == "nHoursLighting", "PropValue"]
        if _nh.empty or str(_nh.iloc[0]) in ("", "nan", "None"):
            df = df[df["PropKey"] != "nHoursLighting"]
            df = pd.concat([df, pd.DataFrame([{"PropKey": "nHoursLighting", "PropValue": "6"}])], ignore_index=True)
        # CeilingConst not in the form — inject the only value that exists in Construction-Floor.csv
        if not (df["PropKey"] == "CeilingConst").any():
            df = pd.concat([df, pd.DataFrame([{"PropKey": "CeilingConst", "PropValue": "Floor construction Reversed"}])], ignore_index=True)
        # Ensure WWR dict row exists
        if not (df["PropKey"] == "WWR").any():
            def _gv(key):
                rows = df.loc[df["PropKey"] == key, "PropValue"]
                v = rows.iloc[0] if not rows.empty else None
                try: return float(v) if v not in (None, "") else 0.0
                except: return 0.0
            df = pd.concat([df, pd.DataFrame([{"PropKey": "WWR", "PropValue": {
                "Front": _gv("WWR_Front"), "Left": _gv("WWR_Left"),
                "Back":  _gv("WWR_Back"),  "Right": _gv("WWR_Right"),
            }}])], ignore_index=True)
        return df

    df_input_org = _patch_df(df_input_org)

    # Build df_input_EEM: copy with ECM values substituted
    df_input_eem = df_input_org.copy()

    def _set_prop(key: str, val: str) -> None:
        mask = df_input_eem["PropKey"] == key
        if mask.any():
            df_input_eem.loc[mask, "PropValue"] = val

    if req.ecm_wall_insulation:
        _set_prop("R-WallInsulation", req.ecm_wall_insulation)
    if req.ecm_infiltration:
        _set_prop("ACH50", req.ecm_infiltration)
    if req.ecm_ceiling_insulation:
        _set_prop("R-CeilingInsulation", req.ecm_ceiling_insulation)
    if req.ecm_window_material:
        _set_prop("WindowMaterial", req.ecm_window_material)
    if req.ecm_daylighting == "Yes":
        _set_prop("Daylighting", "Yes")
    if req.ecm_economizer == "Yes":
        _set_prop("Economizer", "Yes")
    if req.ecm_occupancy_sensor == "Yes":
        _set_prop("OccupancySensor", "Yes")
    if req.ecm_led:
        _set_prop("LEDECM", req.ecm_led)

    # Deep-copy best_model so cache stays clean
    best_model = copy.deepcopy(best_model_orig)

    eval_measure = EvaluateMeasure(df_input_eem, df_weather, BLDG_AUDIT_DIR, project_path, best_model)

    dfMeasure = pd.DataFrame()
    df_eem_last = df_monthly_org.copy()

    def _run_measure(fn, *args):
        nonlocal df_eem_last
        df_eem, results = fn(*args)
        df_eem_last = df_eem
        return results

    # Run selected measures
    if req.ecm_wall_insulation:
        ext_wall = _val(df_input_org, "ExtWallConst")
        wall_org = _val(df_input_org, "R-WallInsulation") or "Uninsulated"
        if not ext_wall:
            raise RuntimeError("Wall Construction Type is required to evaluate the Wall Insulation ECM — please set it in the Envelope step.")
        r = _run_measure(eval_measure.WallInsulation, ext_wall, wall_org, req.ecm_wall_insulation)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_infiltration:
        ach_org = float(_val(df_input_org, "ACH50") or 0)
        ach_eem = float(req.ecm_infiltration)
        r = _run_measure(eval_measure.Infiltration, ach_org, ach_eem)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_ceiling_insulation:
        ext_roof = _val(df_input_org, "ExtRoofConst") or "Asphalt Shingles"
        ceil_const_rows = df_input_org.loc[df_input_org["PropKey"] == "CeilingConst", "PropValue"]
        ceil_const = str(ceil_const_rows.iloc[0]) if not ceil_const_rows.empty else "Floor construction Reversed"
        ceil_org = _val(df_input_org, "R-CeilingInsulation") or "Uninsulated"
        r = _run_measure(eval_measure.CeilingInsulation, ext_roof, ceil_const, ceil_org, req.ecm_ceiling_insulation)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_window_material:
        win_org = _WIN_MAT_MAP.get(_val(df_input_org, "WindowMaterial"), _val(df_input_org, "WindowMaterial"))
        win_eem = _WIN_MAT_MAP.get(req.ecm_window_material, req.ecm_window_material)
        try:
            r = _run_measure(eval_measure.WindowMaterial, win_org, win_eem)
            dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)
        except (IndexError, KeyError) as exc:
            raise RuntimeError(
                f"Window material '{win_eem}' was not found in the cost database. "
                f"Verify that the selected ECM window material matches an available option."
            ) from exc

    if req.ecm_occupancy_sensor == "Yes":
        r = _run_measure(eval_measure.OccupancySensor)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_led:
        led_org = float(_val(df_input_org, "LEDCurrent") or 0)
        led_eem = float(req.ecm_led)
        r = _run_measure(eval_measure.ReplaceLighting, led_org, led_eem)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_daylighting == "Yes":
        r = _run_measure(eval_measure.DaylightingSensor)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_economizer == "Yes":
        bldg_address = _val(df_input_org, "Location")
        r = _run_measure(eval_measure.Economizer, bldg_address)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_cooling_eff:
        cooling_eqp_raw = _val(df_input_org, "CoolingEquipment")
        cooling_eqp_csv = cooling_eqp_raw.replace(" ", "")  # "Air Conditioner" → "AirConditioner"
        cooling_eff_org_str = _normalize_eff(_val(df_input_org, "CoolingEff") or "1")
        cooling_eff_eem_str = _normalize_eff(req.ecm_cooling_eff)
        try:
            cooling_eff_org = float(cooling_eff_org_str or "1")
            cooling_eff_eem = float(cooling_eff_eem_str)
            if cooling_eqp_csv and cooling_eff_eem and cooling_eqp_csv not in ("NoCooling",):
                r = _run_measure(eval_measure.CoolingEff, cooling_eqp_csv, cooling_eff_org, cooling_eff_eem)
                dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)
        except Exception:
            pass  # skip if equipment/efficiency data not available

    if req.ecm_heating_eff:
        heating_eqp_raw = _val(df_input_org, "HeatingEquipment")
        heating_eqp_csv = heating_eqp_raw.replace(" ", "")  # "Gas Furnace" → "GasFurnace"
        heating_eff_org_str = _normalize_eff(_val(df_input_org, "HeatingEff") or "1")
        heating_eff_eem_str = _normalize_eff(req.ecm_heating_eff)
        try:
            heating_eff_org = float(heating_eff_org_str or "1")
            heating_eff_eem = float(heating_eff_eem_str)
            if heating_eqp_csv and heating_eff_eem and heating_eqp_csv not in ("NoHeating",):
                r = _run_measure(eval_measure.HeatingEff, heating_eqp_csv, heating_eff_org, heating_eff_eem)
                dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)
        except Exception:
            pass  # skip if equipment/efficiency data not available

    # Generate comparison plots (use baseline for both when no measures selected)
    plotter = PlotResults(True, project_path)
    plotter.PlotEEMEndUseComparison(df_monthly_org, df_eem_last)

    # Compute package metrics
    tic = float(dfMeasure["InitFixedCost"].sum() + dfMeasure["InitVarCost"].sum()) if not dfMeasure.empty else 0.0
    org_kwh = float(best_model_orig["OrgTotalElectricity"])
    org_therms = float(best_model_orig["OrgTotalNaturalGas"])
    eem_kwh = float(df_eem_last.loc[:, df_eem_last.columns.str.contains("EL-")].sum().sum() / 3.412)
    eem_therms = float(df_eem_last.loc[:, df_eem_last.columns.str.contains("NG-")].sum().sum() / 100)

    r_discount = req.discount_rate / 100.0
    uspw = (1 - (1 + r_discount) ** (-req.lifetime)) / r_discount if r_discount != 0 else req.lifetime
    aoc_org = req.kwh_rate * org_kwh + req.therm_rate * org_therms
    aoc_eem = req.kwh_rate * eem_kwh + req.therm_rate * eem_therms
    org_lcc = uspw * aoc_org
    lcc = tic + uspw * aoc_eem

    kwh_pct = 100.0 * (org_kwh - eem_kwh) / org_kwh if org_kwh else 0.0
    therms_pct = 100.0 * (org_therms - eem_therms) / org_therms if org_therms else 0.0

    import base64

    def _b64_ecm(name: str) -> str | None:
        path = os.path.join(tmp_ecm, name)
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

    try:
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
            "measures": dfMeasure.to_dict(orient="records"),
        }
    finally:
        _shutil.rmtree(tmp_ecm, ignore_errors=True)  # delete temp dir


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
        "EquipPowerDensity": "1.0",
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

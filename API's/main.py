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
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLDG_AUDIT_DIR = os.path.normpath(os.path.join(BASE_DIR, "../BldgAuditToolSimple_v1"))
PROJECTS_DIR = os.path.join(BLDG_AUDIT_DIR, "Projects")
sys.path.insert(0, BLDG_AUDIT_DIR)

_executor = ThreadPoolExecutor(max_workers=2)

# ── In-memory cache for baseline analysis results (keyed by project_name) ──────
_analysis_cache: dict[str, dict] = {}

# ── PKL field mapping ──────────────────────────────────────────────────────────
PROP_KEY_MAP: dict[str, str] = {
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
    "DryerRating":        "dryerRating",
    "WasherRating":       "washerRating",
    "CookingFuelType":    "cookingFuelType",
    "CookingRangeRating": "cookingRating",
    "DishwasherRating":   "dishWasherRating",
    "FridgeRating":       "fridgeRating",
    "MiscPlugLoadRating": "miscPlugLoadRating",
    "MiscTVRating":       "tvRating",
    "nHoursLighting":     "nHoursLighting",
    "LPD":                "lpd",
    "OfficeEqpRating":    "officeEqpRating",
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
}

LIST_FIELDS: dict[str, str] = {
    "Orientation":    "orientation",
    "WindowMaterial": "windowMaterial",
}


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

    # Find the correct project folder:
    # 1. Search existing project subdirectories for one already containing this pkl filename
    # 2. Fall back to deriving project name from the pkl filename itself
    project_name: str | None = None
    if os.path.exists(PROJECTS_DIR):
        for folder in os.listdir(PROJECTS_DIR):
            folder_path = os.path.join(PROJECTS_DIR, folder)
            if os.path.isdir(folder_path) and os.path.exists(os.path.join(folder_path, file.filename)):
                project_name = folder
                break

    if project_name is None:
        project_name = file.filename[: -len("-Baseline.pkl")]

    project_path = os.path.join(PROJECTS_DIR, project_name)
    os.makedirs(project_path, exist_ok=True)
    with open(os.path.join(project_path, file.filename), "wb") as fout:
        fout.write(contents)

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


# ── Utility CSV upload ─────────────────────────────────────────────────────────
@app.post("/upload-utility/{project_name}")
async def upload_utility(project_name: str, file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    contents = await file.read()
    project_path = os.path.join(PROJECTS_DIR, project_name)
    os.makedirs(project_path, exist_ok=True)

    # Always save as {ProjectName}_UtilityData.csv (what the analysis engine expects)
    save_path = os.path.join(project_path, f"{project_name}_UtilityData.csv")
    with open(save_path, "wb") as fout:
        fout.write(contents)

    return {"status": "ok", "saved_as": f"{project_name}_UtilityData.csv"}


# ── Run analysis ───────────────────────────────────────────────────────────────
def _run_analysis_sync(project_name: str) -> dict:
    """Runs the full BldgAuditTool analysis pipeline. Called in a thread pool."""
    from BldgAuditToolPackage.AnalyzeUtilityData import (
        GetWeather,
        BuildChangePointModel,
        GetMonthlyEndUseBreakdown,
    )
    from BldgAuditToolPackage.PostProcessing import PlotResults

    project_path = os.path.join(PROJECTS_DIR, project_name)
    pkl_candidates = glob_module.glob(os.path.join(project_path, "*-Baseline.pkl"))
    if not pkl_candidates:
        raise FileNotFoundError(f"No *-Baseline.pkl found in {project_path}")
    pkl_path = pkl_candidates[0]

    util_path = os.path.join(project_path, f"{project_name}_UtilityData.csv")
    if not os.path.exists(util_path):
        raise FileNotFoundError(f"Utility CSV not found: {util_path}")

    df_input = pd.read_pickle(pkl_path)
    bldg_location = _val(df_input, "Location")
    if not bldg_location:
        raise ValueError("Building location is missing from the PKL file.")

    # 1. Download weather data
    df_weather, weather_station_name = GetWeather(project_path, project_name, bldg_location)

    # 2. Build change-point models
    cpm = BuildChangePointModel(project_path, project_name, df_input, df_weather)
    (
        model_type_cooling,
        model_params_cooling,
        model_type_heating,
        model_params_heating,
    ) = cpm.BuildTemperatureBasedModel()
    dd_results, dfutil_sorted = cpm.BuildDegreeDayBasedModel(
        model_type_cooling, model_params_cooling, model_type_heating, model_params_heating
    )
    best_model = cpm.ChooseBestModel(dd_results, model_params_heating, model_params_cooling)

    # 3. Monthly end-use breakdown
    df_monthly = GetMonthlyEndUseBreakdown(best_model, df_weather, df_input, False)

    # 4. Generate and save all plots
    plotter = PlotResults(True, project_path)
    plotter.PlotWeather(df_weather, weather_station_name)
    plotter.PlotEndUseBreakdown(df_monthly)
    plotter.PlotInverseModelComparison(df_monthly, dfutil_sorted)

    # 5. Collect generated plot filenames
    all_pngs = [os.path.basename(p) for p in glob_module.glob(os.path.join(project_path, "*.png"))]

    def _exists(name: str) -> str | None:
        return name if os.path.exists(os.path.join(project_path, name)) else None

    weather_plot = f"WeatherPlot_{weather_station_name}.png"
    elec_temp = next(
        (f for f in all_pngs if f.startswith("Electricity_") and f.endswith("_TempBasedChngPtModel.png")),
        None,
    )
    ff_temp = next(
        (f for f in all_pngs if f.startswith("Fossil Fuel_") and f.endswith("_TempBasedChngPtModel.png")),
        None,
    )
    elec_dd = next(
        (
            _exists(name)
            for name in [
                "Electricity_Cooling_DDBasedChngPtModel.png",
                "Electricity_Heating_DDBasedChngPtModel.png",
            ]
            if _exists(name)
        ),
        None,
    )

    plots = {
        "weather": _exists(weather_plot),
        "elec_temp_model": elec_temp,
        "ff_temp_model": ff_temp,
        "ff_dd_model": _exists("FossilFuel_Heating_DDBasedChngPtModel.png"),
        "elec_dd_model": elec_dd,
        "end_use": _exists("EndUseBreakdown.png"),
        "ng_monthly": _exists("NaturalGasMonthlyBreakdown.png"),
        "elec_monthly": _exists("ElectricityMonthlyBreakdown.png"),
    }

    # 6. Augment best_model with totals needed by EvaluateMeasure and cache everything
    best_model["OrgTotalElectricity"] = (
        df_monthly.loc[:, df_monthly.columns.str.contains("EL")].sum().sum() / 3.41
    )
    best_model["OrgTotalNaturalGas"] = (
        df_monthly.loc[:, df_monthly.columns.str.contains("NG")].sum().sum() / 100
    )
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

    return {"status": "success", "plots": plots}


@app.post("/run-analysis/{project_name}")
async def run_analysis(project_name: str):
    project_path = os.path.join(PROJECTS_DIR, project_name)
    pkl_candidates = glob_module.glob(os.path.join(project_path, "*-Baseline.pkl"))
    if not pkl_candidates:
        raise HTTPException(status_code=404, detail=f"PKL file not found for project '{project_name}'.")
    if not os.path.exists(os.path.join(project_path, f"{project_name}_UtilityData.csv")):
        raise HTTPException(status_code=404, detail=f"Utility data CSV not found for project '{project_name}'.")

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(_executor, _run_analysis_sync, project_name)
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
    kwh_rate: float = 0.12
    therm_rate: float = 1.20
    discount_rate: float = 3.0
    lifetime: int = 20


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

    project_path = os.path.join(PROJECTS_DIR, project_name)

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
        wall_org = _val(df_input_org, "R-WallInsulation")
        r = _run_measure(eval_measure.WallInsulation, ext_wall, wall_org, req.ecm_wall_insulation)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_infiltration:
        ach_org = float(_val(df_input_org, "ACH50") or 0)
        ach_eem = float(req.ecm_infiltration)
        r = _run_measure(eval_measure.Infiltration, ach_org, ach_eem)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_ceiling_insulation:
        ext_roof = _val(df_input_org, "ExtRoofConst")
        ceil_const_rows = df_input_org.loc[df_input_org["PropKey"] == "CeilingConst", "PropValue"]
        ceil_const = str(ceil_const_rows.iloc[0]) if not ceil_const_rows.empty else "Wood Joist 10in."
        ceil_org = _val(df_input_org, "R-CeilingInsulation")
        r = _run_measure(eval_measure.CeilingInsulation, ext_roof, ceil_const, ceil_org, req.ecm_ceiling_insulation)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

    if req.ecm_window_material:
        win_org = _val(df_input_org, "WindowMaterial")
        r = _run_measure(eval_measure.WindowMaterial, win_org, req.ecm_window_material)
        dfMeasure = pd.concat([dfMeasure, pd.DataFrame([r])], ignore_index=True)

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

    if dfMeasure.empty:
        return {"status": "no_measures", "metrics": {}, "plots": {}}

    # Generate comparison plots
    plotter = PlotResults(True, project_path)
    plotter.PlotEEMEndUseComparison(df_monthly_org, df_eem_last)

    # Compute package metrics
    tic = float(dfMeasure["InitFixedCost"].sum() + dfMeasure["InitVarCost"].sum())
    org_kwh = float(best_model_orig["OrgTotalElectricity"])
    org_therms = float(best_model_orig["OrgTotalNaturalGas"])
    eem_kwh = float(df_eem_last.loc[:, df_eem_last.columns.str.contains("EL-")].sum().sum() / 3.41)
    eem_therms = float(df_eem_last.loc[:, df_eem_last.columns.str.contains("NG-")].sum().sum() / 100)

    r_discount = req.discount_rate / 100.0
    uspw = (1 - (1 + r_discount) ** (-req.lifetime)) / r_discount if r_discount != 0 else req.lifetime
    aoc_eem = req.kwh_rate * eem_kwh + req.therm_rate * eem_therms
    lcc = tic + uspw * aoc_eem

    kwh_pct = 100.0 * (org_kwh - eem_kwh) / org_kwh if org_kwh else 0.0
    therms_pct = 100.0 * (org_therms - eem_therms) / org_therms if org_therms else 0.0

    def _exists(name: str) -> str | None:
        return name if os.path.exists(os.path.join(project_path, name)) else None

    return {
        "status": "success",
        "metrics": {
            "tic": round(tic, 2),
            "lcc": round(lcc, 2),
            "kwh_pct_savings": round(kwh_pct, 1),
            "therms_pct_savings": round(therms_pct, 1),
            "org_kwh": round(org_kwh, 1),
            "eem_kwh": round(eem_kwh, 1),
            "org_therms": round(org_therms, 1),
            "eem_therms": round(eem_therms, 1),
        },
        "plots": {
            "elec_monthly_comp": _exists("ElectricityMonthlyEEMComp.png"),
            "ng_monthly_comp": _exists("NaturalGasMonthlyEEMComp.png"),
        },
        "measures": dfMeasure.to_dict(orient="records"),
    }


@app.post("/run-ecm/{project_name}")
async def run_ecm(project_name: str, req: EcmRequest):
    if project_name not in _analysis_cache:
        raise HTTPException(status_code=400, detail="Baseline analysis not found. Upload PKL and wait for analysis to complete.")

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(_executor, _run_ecm_sync, project_name, req)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ECM evaluation failed: {exc}")


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


# ── Serve result plots ─────────────────────────────────────────────────────────
@app.get("/results/{project_name}/plot/{filename:path}")
async def get_plot(project_name: str, filename: str):
    # Prevent directory traversal
    safe_name = os.path.basename(filename)
    plot_path = os.path.join(PROJECTS_DIR, project_name, safe_name)
    if not os.path.exists(plot_path):
        raise HTTPException(status_code=404, detail=f"Plot '{safe_name}' not found.")
    return FileResponse(plot_path, media_type="image/png")

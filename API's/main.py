"""
Saber BldgAuditTool – FastAPI backend
Run: uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io

app = FastAPI(title="Saber BldgAuditTool API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mapping: PropKey in the pkl DataFrame  →  FormState field name in the frontend
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
}

# Fields that hold a single string value but map to a list in the frontend
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


@app.post("/upload-pkl")
async def upload_pkl(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pkl"):
        raise HTTPException(status_code=400, detail="Only .pkl files are accepted.")

    contents = await file.read()
    try:
        df = pd.read_pickle(io.BytesIO(contents))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse file: {exc}")

    if not isinstance(df, pd.DataFrame) or "PropKey" not in df.columns:
        raise HTTPException(status_code=422, detail="File does not contain expected PropKey/PropValue structure.")

    fields: dict[str, object] = {}

    for prop_key, form_key in PROP_KEY_MAP.items():
        fields[form_key] = _val(df, prop_key)

    for prop_key, form_key in LIST_FIELDS.items():
        raw = _val(df, prop_key)
        fields[form_key] = [raw] if raw else []

    return {"fields": fields, "count": len([v for v in fields.values() if v])}

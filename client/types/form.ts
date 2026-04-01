export interface FormState {
  // ── Preferences ──────────────────────────────────────────
  projectName: string;
  buildingType: string;
  location: string;
  inputMethod: "new" | "existing";
  bldgPropInputFile: string;
  utilDataSource: "enter" | "existing";
  utilDataSourceFile: string;

  // ── Orientation & Geometry ────────────────────────────────
  shapeType: string;
  orientation: string[];
  floorArea: string;
  flrQty: string;
  wallHt: string;
  x1: string;
  x2: string;
  y1: string;
  y2: string;

  // ── Envelope: Walls ───────────────────────────────────────
  extWallConst: string;
  wallInsulation: string;

  // ── Envelope: Roof ────────────────────────────────────────
  extRoofConst: string;
  ceilingInsulation: string;

  // ── Envelope: Foundation ──────────────────────────────────
  foundation: string;
  slabInsulation: string;

  // ── Envelope: Infiltration ────────────────────────────────
  ach50: string;

  // ── Envelope: Windows ─────────────────────────────────────
  windowMaterial: string[];
  wwrFront: string;
  wwrLeft: string;
  wwrBack: string;
  wwrRight: string;

  // ── Envelope: Shading ─────────────────────────────────────
  overhang: string;
  windowHt: string;
  nWindow: string;

  // ── HVAC: Cooling ─────────────────────────────────────────
  coolingEqp: string;
  coolingEff: string;
  coolingEffCustom: string;
  tspc: string;

  // ── HVAC: Heating ─────────────────────────────────────────
  heatingEqp: string;
  heatingEff: string;
  heatingEffCustom: string;
  tsph: string;
  nightSetback: string;
  nNightSetbackHours: string;

  // ── HVAC: Hot Water ───────────────────────────────────────
  dhwSystemType: string;
  dhwTankVol: string;

  // ── HVAC: Other ───────────────────────────────────────────
  economizer: string;
  swampCooler: string;

  // ── Equipment & Lighting ──────────────────────────────────
  cookingFuelType: string;
  cookingRating: string;
  fridgeRating: string;
  dishWasherRating: string;
  washerRating: string;
  dryerRating: string;
  tvRating: string;
  officeEqpRating: string;
  miscPlugLoadRating: string;
  lpd: string;
  daylighting: string;
  nHoursLighting: string;
  led: string;

  // ── Cost & Financial ──────────────────────────────────────
  thermCost: string;
  kWhCost: string;
  discountRate: string;
  lifetime: string;

  // ── ECM Selections ────────────────────────────────────────
  ecmWallInsulation: string;
  ecmInfiltration: string;
  ecmCeilingInsulation: string;
  ecmWindowMaterial: string;
  ecmNightSetback: string;
  ecmNightSetbackHours: string;
  ecmDaylighting: string;
  ecmEconomizer: string;
  ecmOccupancySensor: string;
  ecmLED: string;
  ecmReduceEquipLoad: string;
  ecmCoolingEff: string;
  ecmHeatingEqp: string;
  ecmHeatingEff: string;

  // ── Output / Results ──────────────────────────────────────
  packageLCC: string;
  packageTIC: string;
  packageKWhPctChange: string;
  packageThermsPctChange: string;
}

export const initialFormState: FormState = {
  projectName: "",
  buildingType: "",
  location: "",
  inputMethod: "new",
  bldgPropInputFile: "",
  utilDataSource: "enter",
  utilDataSourceFile: "",

  shapeType: "Rectangle",
  orientation: [],
  floorArea: "",
  flrQty: "",
  wallHt: "",
  x1: "",
  x2: "",
  y1: "",
  y2: "",

  extWallConst: "",
  wallInsulation: "",
  extRoofConst: "Asphalt Shingles",
  ceilingInsulation: "",
  foundation: "",
  slabInsulation: "Uninsulated",
  ach50: "",
  windowMaterial: [],
  wwrFront: "",
  wwrLeft: "",
  wwrBack: "",
  wwrRight: "",
  overhang: "",
  windowHt: "",
  nWindow: "",

  coolingEqp: "",
  coolingEff: "",
  coolingEffCustom: "",
  tspc: "",

  heatingEqp: "",
  heatingEff: "",
  heatingEffCustom: "",
  tsph: "",
  nightSetback: "0.0",
  nNightSetbackHours: "",

  dhwSystemType: "",
  dhwTankVol: "",
  economizer: "No",
  swampCooler: "No",

  cookingFuelType: "",
  cookingRating: "",
  fridgeRating: "",
  dishWasherRating: "",
  washerRating: "",
  dryerRating: "",
  tvRating: "",
  officeEqpRating: "",
  miscPlugLoadRating: "",
  lpd: "",
  daylighting: "No",
  nHoursLighting: "",
  led: "0.0",

  thermCost: "",
  kWhCost: "",
  discountRate: "",
  lifetime: "",

  ecmWallInsulation: "",
  ecmInfiltration: "",
  ecmCeilingInsulation: "",
  ecmWindowMaterial: "",
  ecmNightSetback: "",
  ecmNightSetbackHours: "",
  ecmDaylighting: "",
  ecmEconomizer: "",
  ecmOccupancySensor: "",
  ecmLED: "",
  ecmReduceEquipLoad: "",
  ecmCoolingEff: "",
  ecmHeatingEqp: "",
  ecmHeatingEff: "",

  packageLCC: "",
  packageTIC: "",
  packageKWhPctChange: "",
  packageThermsPctChange: "",
};

export type FormField = keyof FormState;

export interface SectionConfig {
  id: number;
  label: string;
  shortLabel: string;
  firstStep: number;
  lastStep: number;
}

export interface SubStepConfig {
  id: number;
  section: number;
  label: string;
}

export const SECTIONS: SectionConfig[] = [
  { id: 1, label: "Project Info",         shortLabel: "Info",      firstStep: 1,  lastStep: 3  },
  { id: 2, label: "Building Shape",       shortLabel: "Shape",     firstStep: 4,  lastStep: 7  },
  { id: 3, label: "Building Envelope",    shortLabel: "Envelope",  firstStep: 8,  lastStep: 13 },
  { id: 4, label: "HVAC Systems",         shortLabel: "HVAC",      firstStep: 14, lastStep: 17 },
  { id: 5, label: "Equipment & Lighting", shortLabel: "Equipment", firstStep: 18, lastStep: 21 },
  { id: 6, label: "Analysis Results",     shortLabel: "Results",   firstStep: 22, lastStep: 26 },
  { id: 7, label: "ECM Evaluation",       shortLabel: "ECM",       firstStep: 27, lastStep: 30 },
];

export const SUB_STEPS: SubStepConfig[] = [
  { id: 1,  section: 1, label: "Project Information"  },
  { id: 2,  section: 1, label: "Building Properties"  },
  { id: 3,  section: 1, label: "Utility Data Source"  },
  { id: 4,  section: 2, label: "Floor Plan Shape"      },
  { id: 5,  section: 2, label: "Building Orientation" },
  { id: 6,  section: 2, label: "Building Dimensions"  },
  { id: 7,  section: 2, label: "Corner Coordinates"   },
  { id: 8,  section: 3, label: "Exterior Walls"        },
  { id: 9,  section: 3, label: "Roof / Ceiling"        },
  { id: 10, section: 3, label: "Foundation"            },
  { id: 11, section: 3, label: "Air Infiltration"      },
  { id: 12, section: 3, label: "Windows"               },
  { id: 13, section: 3, label: "Shading"               },
  { id: 14, section: 4, label: "Cooling"               },
  { id: 15, section: 4, label: "Heating"               },
  { id: 16, section: 4, label: "Domestic Hot Water"   },
  { id: 17, section: 4, label: "Other Equipment"       },
  { id: 18, section: 5, label: "Kitchen Appliances"   },
  { id: 19, section: 5, label: "Laundry Equipment"    },
  { id: 20, section: 5, label: "Plug Loads"            },
  { id: 21, section: 5, label: "Lighting"             },
  { id: 22, section: 6, label: "Weather Data"          },
  { id: 23, section: 6, label: "Temperature Analysis" },
  { id: 24, section: 6, label: "Degree Day Analysis"  },
  { id: 25, section: 6, label: "End-Use Breakdown"    },
  { id: 26, section: 6, label: "Model Comparison"     },
  { id: 27, section: 7, label: "Financial Parameters" },
  { id: 28, section: 7, label: "ECM Cost Data"         },
  { id: 29, section: 7, label: "ECM Selection"         },
  { id: 30, section: 7, label: "Results Summary"       },
];

export const TOTAL_STEPS = 30;

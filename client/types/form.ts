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

  // ── Lighting hours (from PKL, not shown in UI) ───────────────────────────
  nHoursLighting: string;

  // ── Equipment & Lighting ──────────────────────────────────
  epd: string;
  gpd: string;
  lpd: string;
  daylighting: string;
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

  nHoursLighting: "",

  epd: "1.0",
  gpd: "",
  lpd: "",
  daylighting: "No",
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
  { id: 1, label: "Utility Data",           shortLabel: "Utility",   firstStep: 1,  lastStep: 1  },
  { id: 2, label: "Building Shape",         shortLabel: "Shape",     firstStep: 2,  lastStep: 3  },
  { id: 3, label: "Building Envelope",      shortLabel: "Envelope",  firstStep: 4,  lastStep: 6  },
  { id: 4, label: "Equipment",              shortLabel: "Equipment", firstStep: 7,  lastStep: 7  },
  { id: 5, label: "Lighting & Plug Loads",  shortLabel: "Lighting",  firstStep: 8,  lastStep: 8  },
  { id: 6, label: "HVAC Systems",           shortLabel: "HVAC",      firstStep: 9,  lastStep: 10 },
  { id: 7, label: "Post Retrofit Analysis", shortLabel: "Results",   firstStep: 11, lastStep: 11 },
  { id: 8, label: "Retrofit Analysis",      shortLabel: "Retrofit",  firstStep: 12, lastStep: 15 },
];

export const SUB_STEPS: SubStepConfig[] = [
  { id: 1,  section: 1, label: "Project Setup"            },
  { id: 2,  section: 2, label: "Shape & Orientation"      },
  { id: 3,  section: 2, label: "Dimensions & Coordinates" },
  { id: 4,  section: 3, label: "Walls & Roof"             },
  { id: 5,  section: 3, label: "Foundation & Infiltration"},
  { id: 6,  section: 3, label: "Windows & Shading"        },
  { id: 7,  section: 4, label: "Equipment Power Density"  },
  { id: 8,  section: 5, label: "Lighting & Plug Loads"    },
  { id: 9,  section: 6, label: "Heating & Cooling"        },
  { id: 10, section: 6, label: "Hot Water & Other"        },
  { id: 11, section: 7, label: "Post Retrofit Analysis"   },
  { id: 12, section: 8, label: "Financials & Costs"       },
  { id: 13, section: 8, label: "Retrofit Analysis"        },
  { id: 14, section: 8, label: "Options & Cost"           },
  { id: 15, section: 8, label: "Results Summary"          },
];

export const TOTAL_STEPS = 15;

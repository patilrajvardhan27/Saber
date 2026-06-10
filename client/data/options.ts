/**
 * All dropdown / list options derived from the Python application's
 * Measures CSV files and hardcoded GUI values.
 */

export const BUILDING_TYPES = [
  "Single Family Residential Building",
  "Places of Religious Worship",
];

export const EXT_WALL_CONSTRUCTIONS = [
  "2x4 insulated wood stud with vinyl siding",
  "2x4 insulated wood stud with brick finish",
  "Insulated 8in. Concrete",
];

export const WALL_INSULATIONS = [
  "Uninsulated",
  "R7 Fiberglass",
  "R11 Fiberglass",
  "R13 Fiberglass",
  "R15 Fiberglass",
  "R19 Fiberglass",
  "R21 Fiberglass",
  "R23 Spray Foam",
  "R36 Spray Foam",
];

export const EXT_ROOF_CONSTRUCTIONS = ["Asphalt Shingles"];

export const CEILING_INSULATIONS = [
  "Uninsulated",
  "R7 Fiberglass",
  "R13 Fiberglass",
  "R19 Fiberglass",
  "R30 Fiberglass",
  "R38 Fiberglass",
  "R49 Fiberglass",
  "R60 Fiberglass",
];

export const FOUNDATIONS = ["Slab on grade", "Crawlspace", "Basement"];

export const SLAB_INSULATIONS = [
  "Uninsulated",
  "R5 Rigid Foam",
  "R10 Rigid Foam",
  "R15 Rigid Foam",
  "R20 Rigid Foam",
];

export const ACH50_OPTIONS = ["25", "20", "15", "10", "8", "7", "6", "5", "4", "3", "2"];

export const WINDOW_MATERIALS = [
  "Single Pane Clear",
  "Double Pane Clear",
  "Low-e Double Pane Clear Air Filled",
  "Low-e Double Pane Clear Argon Filled",
  "Low-e Double Pane Insulated Air Filled",
  "Low-e Double Pane Insulated Argon Filled",
  "Low-e Triple Pane Clear Air Filled",
  "Low-e Triple Pane Clear Argon Filled",
  "Low-e Triple Pane Insulated Air Filled",
  "Low-e Triple Pane Insulated Argon Filled",
];

export const ORIENTATIONS = [
  "North",
  "North East",
  "East",
  "South East",
  "South",
  "South West",
  "West",
  "North West",
];

export const SHAPE_TYPES = ["Rectangle", "L-Shape"];

export const COOLING_EQUIPMENT = [
  "NoCooling",
  "Air Conditioner",
  "Air Source Heat Pump",
];

// Efficiency values must match the package's Measures/System-*.csv files exactly so the
// backend can map a selection to an upgrade option. SEER values come from
// System-AirConditioner.csv / System-AirSourceHeatPump.csv.
export const COOLING_EFF_OPTIONS: Record<string, string[]> = {
  NoCooling: [],
  "Air Conditioner": [
    "SEER2 13.4",
    "SEER2 14.3",
    "SEER2 15.2",
    "SEER2 16.2",
    "SEER2 19.1",
    "SEER2 20.0",
    "SEER2 23.0",
    "Other..",
  ],
  "Air Source Heat Pump": [
    "SEER2 15",
    "SEER2 16",
    "SEER2 17",
    "SEER2 18",
    "SEER2 19",
    "Other..",
  ],
};

export const HEATING_EQUIPMENT = [
  "NoHeating",
  "Gas Furnace",
  "Electric Baseboard",
  "Air Source Heat Pump",
];

// Efficiency values must match the package's Measures/System-*.csv files exactly.
// Gas Furnace AFUE values come from System-GasFurnace.csv (stored as fractions);
// Air Source Heat Pump HSPF from System-AirSourceHeatPump.csv; Electric COP = 1.
export const HEATING_EFF_OPTIONS: Record<string, string[]> = {
  NoHeating: [],
  "Gas Furnace": [
    "AFUE 80%",
    "AFUE 90%",
    "AFUE 92.5%",
    "AFUE 95%",
    "AFUE 96%",
    "AFUE 98%",
    "Other..",
  ],
  "Electric Baseboard": ["COP 1.0", "Other.."],
  "Air Source Heat Pump": [
    "HSPF2 8.8",
    "HSPF2 8.9",
    "HSPF2 9.0",
    "HSPF2 9.6",
    "HSPF2 9.8",
    "Other..",
  ],
};

export const DHW_SYSTEM_TYPES = [
  "NoDHWSystem",
  "Gas Heater",
  "Electric Heater",
];

export const COOKING_FUEL_TYPES = ["Electric", "Gas", "Induction"];

export const NIGHT_SETBACK_OPTIONS = [
  "0.0",
  "1.0",
  "2.0",
  "3.0",
  "4.0",
  "5.0",
  "10.0",
  "15.0",
  "20.0",
];

export const LED_OPTIONS = ["0.0", "20.0", "40.0", "60.0", "80.0", "100.0"];

export const YES_NO = ["No", "Yes"];

export const ECM_MEASURE_OPTIONS: Record<string, string[]> = {
  ecmWallInsulation: WALL_INSULATIONS,
  ecmInfiltration: ACH50_OPTIONS,
  ecmCeilingInsulation: CEILING_INSULATIONS,
  ecmWindowMaterial: WINDOW_MATERIALS,
  ecmNightSetback: NIGHT_SETBACK_OPTIONS,
  ecmNightSetbackHours: ["0", "2", "4", "6", "8", "10", "12"],
  ecmDaylighting: YES_NO,
  ecmEconomizer: YES_NO,
  ecmOccupancySensor: YES_NO,
  ecmLED: LED_OPTIONS,
  ecmReduceEquipLoad: ["0%", "5%", "10%", "15%", "20%", "25%"],
  ecmCoolingEff: ["SEER2 13.4", "SEER2 14.3", "SEER2 15.2", "SEER2 16.1", "SEER2 17.0", "SEER2 20.0", "SEER2 23.2"],
  ecmHeatingEqp: HEATING_EQUIPMENT,
  ecmHeatingEff: ["AFUE 80%", "AFUE 85%", "AFUE 90%", "AFUE 92%", "AFUE 95%", "AFUE 98%"],
};

export const ECM_MEASURES = [
  { key: "ecmWallInsulation", label: "Wall Insulation" },
  { key: "ecmInfiltration", label: "Infiltration (ACH50)" },
  { key: "ecmCeilingInsulation", label: "Ceiling Insulation" },
  { key: "ecmWindowMaterial", label: "Window Material" },
  { key: "ecmNightSetback", label: "Night Setback (°F)" },
  { key: "ecmNightSetbackHours", label: "Night Setback Hours" },
  { key: "ecmDaylighting", label: "Daylighting" },
  { key: "ecmEconomizer", label: "Economizer" },
  { key: "ecmOccupancySensor", label: "Occupancy Sensor" },
  { key: "ecmLED", label: "LED Lighting (%)" },
  { key: "ecmReduceEquipLoad", label: "Reduce Equipment Load" },
  { key: "ecmCoolingEff", label: "Cooling Efficiency" },
  { key: "ecmHeatingEqp", label: "Heating Equipment" },
  { key: "ecmHeatingEff", label: "Heating Efficiency" },
] as const;

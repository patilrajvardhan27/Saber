import type { FormState } from "@/types/form";
import type { AnalysisPlots, EcmMetrics, EcmPlots, UtilityData } from "@/context/FormContext";
import { API } from "@/utils/api";

async function toDataUri(url: string): Promise<string> {
  try {
    const res = await fetch(url);
    if (!res.ok) return "";
    const blob = await res.blob();
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve((reader.result as string) ?? "");
      reader.onerror = () => resolve("");
      reader.readAsDataURL(blob);
    });
  } catch {
    return "";
  }
}

function r(label: string, value: string | string[] | undefined, unit = ""): string {
  const v = Array.isArray(value) ? value.join(", ") : value;
  if (!v) return "";
  return `<tr><td class="lbl">${label}</td><td class="val">${v}${unit ? `<span class="u"> ${unit}</span>` : ""}</td></tr>`;
}

function sec(title: string, rows: string, extra = ""): string {
  const filled = rows.replace(/\s/g, "");
  if (!filled && !extra) return "";
  return `<div class="sec"><h2>${title}</h2>${rows ? `<table>${rows}</table>` : ""}${extra}</div>`;
}

function imgBox(src: string, label: string): string {
  if (!src) return "";
  return `<div class="img-box"><img src="${src}" alt="${label}"/><p>${label}</p></div>`;
}

function plotGrid(plots: { label: string; src: string }[]): string {
  const items = plots.filter((p) => p.src);
  if (!items.length) return "";
  return `<div class="plot-grid">${items.map((p) => `<div class="plot-item"><p class="pl">${p.label}</p><img src="${p.src}" alt="${p.label}"/></div>`).join("")}</div>`;
}

const WALL_IMG: Record<string, string> = {
  "2x4 insulated wood stud with vinyl siding": "/envelope/2x4 insulated wood stud with vinyl siding.png",
  "2x4 insulated wood stud with brick finish": "/envelope/2x4 insulated wood stud with brick finish.png",
  "Insulated 8in. Concrete": "/envelope/Insulated 8in. Concrete.png",
};
const FOUND_IMG: Record<string, string> = {
  "Slab on grade": "/foundation/Slab on grade.png",
  Crawlspace: "/foundation/Crawlspace.png",
  Basement: "/foundation/Basement.png",
};
const WIN_IMG: Record<string, string> = {
  "Single Pane Clear": "/windows/single-pane-clear.png",
  "Double Pane Clear": "/windows/double-pane-clear.png",
  "Low-e Double Pane Clear Air Filled": "/windows/low-e-double-pane-air.png",
  "Low-e Double Pane Clear Argon Filled": "/windows/low-e-double-pane-argon.png",
  "Low-e Double Pane Insulated Air Filled": "/windows/low-e-double-pane-air-insulated.png",
  "Low-e Double Pane Insulated Argon Filled": "/windows/low-e-double-pane-argon-insulated.png",
  "Low-e Triple Pane Clear Air Filled": "/windows/low-e-triple-pane-air.png",
  "Low-e Triple Pane Clear Argon Filled": "/windows/low-e-triple-pane-argon.png",
  "Low-e Triple Pane Insulated Air Filled": "/windows/low-e-triple-pane-air-insulated.png",
  "Low-e Triple Pane Insulated Argon Filled": "/windows/low-e-triple-pane-argon-insulated.png",
};

export async function exportPdf(params: {
  state: FormState;
  pklProjectName: string;
  analysisPlots: AnalysisPlots | null;
  analysisWeatherStation: string;
  ecmMetrics: EcmMetrics | null;
  ecmPlots: EcmPlots | null;
  utilityData?: UtilityData | null;
}): Promise<void> {
  const { state, pklProjectName, analysisPlots, analysisWeatherStation, ecmMetrics, ecmPlots, utilityData } = params;
  const projectName = state.projectName || pklProjectName || "Project";
  const origin = window.location.origin;
  const today = new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });

  // Backend already returns plots as data:image/png;base64,... strings — use directly
  const P: Record<string, string> = {};
  if (analysisPlots) {
    for (const [k, f] of Object.entries(analysisPlots)) {
      if (f) P[k] = f;
    }
  }
  if (ecmPlots) {
    for (const [k, f] of Object.entries(ecmPlots)) {
      if (f) P[`ecm_${k}`] = f;
    }
  }

  // Local envelope images — pre-fetch as data URIs so they render in the popup
  const wallSrc = state.extWallConst && WALL_IMG[state.extWallConst]
    ? await toDataUri(`${origin}${WALL_IMG[state.extWallConst]}`)
    : "";
  const roofSrc = state.extRoofConst
    ? await toDataUri(
        state.ceilingInsulation && state.ceilingInsulation !== "Uninsulated"
          ? `${origin}/envelope/Attic Insulation.png`
          : `${origin}/envelope/Asphalt Shingles.png`
      )
    : "";
  const foundSrc = state.foundation && FOUND_IMG[state.foundation]
    ? await toDataUri(`${origin}${FOUND_IMG[state.foundation]}`)
    : "";
  const winSrc = state.windowMaterial?.[0] && WIN_IMG[state.windowMaterial[0]]
    ? await toDataUri(`${origin}${WIN_IMG[state.windowMaterial[0]]}`)
    : "";
  const shadingSrc = await toDataUri(`${origin}/windows/shading-overhang.png`);

  const fmt = (n: number, d = 0) => n.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>${projectName} — Building Audit Report</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,Helvetica,sans-serif;color:#1a2e1a;font-size:13px;background:#fff}
.cover{background:linear-gradient(135deg,#1a3d1a 0%,#2d6a2d 60%,#4a9e4a 100%);color:#fff;padding:56px 48px;min-height:220px;display:flex;flex-direction:column;justify-content:flex-end}
.cover h1{font-size:28px;font-weight:700;letter-spacing:-0.5px;margin-bottom:8px}
.cover .sub{font-size:14px;opacity:0.75;margin-bottom:4px}
.cover .meta{font-size:12px;opacity:0.6;margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.2)}
.sec{padding:20px 32px;border-bottom:1px solid #e0eee0;page-break-inside:avoid}
.sec h2{font-size:14px;font-weight:700;color:#1a3d1a;margin-bottom:12px;padding-left:10px;border-left:4px solid #4a9e4a;text-transform:uppercase;letter-spacing:0.5px}
table{width:100%;border-collapse:collapse}
tr:nth-child(even){background:#f5faf5}
td{padding:6px 10px;vertical-align:top}
.lbl{color:#555;width:45%;font-size:12px}
.val{color:#1a2e1a;font-weight:500;font-size:12px}
.u{color:#888;font-weight:400;font-size:11px}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:12px}
.img-box{text-align:center;border:1px solid #e0eee0;border-radius:8px;overflow:hidden;background:#f9fdf9}
.img-box img{max-width:100%;max-height:180px;object-fit:contain;padding:8px}
.img-box p{font-size:10px;color:#666;padding:4px 8px;border-top:1px solid #e8f0e8;background:#f0f8f0}
.plot-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:12px}
.plot-item img{width:100%;height:200px;object-fit:contain;border-radius:6px;border:1px solid #e0eee0}
.pl{font-size:11px;color:#555;margin-bottom:4px;font-weight:600}
.metric-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px;margin-bottom:4px}
.mc{border:1px solid #d0e8d0;border-radius:10px;padding:14px;text-align:center;background:#f5fbf5}
.mv{font-size:20px;font-weight:700}
.ml{font-size:10px;color:#666;margin-top:4px;line-height:1.3}
.ms{font-size:9px;color:#888;margin-top:2px}
.green{color:#1a7d1a}.orange{color:#c07000}.blue{color:#004db3}.teal{color:#006b6b}
.pb{page-break-before:always}
@media print{
  .pb{page-break-before:always}
  .sec{page-break-inside:avoid}
  .plot-grid{page-break-inside:avoid}
}
</style>
</head>
<body>

<!-- Cover -->
<div class="cover">
  <h1>${projectName}</h1>
  <div class="sub">${state.buildingType || "Building Audit Report"}</div>
  <div class="sub">${state.location || ""}</div>
  <div class="meta">Generated ${today} &nbsp;·&nbsp; Saber BldgAuditTool</div>
</div>

<!-- Section 1: Building Geometry -->
${sec("Building Geometry",
  r("Building Type", state.buildingType) +
  r("Location", state.location) +
  r("Building Shape", state.shapeType) +
  r("Orientation", state.orientation) +
  r("Floor Area", state.floorArea, "ft²") +
  r("Number of Floors", state.flrQty) +
  r("Wall Height", state.wallHt, "ft") +
  (state.shapeType === "Rectangle"
    ? r("Dimensions (X × Y)", state.x1 && state.y1 ? `${state.x1} × ${state.y1} ft` : "")
    : r("Dimensions", [state.x1, state.x2, state.y1, state.y2].filter(Boolean).join(" / ") + " ft"))
)}

<!-- Section 2: Envelope — Walls & Roof -->
${sec("Envelope — Walls & Roof",
  r("Wall Construction", state.extWallConst) +
  r("Wall Insulation", state.wallInsulation) +
  r("Roof Construction", state.extRoofConst) +
  r("Ceiling Insulation", state.ceilingInsulation),
  (wallSrc || roofSrc)
    ? `<div class="two-col">${imgBox(wallSrc, state.extWallConst || "Wall")}${imgBox(roofSrc, state.extRoofConst || "Roof")}</div>`
    : ""
)}

<!-- Section 3: Envelope — Foundation & Infiltration -->
${sec("Envelope — Foundation & Infiltration",
  r("Foundation Type", state.foundation) +
  r("Slab Insulation", state.slabInsulation) +
  r("Air Leakage (ACH50)", state.ach50, "ACH50"),
  foundSrc ? `<div class="two-col">${imgBox(foundSrc, state.foundation || "Foundation")}<div></div></div>` : ""
)}

<!-- Section 4: Envelope — Windows & Shading -->
${sec("Envelope — Windows & Shading",
  r("Window Material", state.windowMaterial) +
  r("WWR Front", state.wwrFront, "%") +
  r("WWR Left", state.wwrLeft, "%") +
  r("WWR Back", state.wwrBack, "%") +
  r("WWR Right", state.wwrRight, "%") +
  r("Overhang Depth", state.overhang, "ft") +
  r("Window Height", state.windowHt, "ft") +
  r("Windows per Wall", state.nWindow),
  winSrc ? `<div class="two-col">${imgBox(winSrc, state.windowMaterial?.[0] || "Window")}${imgBox(shadingSrc, "Shading Overhang")}</div>` : ""
)}

<!-- Section 5: HVAC Systems -->
<div class="pb"></div>
${sec("HVAC — Heating & Cooling",
  r("Heating Equipment", state.heatingEqp) +
  r("Heating Efficiency", state.heatingEffCustom || state.heatingEff) +
  r("Heating Setpoint", state.tsph, "°F") +
  r("Night Setback", state.nightSetback, "°F") +
  r("Setback Hours", state.nNightSetbackHours, "hrs") +
  r("Cooling Equipment", state.coolingEqp) +
  r("Cooling Efficiency", state.coolingEffCustom || state.coolingEff) +
  r("Cooling Setpoint", state.tspc, "°F")
)}
${sec("HVAC — Hot Water & Other",
  r("DHW System Type", state.dhwSystemType) +
  r("DHW Tank Volume", state.dhwTankVol, "gal") +
  r("Economizer", state.economizer) +
  r("Evap / Swamp Cooler", state.swampCooler)
)}

<!-- Section 6: Equipment & Lighting -->
${sec("Equipment",
  r("Equipment Power Density (EPD)", state.epd, "W/ft²") +
  r("Gas Power Density (GPD)", state.gpd, "W/ft²")
)}
${sec("Lighting",
  r("Lighting Power Density", state.lpd, "W/ft²") +
  r("Daylighting Control", state.daylighting) +
  r("LED Fraction (Current)", state.led, "%")
)}

<!-- Section 7: Financials & Costs -->
${sec("Financials & Costs",
  r("Cost per Therm", state.thermCost, "$/therm") +
  r("Cost per kWh", state.kWhCost, "$/kWh") +
  r("Discount Rate", state.discountRate, "%") +
  r("Measure Lifetime", state.lifetime, "yrs")
)}

<!-- Section 8: Utility Data -->
${(() => {
  if (!utilityData) return "";
  const MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  const { year1, year2, year3, rows } = utilityData;
  const hasY2 = rows.some(r => r.kwh2 || r.therms2);
  const hasY3 = rows.some(r => r.kwh3 || r.therms3);
  const fv = (v: string) => (v && v !== "") ? parseFloat(v).toLocaleString("en-US", { maximumFractionDigits: 1 }) : "—";
  const sumCol = (key: keyof typeof rows[0]) =>
    rows.reduce((acc, r) => acc + (parseFloat(r[key] as string) || 0), 0);

  const headerStyle = "text-align:center;padding:5px 8px;font-size:10px;color:#1a3d1a;background:#e8f4e8;border-bottom:1px solid #d0e8d0;border-right:1px solid #d0e8d0";
  const cellStyle = "text-align:center;padding:5px 8px;font-size:11px;border-right:1px solid #e0eee0";
  const lblStyle = "padding:5px 8px;font-size:11px;color:#555;border-right:1px solid #e0eee0";
  const totalStyle = "text-align:center;padding:5px 8px;font-size:11px;font-weight:700;color:#1a3d1a;border-right:1px solid #e0eee0";

  const thead = `<thead><tr style="background:#e8f4e8">
    <th style="${headerStyle};text-align:left;width:100px">Month</th>
    <th style="${headerStyle}">kWh (${year1})</th>
    <th style="${headerStyle}">Therms (${year1})</th>
    ${hasY2 ? `<th style="${headerStyle}">kWh (${year2})</th><th style="${headerStyle}">Therms (${year2})</th>` : ""}
    ${hasY3 ? `<th style="${headerStyle}">kWh (${year3})</th><th style="${headerStyle}">Therms (${year3})</th>` : ""}
  </tr></thead>`;

  const bodyRows = rows.map((row, i) =>
    `<tr style="background:${i % 2 === 0 ? "#fff" : "#f5faf5"}">
      <td style="${lblStyle}">${MONTHS[i]}</td>
      <td style="${cellStyle}">${fv(row.kwh1)}</td>
      <td style="${cellStyle}">${fv(row.therms1)}</td>
      ${hasY2 ? `<td style="${cellStyle}">${fv(row.kwh2)}</td><td style="${cellStyle}">${fv(row.therms2)}</td>` : ""}
      ${hasY3 ? `<td style="${cellStyle}">${fv(row.kwh3)}</td><td style="${cellStyle}">${fv(row.therms3)}</td>` : ""}
    </tr>`
  ).join("");

  const totRow = `<tr style="background:#e8f4e8;border-top:2px solid #c0dcc0">
    <td style="${totalStyle};text-align:left">Annual</td>
    <td style="${totalStyle}">${sumCol("kwh1").toLocaleString("en-US", { maximumFractionDigits: 0 })}</td>
    <td style="${totalStyle}">${sumCol("therms1").toLocaleString("en-US", { maximumFractionDigits: 1 })}</td>
    ${hasY2 ? `<td style="${totalStyle}">${sumCol("kwh2").toLocaleString("en-US", { maximumFractionDigits: 0 })}</td><td style="${totalStyle}">${sumCol("therms2").toLocaleString("en-US", { maximumFractionDigits: 1 })}</td>` : ""}
    ${hasY3 ? `<td style="${totalStyle}">${sumCol("kwh3").toLocaleString("en-US", { maximumFractionDigits: 0 })}</td><td style="${totalStyle}">${sumCol("therms3").toLocaleString("en-US", { maximumFractionDigits: 1 })}</td>` : ""}
  </tr>`;

  return `<div class="sec"><h2>Utility Data</h2>
    <div style="overflow-x:auto">
      <table style="width:100%;border-collapse:collapse;border:1px solid #d0e8d0">
        ${thead}
        <tbody>${bodyRows}${totRow}</tbody>
      </table>
    </div>
  </div>`;
})()}

<!-- Section 9: Retrofit Analysis -->
${(() => {
  const baselineMap: Record<string, string> = {
    ecmWallInsulation:    state.wallInsulation    || "—",
    ecmInfiltration:      state.ach50             || "—",
    ecmCeilingInsulation: state.ceilingInsulation || "—",
    ecmWindowMaterial:    state.windowMaterial?.[0] || "—",
    ecmNightSetback:      state.nightSetback      || "—",
    ecmNightSetbackHours: state.nNightSetbackHours|| "—",
    ecmDaylighting:       state.daylighting       || "No",
    ecmEconomizer:        state.economizer        || "No",
    ecmOccupancySensor:   "No",
    ecmLED:               state.led               || "0",
    ecmReduceEquipLoad:   "0%",
    ecmCoolingEff:        state.coolingEff        || "—",
    ecmHeatingEqp:        state.heatingEqp        || "—",
    ecmHeatingEff:        state.heatingEff        || "—",
  };
  const ecmMeasures = [
    { key: "ecmWallInsulation",    label: "Wall Insulation" },
    { key: "ecmInfiltration",      label: "Infiltration (ACH50)" },
    { key: "ecmCeilingInsulation", label: "Ceiling Insulation" },
    { key: "ecmWindowMaterial",    label: "Window Material" },
    { key: "ecmNightSetback",      label: "Night Setback (°F)" },
    { key: "ecmNightSetbackHours", label: "Night Setback Hours" },
    { key: "ecmDaylighting",       label: "Daylighting" },
    { key: "ecmEconomizer",        label: "Economizer" },
    { key: "ecmOccupancySensor",   label: "Occupancy Sensor" },
    { key: "ecmLED",               label: "LED Lighting (%)" },
    { key: "ecmReduceEquipLoad",   label: "Reduce Equipment Load" },
    { key: "ecmCoolingEff",        label: "Cooling Efficiency" },
    { key: "ecmHeatingEqp",        label: "Heating Equipment" },
    { key: "ecmHeatingEff",        label: "Heating Efficiency" },
  ];
  const hasAny = ecmMeasures.some((m) => (state as unknown as Record<string,string>)[m.key]);
  if (!hasAny) return "";
  const rows = ecmMeasures.map((m, i) => {
    const selected = (state as unknown as Record<string,string>)[m.key] || "No change";
    const baseline = baselineMap[m.key];
    return `<tr style="background:${i % 2 === 0 ? "#fff" : "#f5faf5"}">
      <td class="lbl" style="width:35%">${m.label}</td>
      <td class="val" style="width:30%;color:#888;font-style:italic">${baseline}</td>
      <td class="val" style="width:35%;color:${selected === "No change" ? "#aaa" : "#1a7d1a"};font-weight:${selected === "No change" ? "400" : "600"}">${selected}</td>
    </tr>`;
  }).join("");
  return `<div class="sec"><h2>Retrofit Analysis</h2>
    <table>
      <thead><tr style="background:#e8f4e8">
        <th style="text-align:left;padding:6px 10px;font-size:11px;color:#1a3d1a;width:35%">Measure</th>
        <th style="text-align:left;padding:6px 10px;font-size:11px;color:#1a3d1a;width:30%">Baseline</th>
        <th style="text-align:left;padding:6px 10px;font-size:11px;color:#1a3d1a;width:35%">ECM Option</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </div>`;
})()}

${(() => {
  const appliedBaselineMap: Record<string, string> = {
    ecmWallInsulation:    state.wallInsulation    || "Uninsulated",
    ecmInfiltration:      state.ach50             || "—",
    ecmCeilingInsulation: state.ceilingInsulation || "Uninsulated",
    ecmWindowMaterial:    state.windowMaterial?.[0] || "—",
    ecmNightSetback:      state.nightSetback      || "0",
    ecmNightSetbackHours: state.nNightSetbackHours|| "0",
    ecmDaylighting:       state.daylighting       || "No",
    ecmEconomizer:        state.economizer        || "No",
    ecmOccupancySensor:   "No",
    ecmLED:               state.led               || "0",
    ecmReduceEquipLoad:   "0%",
    ecmCoolingEff:        state.coolingEff        || "—",
    ecmHeatingEqp:        state.heatingEqp        || "—",
    ecmHeatingEff:        state.heatingEff        || "—",
  };
  const ecmDescFns: Record<string, (b: string, s: string) => string> = {
    ecmWallInsulation:    (b, s) => `Wall insulation upgraded from ${b} to ${s}.`,
    ecmInfiltration:      (b, s) => `Air leakage reduced from ${b} ACH50 to ${s} ACH50.`,
    ecmCeilingInsulation: (b, s) => `Ceiling insulation upgraded from ${b} to ${s}.`,
    ecmWindowMaterial:    (b, s) => `Windows upgraded from ${b} to ${s}.`,
    ecmNightSetback:      (b, s) => `Night setback temperature set to ${s}°F (baseline: ${b}°F).`,
    ecmNightSetbackHours: (b, s) => `Night setback extended to ${s} hrs/day (baseline: ${b} hrs).`,
    ecmDaylighting:       () => "Daylighting controls added to reduce lighting energy use.",
    ecmEconomizer:        () => "Air-side economizer added for free cooling during mild weather.",
    ecmOccupancySensor:   () => "Occupancy sensors installed to cut lighting when spaces are unoccupied.",
    ecmLED:               (b, s) => `LED fraction increased from ${b}% to ${s}%.`,
    ecmReduceEquipLoad:   (_b, s) => `Plug load reduction of ${s} applied through equipment scheduling.`,
    ecmCoolingEff:        (b, s) => `Cooling efficiency upgraded from ${b} to ${s} SEER2.`,
    ecmHeatingEqp:        (b, s) => `Heating equipment replaced: ${b} → ${s}.`,
    ecmHeatingEff:        (b, s) => `Heating efficiency upgraded from ${b} to ${s}.`,
  };
  const ecmMeasureList = [
    { key: "ecmWallInsulation",    label: "Wall Insulation" },
    { key: "ecmInfiltration",      label: "Infiltration (ACH50)" },
    { key: "ecmCeilingInsulation", label: "Ceiling Insulation" },
    { key: "ecmWindowMaterial",    label: "Window Material" },
    { key: "ecmNightSetback",      label: "Night Setback (°F)" },
    { key: "ecmNightSetbackHours", label: "Night Setback Hours" },
    { key: "ecmDaylighting",       label: "Daylighting" },
    { key: "ecmEconomizer",        label: "Economizer" },
    { key: "ecmOccupancySensor",   label: "Occupancy Sensor" },
    { key: "ecmLED",               label: "LED Lighting (%)" },
    { key: "ecmReduceEquipLoad",   label: "Reduce Equipment Load" },
    { key: "ecmCoolingEff",        label: "Cooling Efficiency" },
    { key: "ecmHeatingEqp",        label: "Heating Equipment" },
    { key: "ecmHeatingEff",        label: "Heating Efficiency" },
  ];
  const activeItems = ecmMeasureList
    .filter((m) => {
      const val = (state as unknown as Record<string, string>)[m.key];
      return val && val !== "No change" && val !== "" && val !== "No";
    })
    .map((m) => {
      const val = (state as unknown as Record<string, string>)[m.key];
      const desc = ecmDescFns[m.key]?.(appliedBaselineMap[m.key], val) ?? `${m.label} changed to ${val}.`;
      return `<li style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px">
        <span style="min-width:8px;height:8px;border-radius:50%;background:#4a9e4a;margin-top:4px;flex-shrink:0;display:inline-block"></span>
        <span style="font-size:12px;color:#1a2e1a;line-height:1.5"><strong style="color:#1a3d1a">${m.label}:</strong> ${desc}</span>
      </li>`;
    })
    .join("");
  if (!activeItems) return "";
  return `<div class="sec"><h2>Applied ECM Measures</h2><ul style="list-style:none;padding:0;margin:0">${activeItems}</ul></div>`;
})()}

${(P.weather || P.end_use || P.elec_monthly || P.ng_monthly || P.elec_temp_model || P.ff_temp_model || P.elec_dd_model || P.ff_dd_model)
  ? `<div class="pb"></div>
     <div class="sec"><h2>Post Retrofit Analysis</h2>
     ${analysisWeatherStation ? `<p style="font-size:11px;color:#555;margin-bottom:10px">NOAA Weather Station: <strong style="color:#1a3d1a">${analysisWeatherStation}</strong></p>` : ""}

     ${P.weather ? `
       <p class="pl" style="font-size:12px;font-weight:700;color:#1a3d1a;margin:12px 0 6px">Weather Data</p>
       <img src="${P.weather}" alt="Weather Data" style="width:100%;height:200px;object-fit:contain;border-radius:6px;border:1px solid #e0eee0;display:block;margin-bottom:12px"/>
     ` : ""}

     ${(P.elec_temp_model || P.ff_temp_model) ? `
       <p class="pl" style="font-size:12px;font-weight:700;color:#1a3d1a;margin:12px 0 6px">Temperature-Based Change-Point Models</p>
       ${plotGrid([
         { label: "Electricity (Cooling)", src: P.elec_temp_model ?? "" },
         { label: "Fossil Fuel (Heating)",  src: P.ff_temp_model  ?? "" },
       ])}
     ` : ""}

     ${(P.ff_dd_model || P.elec_dd_model) ? `
       <p class="pl" style="font-size:12px;font-weight:700;color:#1a3d1a;margin:12px 0 6px">Degree-Day Models</p>
       ${plotGrid([
         { label: "Heating Degree Days (Fossil Fuel)",   src: P.ff_dd_model   ?? "" },
         { label: "Cooling Degree Days (Electricity)",   src: P.elec_dd_model ?? "" },
       ])}
     ` : ""}

     ${P.end_use ? `
       <p class="pl" style="font-size:12px;font-weight:700;color:#1a3d1a;margin:12px 0 6px">Annual End-Use Energy Breakdown</p>
       <img src="${P.end_use}" alt="End-Use Breakdown" style="width:100%;height:200px;object-fit:contain;border-radius:6px;border:1px solid #e0eee0;display:block;margin-bottom:12px"/>
     ` : ""}

     ${(P.elec_monthly || P.ng_monthly) ? `
       <p class="pl" style="font-size:12px;font-weight:700;color:#1a3d1a;margin:12px 0 6px">Monthly Model vs. Meter Comparison</p>
       ${plotGrid([
         { label: "Electricity (kWh)",       src: P.elec_monthly ?? "" },
         { label: "Natural Gas (Therms)",    src: P.ng_monthly   ?? "" },
       ])}
     ` : ""}

     </div>`
  : ""}

${(ecmMetrics || P.ecm_elec_monthly_comp || P.ecm_ng_monthly_comp)
  ? `<div class="pb"></div>
     <div class="sec"><h2>ECM Package Results</h2>
     ${ecmMetrics ? `<div class="metric-grid">
       <div class="mc"><div class="mv" style="color:#555">$${fmt(ecmMetrics.org_lcc)}</div><div class="ml">Baseline Life-Cycle Cost</div></div>
       <div class="mc"><div class="mv blue">$${fmt(ecmMetrics.lcc)}</div><div class="ml">ECM Package Life-Cycle Cost</div></div>
       <div class="mc"><div class="mv orange">$${fmt(ecmMetrics.tic)}</div><div class="ml">Total Installed Cost</div></div>
     </div>
     <div class="metric-grid" style="grid-template-columns:1fr 1fr;margin-top:12px">
       <div class="mc"><div class="mv green">${fmt(ecmMetrics.kwh_pct_savings, 1)}%</div><div class="ml">Electricity Savings</div><div class="ms">${fmt(ecmMetrics.org_kwh)} → ${fmt(ecmMetrics.eem_kwh)} kWh</div></div>
       <div class="mc"><div class="mv teal">${fmt(ecmMetrics.therms_pct_savings, 1)}%</div><div class="ml">Natural Gas Savings</div><div class="ms">${fmt(ecmMetrics.org_therms)} → ${fmt(ecmMetrics.eem_therms)} therms</div></div>
     </div>` : ""}
     ${(P.ecm_elec_monthly_comp || P.ecm_ng_monthly_comp) ? `
       <p class="pl" style="font-size:12px;font-weight:700;color:#1a3d1a;margin:12px 0 6px">Monthly Energy Comparison — Baseline vs. ECM Package</p>
       ${plotGrid([
         { label: "Electricity (kWh)",    src: P.ecm_elec_monthly_comp ?? "" },
         { label: "Natural Gas (Therms)", src: P.ecm_ng_monthly_comp   ?? "" },
       ])}
     ` : ""}
     </div>`
  : ""}

</body>
</html>`;

  const win = window.open("", "_blank", "width=960,height=800");
  if (!win) {
    alert("Allow pop-ups in your browser to generate the PDF report, then try again.");
    return;
  }
  win.document.write(html + `<script>window.addEventListener('load',function(){window.print()});<\/script>`);
  win.document.close();
  win.focus();
}

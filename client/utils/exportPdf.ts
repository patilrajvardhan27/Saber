import type { FormState } from "@/types/form";
import type { AnalysisPlots, EcmMetrics, EcmPlots } from "@/context/FormContext";

const API = "http://localhost:8000";

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
  ecmMetrics: EcmMetrics | null;
  ecmPlots: EcmPlots | null;
}): Promise<void> {
  const { state, pklProjectName, analysisPlots, ecmMetrics, ecmPlots } = params;
  const projectName = state.projectName || pklProjectName || "Project";
  const origin = window.location.origin;
  const today = new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });

  // Fetch backend plot images as data URIs
  const P: Record<string, string> = {};
  if (analysisPlots && pklProjectName) {
    for (const [k, f] of Object.entries(analysisPlots)) {
      if (f) P[k] = await toDataUri(`${API}/results/${encodeURIComponent(pklProjectName)}/plot/${encodeURIComponent(f)}`);
    }
  }
  if (ecmPlots && pklProjectName) {
    for (const [k, f] of Object.entries(ecmPlots)) {
      if (f) P[`ecm_${k}`] = await toDataUri(`${API}/results/${encodeURIComponent(pklProjectName)}/plot/${encodeURIComponent(f)}`);
    }
  }

  // Local envelope images — use full origin URL
  const wallSrc = state.extWallConst && WALL_IMG[state.extWallConst] ? `${origin}${WALL_IMG[state.extWallConst]}` : "";
  const roofSrc = state.extRoofConst
    ? state.ceilingInsulation && state.ceilingInsulation !== "Uninsulated"
      ? `${origin}/envelope/Attic Insulation.png`
      : `${origin}/envelope/Asphalt Shingles.png`
    : "";
  const foundSrc = state.foundation && FOUND_IMG[state.foundation] ? `${origin}${FOUND_IMG[state.foundation]}` : "";
  const winSrc = state.windowMaterial?.[0] && WIN_IMG[state.windowMaterial[0]] ? `${origin}${WIN_IMG[state.windowMaterial[0]]}` : "";

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
.plot-item img{width:100%;border-radius:6px;border:1px solid #e0eee0}
.pl{font-size:11px;color:#555;margin-bottom:4px;font-weight:600}
.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:12px;margin-bottom:4px}
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
  winSrc ? `<div class="two-col">${imgBox(winSrc, state.windowMaterial?.[0] || "Window")}${imgBox(`${origin}/windows/shading-overhang.png`, "Shading Overhang")}</div>` : ""
)}

<!-- Section 5: HVAC Systems -->
<div class="pb"></div>
${sec("HVAC — Heating & Cooling",
  r("Cooling Equipment", state.coolingEqp) +
  r("Cooling Efficiency", state.coolingEffCustom || state.coolingEff) +
  r("Cooling Setpoint", state.tspc, "°F") +
  r("Heating Equipment", state.heatingEqp) +
  r("Heating Efficiency", state.heatingEffCustom || state.heatingEff) +
  r("Heating Setpoint", state.tsph, "°F") +
  r("Night Setback", state.nightSetback, "°F") +
  r("Setback Hours", state.nNightSetbackHours, "hrs")
)}
${sec("HVAC — Hot Water & Other",
  r("DHW System Type", state.dhwSystemType) +
  r("DHW Tank Volume", state.dhwTankVol, "gal") +
  r("Economizer", state.economizer) +
  r("Evap / Swamp Cooler", state.swampCooler)
)}

<!-- Section 6: Equipment & Lighting -->
${sec("Equipment & Appliances",
  r("Cooking Fuel", state.cookingFuelType) +
  r("Cooking Range", state.cookingRating, "W") +
  r("Refrigerator", state.fridgeRating, "W") +
  r("Dishwasher", state.dishWasherRating, "W") +
  r("Clothes Washer", state.washerRating, "W") +
  r("Clothes Dryer", state.dryerRating, "W") +
  r("Television", state.tvRating, "W") +
  r("Office Equipment", state.officeEqpRating, "W") +
  r("Misc Plug Loads", state.miscPlugLoadRating, "W")
)}
${sec("Lighting",
  r("Lighting Power Density", state.lpd, "W/ft²") +
  r("Operating Hours", state.nHoursLighting, "hrs/yr") +
  r("Daylighting Control", state.daylighting) +
  r("LED Fraction (Current)", state.led, "%")
)}

${(P.weather || P.end_use || P.elec_monthly || P.ng_monthly)
  ? `<div class="pb"></div>
     <div class="sec"><h2>Analysis Results</h2>
     ${plotGrid([
       { label: "Weather Data", src: P.weather ?? "" },
       { label: "End-Use Breakdown", src: P.end_use ?? "" },
       { label: "Electricity Monthly", src: P.elec_monthly ?? "" },
       { label: "Natural Gas Monthly", src: P.ng_monthly ?? "" },
     ])}
     ${plotGrid([
       { label: "Electricity Temperature Model", src: P.elec_temp_model ?? "" },
       { label: "Fossil Fuel Temperature Model", src: P.ff_temp_model ?? "" },
       { label: "Electricity Degree-Day Model", src: P.elec_dd_model ?? "" },
       { label: "Fossil Fuel Degree-Day Model", src: P.ff_dd_model ?? "" },
     ])}
     </div>`
  : ""}

${(ecmMetrics || P.ecm_elec_monthly_comp || P.ecm_ng_monthly_comp)
  ? `<div class="pb"></div>
     <div class="sec"><h2>ECM Package Results</h2>
     ${ecmMetrics ? `<div class="metric-grid">
       <div class="mc"><div class="mv orange">$${fmt(ecmMetrics.tic)}</div><div class="ml">Total Installed Cost</div></div>
       <div class="mc"><div class="mv blue">$${fmt(ecmMetrics.lcc)}</div><div class="ml">Package Life-Cycle Cost</div></div>
       <div class="mc"><div class="mv green">${fmt(ecmMetrics.kwh_pct_savings, 1)}%</div><div class="ml">Electricity Savings</div><div class="ms">${fmt(ecmMetrics.org_kwh)} → ${fmt(ecmMetrics.eem_kwh)} kWh</div></div>
       <div class="mc"><div class="mv teal">${fmt(ecmMetrics.therms_pct_savings, 1)}%</div><div class="ml">Natural Gas Savings</div><div class="ms">${fmt(ecmMetrics.org_therms)} → ${fmt(ecmMetrics.eem_therms)} therms</div></div>
     </div>` : ""}
     ${plotGrid([
       { label: "Electricity — Baseline vs ECM", src: P.ecm_elec_monthly_comp ?? "" },
       { label: "Natural Gas — Baseline vs ECM", src: P.ecm_ng_monthly_comp ?? "" },
     ])}
     </div>`
  : ""}

</body>
</html>`;

  const win = window.open("", "_blank", "width=960,height=800");
  if (!win) {
    alert("Allow pop-ups in your browser to generate the PDF report, then try again.");
    return;
  }
  win.document.write(html);
  win.document.close();
  win.focus();
  setTimeout(() => win.print(), 800);
}

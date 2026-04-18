import type { FormState } from "@/types/form";

const API = "http://localhost:8000";

export async function exportPkl(state: FormState, pklProjectName: string): Promise<void> {
  const raw = state.projectName || pklProjectName || "Project";
  const name = raw.replace(/\s+/g, "");

  const res = await fetch(`${API}/export-pkl/${encodeURIComponent(name)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ form_data: state }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Export failed" }));
    throw new Error(err.detail ?? "PKL export failed");
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${name}-Baseline.pkl`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

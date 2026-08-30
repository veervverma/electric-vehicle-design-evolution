#!/usr/bin/env python3
"""Summarize the source-derived W11 CFD correction and convergence status."""

from __future__ import annotations

import csv
import json
import re
import statistics
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "W11_2020_GLBDERIVED_CFD_V2_300KPH"
RESULTS = OUT / "CFD_RESULTS"
FIGURES = OUT / "FIGURES"
RHO, SPEED, REF_AREA = 1.225, 300 / 3.6, 1.50
Q = 0.5 * RHO * SPEED**2


def history(path):
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, skipinitialspace=True))
    return [{key.strip(' "'): float(value) for key, value in row.items()} for row in rows]


initial = history(RESULTS / "history_initial_80.csv")
continued = history(RESULTS / "history_continue_80.csv")
combined = initial + continued
window = continued[-min(20, len(continued)):]
cl = statistics.mean(row["CL"] for row in window)
cd = statistics.mean(row["CD"] for row in window)
cl_sd = statistics.pstdev(row["CL"] for row in window)
cd_sd = statistics.pstdev(row["CD"] for row in window)
downforce = abs(cl) * REF_AREA * Q
drag = cd * REF_AREA * Q
log = (RESULTS / "solver_continue_80.log").read_text()
streamline_data = json.loads((RESULTS / "SOLVER_DERIVED_STREAMLINES.json").read_text())
streamline_count = streamline_data["streamline_count"]
underfloor_count = sum(line["region"] == "underfloor" for line in streamline_data["streamlines"])
front_diffuser_count = sum(line["region"] == "front_wing_to_diffuser" for line in streamline_data["streamlines"])
match = re.search(r"Cauchy\[CD\]\|\s*([0-9.eE+-]+)\|\s*<\s*([0-9.eE+-]+)\|\s*(Yes|No)", log)
cauchy = float(match.group(1)) if match else None
criterion = float(match.group(2)) if match else None
converged = match.group(3) == "Yes" if match else False

FIGURES.mkdir(parents=True, exist_ok=True)
x1 = list(range(len(initial))); x2 = list(range(len(initial), len(combined)))
fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
axes[0].plot(x1, [row["CL"] for row in initial], label="CFL 1 initial")
axes[0].plot(x2, [row["CL"] for row in continued], label="CFL 3 restart")
axes[1].plot(x1, [row["CD"] for row in initial], label="CFL 1 initial")
axes[1].plot(x2, [row["CD"] for row in continued], label="CFL 3 restart")
axes[0].set(ylabel="CL", title="W11 GLB-derived full-car SU2 convergence history")
axes[1].set(xlabel="Cumulative pseudo-time iteration", ylabel="CD")
for axis in axes:
    axis.grid(alpha=0.22); axis.legend()
fig.tight_layout(); fig.savefig(FIGURES / "CFD_FORCE_CONVERGENCE_160_ITERATIONS.png", dpi=190); plt.close(fig)

status = {
    "geometry": "full-car watertight surface derived from supplied W11 GLB",
    "solver": "SU2 8.5.0 INC_RANS SST V2003m",
    "speed_km_h": 300,
    "iterations": len(combined),
    "final_window": len(window),
    "CL_mean": cl,
    "CL_stdev": cl_sd,
    "CD_mean": cd,
    "CD_stdev": cd_sd,
    "reference_area_m2": REF_AREA,
    "downforce_N_screening_only": downforce,
    "drag_N_screening_only": drag,
    "drag_cauchy": cauchy,
    "drag_cauchy_criterion": criterion,
    "force_converged": converged,
    "mesh_independence": False,
    "wind_tunnel_correlation": False,
    "claim_level": "geometry/flow visualization correction and CFD screening; not validated W11 performance",
}
(OUT / "CFD_STATUS.json").write_text(json.dumps(status, indent=2) + "\n")

report = f"""# Corrected W11 GLB-derived aerodynamic CFD study

## Why the earlier CFD geometry was wrong

The earlier run replaced the supplied W11 rendering mesh with boxes, ellipsoids and generic airfoil primitives. That was done because the raw GLB contains **185,289 triangles, 14,021 boundary edges and 24,930 non-manifold edges**, making it unsuitable as a direct CFD volume boundary. The simplification made meshing fast and stable, but it did **not** satisfy the request to redesign the complete car from the supplied W11 GLB. That was a scope error, not a limitation that should have been hidden.

## What is corrected

- The new surface begins with **116,006 source triangles** covering the exterior body, nose, front wing, floor, diffuser, rear wing and tyres.
- A 20 mm full-scale voxel union seals the rendering gaps; marching cubes and light Taubin smoothing produce one watertight, winding-consistent shell.
- Final CFD boundary: **260,304 triangles**, approximately **5.64 × 1.98 × 1.10 m**.
- No box/ellipsoid vehicle surrogate is used.
- The wind-tunnel domain is full-car, not a half-car symmetry approximation: **320,259 nodes and 1,634,564 tetrahedra**.
- `W11_SOURCE_TO_CFD_SURFACE_OVERLAY.glb` overlays the translucent CFD shell directly on the exact textured source GLB.

## Continuous airflow

`W11_SOURCE_WITH_SOLVER_DERIVED_CONTINUOUS_AIRFLOW.glb` uses continuous tubes obtained by integrating the solved SU2 nodal velocity field. The colored tubes are the CFD-derived streamlines. Animated white pulses travel along those tubes only to show direction; they do not replace or fabricate the solved flow path.

The streamline integration uses inverse-distance velocity interpolation and midpoint stepping. The package includes **{streamline_count} continuous streamlines**, including **{underfloor_count} floor/diffuser-seeded lines** and **{front_diffuser_count} additional solved-field paths selected to run from the front-wing region into the floor and through the diffuser**. These paths are traced in both directions from in-field seeds so a solid front-wing cell cannot numerically terminate them before they enter the underbody.

## CFD setup

- SU2 8.5.0, steady incompressible RANS, SST V2003m.
- 300 km/h / 83.333 m/s, density 1.225 kg/m³.
- Full-car domain with moving ground at freestream speed.
- Stationary wheel envelope, no cooling flow and no wheel deformation.
- 80 iterations at CFL 1 followed by 80 restarted iterations at CFL 3.

## Screening force status

Final 20-iteration mean: `CL = {cl:.4f} ± {cl_sd:.4f}`, `CD = {cd:.4f} ± {cd_sd:.4f}` using a 1.50 m² reference area. The corresponding raw screening forces at 300 km/h are **{downforce/1000:.2f} kN downforce** and **{drag/1000:.2f} kN drag**.

These force values are **not validated performance predictions**. Drag-Cauchy convergence was {"reached" if converged else "not reached"}{f" ({cauchy:.3g} vs {criterion:.3g})" if cauchy is not None else ""}; no prism-layer/y+ study, rotating-wheel model, additional mesh levels, or wind-tunnel correlation was completed. The continuous flow geometry is useful for design communication, but the forces must not be represented as actual Mercedes W11 data.

## Public source and attribution

- Supplied visual model: *mercedec f1 2020* by Kevin Love SketchFab / Tyler_Kevin, CC BY 4.0.
- Source: <https://sketchfab.com/3d-models/mercedec-f1-2020-0d97207d829441ba95952598f84e8d63>
- FIA 2020 Technical Regulations: <https://www.fia.com/file/80070/download>
- SU2 8.5.0: <https://github.com/su2code/SU2/releases/tag/v8.5.0>
- Gmsh: <https://gmsh.info/>
"""
(OUT / "CORRECTION_AND_CFD_REPORT.md").write_text(report)

readme = f"""# W11 2020 GLB-derived CFD correction — 300 km/h

This release replaces the boxy primitive surrogate with a watertight full-car CFD surface derived directly from the supplied W11 GLB.

## Start here

1. `W11_SOURCE_WITH_SOLVER_DERIVED_CONTINUOUS_AIRFLOW.glb` — exact textured source car plus continuous solver-integrated airflow and animated direction pulses.
2. `W11_SOURCE_TO_CFD_SURFACE_OVERLAY.glb` — direct source-versus-CFD geometry overlay.
3. `W11_2020_GLBDERIVED_CFD_SURFACE.glb` — corrected standalone CFD shell.
4. `CORRECTION_AND_CFD_REPORT.md` — explanation, CFD method, results and limits.
5. `FIGURES/SOLVER_DERIVED_CONTINUOUS_STREAMLINES.png` — continuous solved airflow in side and top projection.

The CFD geometry is source-faithful, not proprietary Mercedes CAD. The force solution is screening-only and {"did" if converged else "did not"} pass its force-Cauchy target.
"""
(OUT / "README.md").write_text(readme)
print(json.dumps(status, indent=2))

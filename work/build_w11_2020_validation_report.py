#!/usr/bin/env python3
"""Package the W11 2020 SU2 screening results into auditable reports."""

from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "W11_2020_AERO_CFD_VALIDATION_300KPH"
RESULTS = OUT / "CFD_RESULTS"
CASE = OUT / "CFD_SU2_CASE"

RHO = 1.225
SPEED_KMH = 300.0
SPEED_MS = SPEED_KMH / 3.6
Q = 0.5 * RHO * SPEED_MS**2
G = 9.80665

RUNS = [
    {
        "case": "coarse_stationary_ground_diagnostic",
        "history": "history_coarse_stationary.csv",
        "mesh": "coarse",
        "ground": "stationary slip",
        "nodes": 59882,
        "tets": 266014,
        "solver_status": "residual criterion reached",
        "use": "diagnostic only",
    },
    {
        "case": "medium_stationary_ground_diagnostic",
        "history": "history_medium_stationary.csv",
        "mesh": "medium",
        "ground": "stationary slip",
        "nodes": 124977,
        "tets": 601194,
        "solver_status": "stable final force window",
        "use": "diagnostic only",
    },
    {
        "case": "coarse_moving_ground",
        "history": "history_coarse_moving_ground.csv",
        "mesh": "coarse",
        "ground": "moving wall 83.333 m/s",
        "nodes": 59882,
        "tets": 266014,
        "solver_status": "drag Cauchy 9.74e-5 < 1e-4",
        "use": "screening result",
    },
    {
        "case": "medium_moving_ground",
        "history": "history_medium_moving_ground.csv",
        "mesh": "medium",
        "ground": "moving wall 83.333 m/s",
        "nodes": 124977,
        "tets": 601194,
        "solver_status": "iteration limit; drag Cauchy 5.72e-4 > 1e-4",
        "use": "grid-sensitivity result; not strictly converged",
    },
]


def read_history(path: Path, window: int = 20) -> dict[str, float]:
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle, skipinitialspace=True))
    clean = [{key.strip(' "'): value for key, value in row.items()} for row in rows]
    tail = clean[-min(window, len(clean)) :]
    cl = [float(row["CL"]) for row in tail]
    cd = [float(row["CD"]) for row in tail]
    return {
        "iterations": len(clean),
        "window": len(tail),
        "cl_half_mean": statistics.mean(cl),
        "cl_half_stdev": statistics.pstdev(cl),
        "cd_half_mean": statistics.mean(cd),
        "cd_half_stdev": statistics.pstdev(cd),
        "final_rms_pressure_log10": float(clean[-1]["rms[P]"]),
    }


def enrich(run: dict[str, object]) -> dict[str, object]:
    stats = read_history(RESULTS / str(run["history"]))
    cl_area = 2.0 * abs(stats["cl_half_mean"])  # half model uses REF_AREA = 1 m^2
    cd_area = 2.0 * stats["cd_half_mean"]
    downforce = Q * cl_area
    drag = Q * cd_area
    return {
        **run,
        **stats,
        "full_car_ClA_m2": cl_area,
        "full_car_CdA_m2": cd_area,
        "downforce_N_at_300_kmh": downforce,
        "downforce_kgf_at_300_kmh": downforce / G,
        "drag_N_at_300_kmh": drag,
        "aero_power_kW_at_300_kmh": drag * SPEED_MS / 1000.0,
        "downforce_to_drag": cl_area / cd_area,
    }


rows = [enrich(run) for run in RUNS]
fields = list(rows[0])
with (OUT / "CFD_GRID_AND_FORCE_SUMMARY.csv").open("w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

coarse = next(row for row in rows if row["case"] == "coarse_moving_ground")
medium = next(row for row in rows if row["case"] == "medium_moving_ground")
low_df = min(float(coarse["downforce_N_at_300_kmh"]), float(medium["downforce_N_at_300_kmh"]))
high_df = max(float(coarse["downforce_N_at_300_kmh"]), float(medium["downforce_N_at_300_kmh"]))
mid_df = (low_df + high_df) / 2.0
grid_half_range_pct = ((high_df - low_df) / 2.0) / mid_df * 100.0
cl_grid_change_pct = (
    abs(float(coarse["full_car_ClA_m2"]) - float(medium["full_car_ClA_m2"]))
    / float(coarse["full_car_ClA_m2"])
    * 100.0
)
cd_grid_change_pct = (
    abs(float(coarse["full_car_CdA_m2"]) - float(medium["full_car_CdA_m2"]))
    / float(coarse["full_car_CdA_m2"])
    * 100.0
)

validation = {
    "model": "W11 2020 public-reference-based, de-featured half-car aerodynamic surrogate",
    "solver": "SU2 8.5.0 INC_RANS, SST V2003m, steady",
    "speed_km_h": SPEED_KMH,
    "speed_m_s": SPEED_MS,
    "air_density_kg_m3": RHO,
    "dynamic_pressure_Pa": Q,
    "moving_ground_screening_bracket_N": [low_df, high_df],
    "moving_ground_screening_bracket_kgf": [low_df / G, high_df / G],
    "midpoint_N": mid_df,
    "grid_half_range_percent_of_midpoint": grid_half_range_pct,
    "coarse_to_medium_ClA_change_percent": cl_grid_change_pct,
    "coarse_to_medium_CdA_change_percent": cd_grid_change_pct,
    "checks": {
        "coarse_force_convergence": "pass",
        "medium_force_convergence": "not passed",
        "grid_independence": "not passed",
        "moving_ground_sensitivity": "demonstrated",
        "wind_tunnel_correlation": "not performed",
        "claim_level": "CFD screening / numerical verification, not physical validation",
    },
}
(OUT / "CFD_VALIDATION_STATUS.json").write_text(json.dumps(validation, indent=2) + "\n")

mesh_metadata = {
    "units": "metres",
    "domain_m": {"x": [-10.0, 15.0], "y": [0.0, 5.0], "z": [0.0, 5.0]},
    "coarse": {"nodes": 59882, "tetrahedra": 266014, "body_size_m": 0.24, "underfloor_size_m": 0.024},
    "medium": {"nodes": 124977, "tetrahedra": 601194, "body_size_m": 0.16, "underfloor_size_m": 0.016},
    "boundary_model": "half-car symmetry; moving wall ground; stationary non-rotating wheels",
}
(CASE / "MESH_METADATA.json").write_text(json.dumps(mesh_metadata, indent=2) + "\n")


def fmt_run(row: dict[str, object]) -> str:
    return (
        f"| {row['case']} | {int(row['nodes']):,} | {row['ground']} | "
        f"{float(row['full_car_ClA_m2']):.3f} | {float(row['full_car_CdA_m2']):.3f} | "
        f"{float(row['downforce_N_at_300_kmh'])/1000:.2f} | {float(row['drag_N_at_300_kmh'])/1000:.2f} | "
        f"{row['solver_status']} |"
    )


table = "\n".join(fmt_run(row) for row in rows)
report = f"""# W11 2020 reference study — aerodynamic visualization, estimates, and CFD screening

## Decision summary

An actual **SU2 8.5.0 steady INC_RANS/SST CFD screening study** was completed at **{SPEED_KMH:.0f} km/h ({SPEED_MS:.3f} m/s)**. It is more rigorous than the earlier illustrative airflow animations, but it is **not a wind-tunnel-correlated prediction of the proprietary Mercedes W11**.

The two moving-ground meshes predict a full-car-equivalent downforce bracket of **{low_df/1000:.2f}–{high_df/1000:.2f} kN** (**{low_df/G:.0f}–{high_df/G:.0f} kgf**) at 300 km/h. The midpoint is **{mid_df/1000:.2f} kN**, with a coarse/medium half-range of **±{grid_half_range_pct:.1f}%**. Because full-car ClA changed **{cl_grid_change_pct:.1f}%** from coarse to medium and the medium moving-ground run did not satisfy the specified force-Cauchy threshold, the study **did not achieve mesh independence**. Treat the bracket as screening evidence only, with additional geometry/model uncertainty of at least roughly ±30–40%.

## Run matrix and results

Half-model SU2 coefficients were converted to full-car effective areas as `ClA = 2 × |CL_half| × 1 m²` and `CdA = 2 × CD_half × 1 m²`. Forces use `q = 0.5 ρ V²`, with `ρ = {RHO} kg/m³` and `q = {Q:.2f} Pa`.

| Case | Nodes | Ground | Full ClA (m²) | Full CdA (m²) | Downforce (kN) | Drag (kN) | Solver status |
|---|---:|---|---:|---:|---:|---:|---|
{table}

The stationary/slip-ground runs are diagnostics, not vehicle predictions. Their large loss of downforce demonstrates that a moving ground is essential for this ground-effect-sensitive surrogate.

## What was modeled

- Full-scale, half-car symmetry domain: 25 m long × 5 m half-width × 5 m high.
- De-featured public-information surrogate preserving a 2020-era flat/stepped floor, central plank, short diffuser, exposed wheels, sidepod/body volumes, and inverted multi-element wings.
- Steady incompressible RANS with SST V2003m turbulence model.
- Freestream and moving ground: 83.333 m/s.
- Coarse mesh: 59,882 nodes / 266,014 tetrahedra.
- Medium mesh: 124,977 nodes / 601,194 tetrahedra.

## What was not modeled

- Proprietary Mercedes W11 production CAD, hidden floor details, exact ride heights, rake, suspension deflection, or aero-elasticity.
- Rotating wheels, tyre deformation, cooling flow, exhaust plume, leakage, or yaw.
- Near-wall prism layers with verified y+, transient structures, or a high-order production-quality mesh.
- Physical moving-belt wind-tunnel data or track correlation.

## Numerical verification status

| Check | Result |
|---|---|
| Coarse moving-ground force convergence | Pass: drag Cauchy 9.74e-5 < 1e-4 |
| Medium moving-ground force convergence | Not passed: 5.72e-4 > 1e-4 at the iteration limit |
| Grid independence | Not passed: ClA changed {cl_grid_change_pct:.1f}% and CdA changed {cd_grid_change_pct:.1f}% |
| Ground-boundary sensitivity | Demonstrated; stationary ground is unsuitable |
| Wind-tunnel correlation | Not performed |

This completes a reproducible **CFD screening and numerical verification step**, not experimental validation. Physical validation would require a documented scale model, a rolling-road/moving-belt tunnel, wheel rotation, ride-height control, force-balance calibration, repeat runs, and correlation against the same geometry and conditions.

## Equation-based estimate

`W11_EQUATION_BASED_AERO_ESTIMATE.csv` uses an intentionally transparent assumption of `ClA = 4.20 m²` and `CdA = 1.25 m²`, not a measured W11 value. Its nominal 300 km/h result is about 17.86 kN, which is well above this coarse surrogate CFD bracket. That disagreement is useful: it shows why an uncalibrated coefficient assumption must not be presented as validation.

## Files to inspect

- `W11_2020_WHOLE_CAR_AIRFLOW_PRESENTATION.glb` — animated explanatory airflow presentation; particles are illustrative, not CFD streamlines.
- `FIGURES/CFD_SIDEPLANE_VELOCITY.png` — contour from the solved coarse moving-ground SU2 field.
- `FIGURES/CFD_SIDEPLANE_PRESSURE.png` — solved symmetry-plane pressure coefficient contour.
- `FIGURES/CFD_FORCE_CONVERGENCE.png` — force history for all four cases.
- `FIGURES/CFD_MOVING_GROUND_CONVERGENCE.png` — moving-ground cases on a readable force scale.
- `CFD_GRID_AND_FORCE_SUMMARY.csv` — auditable final-window statistics and force conversions.
- `CFD_RESULTS/` — solver histories, logs, and ParaView-readable VTU output.
- `CFD_SU2_CASE/` — SU2 meshes and configuration files.

## Public references and software

- [FIA 2020 Formula One Technical Regulations](https://www.fia.com/file/80070/download)
- [Formula 1 technical analysis of the W11 Spa floor](https://www.formula1.com/en/latest/article/a-close-look-at-the-w11-upgrades-that-show-how-hard-mercedes-are-pushing-to.9gN4Z9e1WyQLz7hofTf46.9gN4Z9e1WyQLz7hofTf46)
- [Formula 1 W11 suspension analysis](https://www.formula1.com/en/latest/article/tech-tuesday-why-das-is-only-the-second-most-impressive-innovation-on-the.2EfeudguxvleJcSV7GJ2TZ)
- [Mercedes-AMG F1 W11 EQ Performance technical specification](https://media.mercedes-benz.com/article/95002cb8-fdee-4190-82fb-c2b00feaf8db)
- [SU2 v8.5.0 release](https://github.com/su2code/SU2/releases/tag/v8.5.0)
- [SU2 incompressible turbulent tutorial](https://su2code.github.io/tutorials/Inc_Turbulent_NACA0012/)
- [Gmsh](https://gmsh.info/)
"""
(OUT / "CFD_VALIDATION_REPORT.md").write_text(report)

readme = f"""# W11 2020 aerodynamic CFD package — 300 km/h

This folder contains the rerun aerodynamic presentation, equation-based estimate, reproducible SU2 cases, solved CFD output, and numerical verification report for the latest W11 2020 public-reference-based design.

## Headline result

- Actual open-source CFD was run with SU2 8.5.0 using steady incompressible RANS/SST.
- Moving-ground screening bracket at 300 km/h: **{low_df/1000:.2f}–{high_df/1000:.2f} kN downforce**.
- The result is **not mesh-independent and not wind-tunnel validated**. It is a documented screening estimate, not an exact Mercedes W11 claim.

Start with:

1. [`CFD_VALIDATION_REPORT.md`](CFD_VALIDATION_REPORT.md) — method, results, and limitations.
2. [`W11_2020_WHOLE_CAR_AIRFLOW_PRESENTATION.glb`](W11_2020_WHOLE_CAR_AIRFLOW_PRESENTATION.glb) — browser-viewable animated presentation.
3. [`CFD_GRID_AND_FORCE_SUMMARY.csv`](CFD_GRID_AND_FORCE_SUMMARY.csv) — numeric results.
4. [`RUN_CFD.md`](RUN_CFD.md) — reproducibility instructions.

The GLB airflow particles are explanatory animation. The PNG contours and VTU files come from the solved SU2 field.
"""
(OUT / "README.md").write_text(readme)

run_cfd = """# Re-running the SU2 cases

## Software

- SU2 8.5.0: <https://github.com/su2code/SU2/releases/tag/v8.5.0>
- Optional mesh regeneration: Python 3 plus the packages in `requirements_cfd.txt`.

## Solver runs

Run from `CFD_SU2_CASE` so each configuration can find its mesh:

```bash
SU2_CFD -t 8 w11_coarse_moving_final.cfg
SU2_CFD -t 8 w11_medium_moving_ground.cfg
```

The stationary-ground configurations are retained only as diagnostics. SU2 output names in the original configurations differ slightly from the curated names under `CFD_RESULTS`; the report records the mapping.

## Mesh regeneration

From the repository root:

```bash
python -m pip install -r outputs/W11_2020_AERO_CFD_VALIDATION_300KPH/requirements_cfd.txt
python work/build_w11_2020_su2_case.py outputs/W11_2020_AERO_CFD_VALIDATION_300KPH/CFD_SU2_CASE/w11_coarse.su2 0.24
python work/build_w11_2020_su2_case.py outputs/W11_2020_AERO_CFD_VALIDATION_300KPH/CFD_SU2_CASE/w11_medium.su2 0.16
```

Use ParaView to inspect `CFD_RESULTS/*.vtu`. A production study should add prism layers/y+ control, rotating wheels, tighter local refinement, further mesh levels, yaw/ride-height sweeps, and experimental correlation.
"""
(OUT / "RUN_CFD.md").write_text(run_cfd)
(OUT / "requirements_cfd.txt").write_text("gmsh>=4.15,<5\nmatplotlib>=3.10,<4\nnumpy>=2.3,<3\n")

print(json.dumps(validation, indent=2))

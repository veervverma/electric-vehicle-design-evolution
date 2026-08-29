# W11 2020 reference study — aerodynamic visualization, estimates, and CFD screening

## Decision summary

An actual **SU2 8.5.0 steady INC_RANS/SST CFD screening study** was completed at **300 km/h (83.333 m/s)**. It is more rigorous than the earlier illustrative airflow animations, but it is **not a wind-tunnel-correlated prediction of the proprietary Mercedes W11**.

The two moving-ground meshes predict a full-car-equivalent downforce bracket of **6.65–9.49 kN** (**678–968 kgf**) at 300 km/h. The midpoint is **8.07 kN**, with a coarse/medium half-range of **±17.6%**. Because full-car ClA changed **29.9%** from coarse to medium and the medium moving-ground run did not satisfy the specified force-Cauchy threshold, the study **did not achieve mesh independence**. Treat the bracket as screening evidence only, with additional geometry/model uncertainty of at least roughly ±30–40%.

## Run matrix and results

Half-model SU2 coefficients were converted to full-car effective areas as `ClA = 2 × |CL_half| × 1 m²` and `CdA = 2 × CD_half × 1 m²`. Forces use `q = 0.5 ρ V²`, with `ρ = 1.225 kg/m³` and `q = 4253.47 Pa`.

| Case | Nodes | Ground | Full ClA (m²) | Full CdA (m²) | Downforce (kN) | Drag (kN) | Solver status |
|---|---:|---|---:|---:|---:|---:|---|
| coarse_stationary_ground_diagnostic | 59,882 | stationary slip | 0.113 | 0.739 | 0.48 | 3.14 | residual criterion reached |
| medium_stationary_ground_diagnostic | 124,977 | stationary slip | 0.191 | 0.711 | 0.81 | 3.03 | stable final force window |
| coarse_moving_ground | 59,882 | moving wall 83.333 m/s | 2.231 | 2.048 | 9.49 | 8.71 | drag Cauchy 9.74e-5 < 1e-4 |
| medium_moving_ground | 124,977 | moving wall 83.333 m/s | 1.564 | 1.834 | 6.65 | 7.80 | iteration limit; drag Cauchy 5.72e-4 > 1e-4 |

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
| Grid independence | Not passed: ClA changed 29.9% and CdA changed 10.5% |
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

# Fine-grid W11 numerical check

Default simulated Reynolds number: **1000**. Full-scale reference at 300 km/h: **32,514,865** (car length 5.699471 m). These conditions are not matched.

| Check | Coarse | Fine |
|---|---:|---:|
| Grid | [480, 144] | [960, 288] |
| Cells | 69,120 | 276,480 |
| Simulated Re | 1000 | 1000 |
| Convective car-length times | 1.000093 | 1.000011 |
| Numerical viscosity (lattice units) | 0.00547149 | 0.01094298 |
| Final maximum lattice Mach | 0.0803 | 0.0803 |
| Final maximum density deviation | 0.681% | 1.029% |
| Wake mean speed / inlet speed | 0.6136 | 0.6173 |
| Wake cells with reverse streamwise flow | 23.18% | 24.21% |

The final maximum values above describe a snapshot, not the maximum over the entire startup. Early acoustic startup transients produce larger deviations. Complete sampled histories are retained in the JSON checks.

Wake mean-speed difference: **0.59%** relative to the fine-grid snapshot. Reverse-flow fraction differs by **1.03 percentage points**.

These are diagnostic early-transient differences, not an accuracy percentage or proof of grid independence. Both runs span only one car-length convective time. Reverse flow is recirculation evidence within this numerical model; it is not proof of turbulent shedding or accurate W11 vortices.

The ultra grid and high-Re endpoint have shorter stability checks documented separately in PARAMETER_SMOKE_CHECKS.json. The ultra grid has not been compared at the same convective age.

## What passed
- Uniform empty-domain flow preservation.
- Re arithmetic and grid-consistent viscosity.
- Zero stored velocity inside solid obstacle cells.
- Finite calculations within the stated Mach/density screening bounds for the recorded runs.
- No artificial vortex forcing.

## What remains unverified
Full-scale Reynolds similarity, settled wake statistics, grid independence, boundary/domain sensitivity, 3D turbulence, accurate force coefficients, physical wind-tunnel correlation.

The numerical update improves the reduced-Re browser experiment; it does not complete the full-scale aerodynamic validation requested earlier.

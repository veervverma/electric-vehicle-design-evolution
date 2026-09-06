# W11 2020 GLB-derived CFD correction — 300 km/h

This release replaces the boxy primitive surrogate with a watertight full-car CFD surface derived directly from the supplied W11 GLB.

## Start here

1. `W11_SOURCE_WITH_SOLVER_DERIVED_CONTINUOUS_AIRFLOW.glb` — exact textured source car plus continuous solver-integrated airflow and animated direction pulses.
2. `W11_SOURCE_TO_CFD_SURFACE_OVERLAY.glb` — direct source-versus-CFD geometry overlay.
3. `W11_2020_GLBDERIVED_CFD_SURFACE.glb` — corrected standalone CFD shell.
4. `CORRECTION_AND_CFD_REPORT.md` — explanation, CFD method, results and limits.
5. `FIGURES/SOLVER_DERIVED_CONTINUOUS_STREAMLINES.png` — continuous solved airflow in side and top projection.
6. [Interactive W11 aerodynamic lab](https://veervverma.github.io/electric-vehicle-design-evolution/wind-tunnel.html) — browser presentation of the detailed W11 with automatic and keyboard-controlled Drive mode, 40 solved paths, camera presets and clearly identified tracing guides.

The CFD geometry is source-faithful, not proprietary Mercedes CAD. The force solution is screening-only and did not pass its force-Cauchy target.

## Interactive visualization limits

The browser lab is an original implementation inspired by the mode-based interaction of Patrick Heintzmann's public Formula demo; it does not copy that site's code, car asset or branding. Cyan and green paths are drawn from `CFD_RESULTS/SOLVER_DERIVED_STREAMLINES.json`. Because the nine floor-seeded paths terminate upstream in the unconverged screening field, orange lines add an explicitly disclosed visual guide from ahead of the front wing to each solver-derived floor/diffuser path. The speed slider changes particle motion and equation-based dynamic pressure (`q = 1/2 rho V^2`); it does not rerun CFD, alter the 300 km/h path geometry, or provide force validation.

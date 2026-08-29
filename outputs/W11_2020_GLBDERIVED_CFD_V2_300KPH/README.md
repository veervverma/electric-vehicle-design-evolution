# W11 2020 GLB-derived CFD correction — 300 km/h

This release replaces the boxy primitive surrogate with a watertight full-car CFD surface derived directly from the supplied W11 GLB.

## Start here

1. `W11_SOURCE_WITH_SOLVER_DERIVED_CONTINUOUS_AIRFLOW.glb` — exact textured source car plus continuous solver-integrated airflow and animated direction pulses.
2. `W11_SOURCE_TO_CFD_SURFACE_OVERLAY.glb` — direct source-versus-CFD geometry overlay.
3. `W11_2020_GLBDERIVED_CFD_SURFACE.glb` — corrected standalone CFD shell.
4. `CORRECTION_AND_CFD_REPORT.md` — explanation, CFD method, results and limits.
5. `FIGURES/SOLVER_DERIVED_CONTINUOUS_STREAMLINES.png` — continuous solved airflow in side and top projection.

The CFD geometry is source-faithful, not proprietary Mercedes CAD. The force solution is screening-only and did not pass its force-Cauchy target.

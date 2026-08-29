# W11 2020 aerodynamic CFD package — 300 km/h

This folder contains the rerun aerodynamic presentation, equation-based estimate, reproducible SU2 cases, solved CFD output, and numerical verification report for the latest W11 2020 public-reference-based design.

## Headline result

- Actual open-source CFD was run with SU2 8.5.0 using steady incompressible RANS/SST.
- Moving-ground screening bracket at 300 km/h: **6.65–9.49 kN downforce**.
- The result is **not mesh-independent and not wind-tunnel validated**. It is a documented screening estimate, not an exact Mercedes W11 claim.

Start with:

1. [`CFD_VALIDATION_REPORT.md`](CFD_VALIDATION_REPORT.md) — method, results, and limitations.
2. [`W11_2020_WHOLE_CAR_AIRFLOW_PRESENTATION.glb`](W11_2020_WHOLE_CAR_AIRFLOW_PRESENTATION.glb) — browser-viewable animated presentation.
3. [`CFD_GRID_AND_FORCE_SUMMARY.csv`](CFD_GRID_AND_FORCE_SUMMARY.csv) — numeric results.
4. [`RUN_CFD.md`](RUN_CFD.md) — reproducibility instructions.

The GLB airflow particles are explanatory animation. The PNG contours and VTU files come from the solved SU2 field.

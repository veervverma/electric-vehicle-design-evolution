# Re-running the SU2 cases

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

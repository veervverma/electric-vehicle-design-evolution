# Design version history

## Sedan design branch

| Stage | Folder | Purpose and major change |
|---|---|---|
| Visual chassis studies | [`outputs/ev_chassis_model`](outputs/ev_chassis_model/) | Early skateboard-chassis, sedan packaging, and exploded-layout reference renders. |
| Advanced sedan V1 | [`outputs/advanced_ev_sedan`](outputs/advanced_ev_sedan/) | First modular printable fastback sedan with separate body, cabin, wing, wheels, suspension/axle modules, and retainers. |
| Advanced sedan V2 | [`outputs/advanced_ev_sedan_v2`](outputs/advanced_ev_sedan_v2/) | More complex monocoque, removable hood, interior, steering/suspension, detailed wheels and brakes, lights, mirrors, and motor cradle. Includes repaired white 3MF. |
| Portfolio sedan V3 | [`outputs/portfolio_ev_sedan_v3`](outputs/portfolio_ev_sedan_v3/) | System-level college portfolio model adding the battery pack, rear motor/gearbox, inverter, charging unit, assembled and exploded references, and presentation drawings. |

## Formula EV design branch

| Version | Folder | Purpose and major change |
|---|---|---|
| Prototype / V1 | [`outputs/formula_ev_prototype`](outputs/formula_ev_prototype/) | New open-wheel EV architecture with monocoque, detachable nose, wings, halo, suspension, wheels, battery, motor/gearbox, inverter, printable parts, assembled STL/3MF, and GLB viewer. |
| V2 detailed | [`outputs/formula_ev_v2_detailed`](outputs/formula_ev_v2_detailed/) | Higher-detail GLB presentation model with named individual systems and animated rear DRS. |
| V3 floor study | [`outputs/formula_ev_v3_2022_2025_floor`](outputs/formula_ev_v3_2022_2025_floor/) | Original educational interpretation of 2022–2025 ground-effect ideas: twin Venturi tunnels, fences, floor edge, plank/skids, diffuser, and underfloor study files. |
| V4 dual active aero | [`outputs/formula_ev_v4_dual_active_aero`](outputs/formula_ev_v4_dual_active_aero/) | Adds independent front active-aero flaps and actuator while retaining rear DRS. |
| V5 all active flaps | [`outputs/formula_ev_v5_all_active_flaps`](outputs/formula_ev_v5_all_active_flaps/) | Six moving front flaps, rear DRS, synchronized whole-car fix, individual GLBs, and 55-part 3MF print kits. |
| V5 print parts | [`outputs/FORMULA_EV_V5_PRINT_PARTS`](outputs/FORMULA_EV_V5_PRINT_PARTS/) | Separate STL export of the complete 55-part V5 assembly with parts/material manifest. |
| V5 conceptual studies | [`outputs/aero_estimate_v5`](outputs/aero_estimate_v5/), [`outputs/v5_track_setups_spa_silverstone_monaco`](outputs/v5_track_setups_spa_silverstone_monaco/), [`outputs/v5_wind_tunnel_and_track_sim`](outputs/v5_wind_tunnel_and_track_sim/) | First-order force estimates, track-specific setup hypotheses, reduced-order lap estimates, and a presentation airflow animation. These are not CFD validation. |
| V6 full-scale CFD rebuild | [`outputs/V6_CFD_REBUILD`](outputs/V6_CFD_REBUILD/) | Parametric 5.45 m Formula EV geometry, separated aerodynamic surfaces, preview GLB, manifest, and prepared 300 km/h OpenFOAM case. This is CFD preparation, not a solved case. |
| V6 repaired print release | [`outputs/V6_PRINT_READY_5_TO_8_INCH`](outputs/V6_PRINT_READY_5_TO_8_INCH/) | Solidified and topology-checked 5-inch and 8-inch derivatives of the V6 model, with explicit-millimeter 3MFs and validated STL alternatives. |

## Important distinction between V5 and V6

V5 is primarily a detailed presentation/animation and multi-part printing model. V6 is a separate full-scale CFD-preparation rebuild with a different parametric geometry pipeline. The later V6 print files are scaled, reinforced, and solidified derivatives made specifically because the full-scale CFD surface export was too large and unsuitable for a consumer slicer.


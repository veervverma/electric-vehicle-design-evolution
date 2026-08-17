# Generation and analysis tools

These Python scripts are the reproducible design record behind the files in `outputs/`. They use lightweight procedural mesh generation and standard-library exporters rather than a production CAD kernel.

| Script | Role |
|---|---|
| `advanced_sedan.py` | Builds the first advanced modular sedan. |
| `advanced_sedan_v2.py` | Builds the more detailed V2 sedan kit and assembled reference. |
| `portfolio_v3.py` | Adds EV systems and portfolio presentation outputs to the sedan branch. |
| `formula_ev.py` | Builds the Formula EV prototype and printable components. |
| `formula_ev_v2_glb.py` | Adds detailed systems, GLB export, named parts, and rear-DRS animation. |
| `formula_ev_v3_floor.py` | Adds the 2022–2025-inspired educational ground-effect floor study. |
| `formula_ev_v4_active_front.py` | Adds independent active front aero. |
| `formula_ev_v5_all_front_flaps.py` | Adds six active front flaps and the V5 complete models. |
| `export_v3_stl.py` | Exports assembled V3 geometry to STL. |
| `export_v5_print_stls.py` | Exports individual V5 print-part STLs. |
| `package_v5_print_kit.py` | Packages and documents the V5 print kit. |
| `export_formula_viewers.py` | Produces viewer-friendly Formula EV assets. |
| `embed_v6_actual_side_profile.py` | Updates V6 presentation geometry used in comparison visuals. |
| `rebuild_v6_cfd.py` | Rebuilds the full-scale V6 surfaces and OpenFOAM preparation package. |
| `make_v6_print_ready.py` | Repairs, reinforces, scales, solidifies, and validates the 5-inch and 8-inch V6 print models. |
| `audit_stl_mesh.py` | Audits STL topology, boundaries, degeneracy, dimensions, and shells. |
| `aero_estimate_v5.py` | Creates the first-order V5 force estimate. |
| `track_sim_v5.py` | Creates reduced-order track/lap estimates. |
| `v5_track_setups.py` | Creates Spa, Silverstone, and Monaco setup hypotheses. |
| `venturi_animation.py` | Creates the conceptual wind-tunnel/flow presentation animation. |
| `build_repository_docs.py` | Regenerates folder READMEs, manifests, and the browser gallery catalog. |

## Reproducibility note

The outputs reflect the scripts and assumptions at the time each version was created. Regeneration can replace files in `outputs/`; preserve a clean Git commit before rerunning a generator. Aerodynamic scripts implement conceptual reduced-order equations and should not be represented as validated CFD.


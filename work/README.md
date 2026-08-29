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
| `build_w11_v6_static_hybrid.py` | Builds the static 8-inch W11-reference/V6-floor hybrid, complete EV chassis, rolling-wheel print kit, GLBs, STLs, 3MF, validation, and package archive. |
| `build_w11_2020_research_rebuild.py` | Replaces the V6 tunnel concept with a source-backed 2020 W11 flat/stepped floor, carbon-honeycomb chassis study, hybrid packaging, pushrod front suspension, swept pullrod rear suspension, and a complete 8-inch print/view package. |
| `build_w11_2020_su2_case.py` | Builds the full-scale, de-featured W11 2020 half-car meshes used for reproducible SU2 CFD screening. |
| `build_w11_2020_aero_outputs.py` | Builds the animated whole-car airflow presentation, equation estimate, solved-field figures, and force-history charts. |
| `build_w11_2020_validation_report.py` | Converts the solved SU2 histories into auditable force, grid-sensitivity, validation-status, and reproducibility reports. |
| `build_w11_2020_glbderived_cfd_v2.py` | Rebuilds the CFD shell directly from the supplied W11 GLB exterior and prepares the corrected full-car domain. |
| `render_w11_glbderived_cfd_figures.py` | Renders source-versus-CFD silhouette and corrected-shell reference figures. |
| `integrate_w11_su2_streamlines.py` | Integrates continuous streamlines from the solved SU2 velocity field and renders flow/side-plane figures. |
| `build_w11_glbderived_visuals.py` | Builds the exact-source overlay GLB and solver-derived continuous-airflow animated GLB. |
| `build_w11_glbderived_cfd_report.py` | Summarizes convergence, screening forces, geometry correction, assumptions, and validation limits. |
| `audit_w11_reference.py` | Audits the supplied rendering mesh and documents why its raw shells are unsuitable for direct STL printing. |
| `audit_stl_mesh.py` | Audits STL topology, boundaries, degeneracy, dimensions, and shells. |
| `aero_estimate_v5.py` | Creates the first-order V5 force estimate. |
| `track_sim_v5.py` | Creates reduced-order track/lap estimates. |
| `v5_track_setups.py` | Creates Spa, Silverstone, and Monaco setup hypotheses. |
| `venturi_animation.py` | Creates the conceptual wind-tunnel/flow presentation animation. |
| `build_repository_docs.py` | Regenerates folder READMEs, manifests, and the browser gallery catalog. |

## Reproducibility note

The outputs reflect the scripts and assumptions at the time each version was created. Regeneration can replace files in `outputs/`; preserve a clean Git commit before rerunning a generator. Most earlier aerodynamic scripts implement conceptual reduced-order equations. The W11 2020 aero package adds actual SU2 RANS screening, but its documented mesh-convergence and physical-correlation limits mean it must not be represented as exact or wind-tunnel-validated W11 data.

# Electric Vehicle Design Evolution

An educational CAD, visualization, 3D-printing, and conceptual aerodynamics portfolio tracing the development of an electric sedan and a Formula-style electric race-car study.

## Explore the project

- **[Interactive browser gallery](https://veervverma.github.io/electric-vehicle-design-evolution/):** displays both GLB and STL models, plays available glTF animations, and exposes every viewable model through a searchable catalog.
- **[Interactive W11 aerodynamic lab](https://veervverma.github.io/electric-vehicle-design-evolution/wind-tunnel.html):** places the detailed W11 reference model in an original browser wind-tunnel scene with continuous solved-flow paths, front-to-diffuser tracing guides, speed telemetry, camera presets, and focused inspection modes.
- **[Version history](VERSIONS.md):** what changed from the first chassis sketches through Formula EV V6.
- **[Model catalog](MODEL_CATALOG.md):** recommended assembled files and direct repository links.
- **[Complete file manifest](FILE_MANIFEST.csv):** path, size, type, and SHA-256 digest for the preserved project artifacts.
- **[Generation and analysis tools](work/README.md):** the scripts used to build, convert, validate, estimate, and package the models.

## Best starting points

| Goal | Recommended file |
|---|---|
| View the final animated V5 car | [`outputs/formula_ev_v5_all_active_flaps/FORMULA_EV_V5_COMPLETE_SYNCED_AERO_FIXED.glb`](outputs/formula_ev_v5_all_active_flaps/FORMULA_EV_V5_COMPLETE_SYNCED_AERO_FIXED.glb) |
| Inspect the V6 CFD-preparation geometry | [`outputs/V6_CFD_REBUILD/V6_FULL_SCALE_CFD_PREVIEW.glb`](outputs/V6_CFD_REBUILD/V6_FULL_SCALE_CFD_PREVIEW.glb) |
| Print the repaired V6 at 8 inches | [`outputs/V6_PRINT_READY_5_TO_8_INCH/V6_8IN_PRINT_READY_SOLID_MM.3mf`](outputs/V6_PRINT_READY_5_TO_8_INCH/V6_8IN_PRINT_READY_SOLID_MM.3mf) |
| Print the repaired V6 at 5 inches | [`outputs/V6_PRINT_READY_5_TO_8_INCH/V6_5IN_PRINT_READY_SOLID_MM.3mf`](outputs/V6_PRINT_READY_5_TO_8_INCH/V6_5IN_PRINT_READY_SOLID_MM.3mf) |
| View the portfolio sedan | [`outputs/portfolio_ev_sedan_v3/EV_SEDAN_V3_COMPLETE_ASSEMBLED.stl`](outputs/portfolio_ev_sedan_v3/EV_SEDAN_V3_COMPLETE_ASSEMBLED.stl) |
| Inspect V5 print parts | [`outputs/FORMULA_EV_V5_PRINT_PARTS/`](outputs/FORMULA_EV_V5_PRINT_PARTS/) |
| View the final static W11/V6 hybrid | [`outputs/W11_V6_HYBRID_STATIC_8IN/W11_REFERENCE_V6_SYSTEMS_ASSEMBLED.glb`](outputs/W11_V6_HYBRID_STATIC_8IN/W11_REFERENCE_V6_SYSTEMS_ASSEMBLED.glb) |
| Print the final 8-inch modular hybrid | [`outputs/W11_V6_HYBRID_STATIC_8IN/W11_V6_ALL_PRINT_PARTS_220MM_PLATE.3mf`](outputs/W11_V6_HYBRID_STATIC_8IN/W11_V6_ALL_PRINT_PARTS_220MM_PLATE.3mf) |
| View the historically corrected W11 2020 rebuild | [`outputs/W11_2020_RESEARCH_REBUILD_STATIC_8IN/W11_2020_REFERENCE_RESEARCH_ASSEMBLED.glb`](outputs/W11_2020_RESEARCH_REBUILD_STATIC_8IN/W11_2020_REFERENCE_RESEARCH_ASSEMBLED.glb) |
| Print the corrected 29-piece W11 model | [`outputs/W11_2020_RESEARCH_REBUILD_STATIC_8IN/W11_2020_ALL_PRINT_PARTS_220MM_PLATE.3mf`](outputs/W11_2020_RESEARCH_REBUILD_STATIC_8IN/W11_2020_ALL_PRINT_PARTS_220MM_PLATE.3mf) |
| View the W11 2020 whole-car airflow presentation | [`outputs/W11_2020_AERO_CFD_VALIDATION_300KPH/W11_2020_WHOLE_CAR_AIRFLOW_PRESENTATION.glb`](outputs/W11_2020_AERO_CFD_VALIDATION_300KPH/W11_2020_WHOLE_CAR_AIRFLOW_PRESENTATION.glb) |
| Explore the interactive W11 wind tunnel | [Open the GitHub Pages aerodynamic lab](https://veervverma.github.io/electric-vehicle-design-evolution/wind-tunnel.html) |
| Review the solved SU2 CFD screening | [`outputs/W11_2020_AERO_CFD_VALIDATION_300KPH/CFD_VALIDATION_REPORT.md`](outputs/W11_2020_AERO_CFD_VALIDATION_300KPH/CFD_VALIDATION_REPORT.md) |

## Repository layout

```text
outputs/   Finished models, print files, previews, reports, CFD preparation, and data
work/      Reproducible Python generation, conversion, validation, and analysis scripts
docs/      Zero-build interactive model gallery for GitHub Pages
```

Every folder under `outputs/` includes its own `README.md` describing its purpose, important files, units, and limitations.

## File-format guide

- **GLB:** preferred for browser viewing, colors, named parts, and animation.
- **STL:** triangle geometry for slicers and GitHub's native STL viewer; STL does not store units.
- **3MF:** preferred for printing when available because it can preserve millimeter units, objects, and material assignments.
- **CSV/SVG/TXT:** conceptual analysis data, plots, reports, and assembly notes.
- **OpenFOAM case:** a prepared CFD starting point, not a completed or validated CFD result.
- **SU2/VTU/CSV:** reproducible CFD cases, ParaView-readable solved fields, and solver histories in the W11 2020 aerodynamic package.

## Accuracy and safety

This repository documents an educational design study—not a road-safe vehicle, homologated race car, validated aerodynamic package, or manufacturing release. The aerodynamic and lap-time outputs are reduced-order conceptual estimates unless a file explicitly states otherwise. The V6 OpenFOAM case was prepared but not solved. The W11 2020 aerodynamic package contains actual SU2 RANS screening, but it did not achieve mesh independence or physical wind-tunnel correlation and is not exact W11 performance data. Always inspect meshes in a slicer, confirm units, test tolerances, and perform appropriate engineering validation before fabrication or powered use.

## License

No open-source or fabrication license has been selected. The repository is provided as a portfolio record; copyright and reuse permission remain with the author unless a license is added later.

# W11 GLB-derived print-ready release — exact 8-inch length

This folder converts the corrected source-GLB-derived W11 aerodynamic shell into a strengthened static display model measuring **203.2 × 71.975 × 40.560 mm**. The main release is a single watertight, positive-volume, connected body so the complete car can be quoted and printed as one object.

## Recommended files

### Lowest-assembly-cost option

- `W11_8IN_ONE_PIECE_PRINT_READY_MM.3mf` — recommended single-object print project with explicit millimeter units, already positioned inside a 220 × 220 mm bed.
- `W11_8IN_ONE_PIECE_PRINT_READY_MM.stl` — the same one-piece model; choose **millimeters** if the slicer asks.
- `W11_8IN_ONE_PIECE_PRINT_READY_PREVIEW.glb` — browser preview of the printable geometry.

The one-piece model is exactly **8.000 inches / 203.2 mm long**, has one connected body, and is watertight. It uses a 0.40 mm printer-scale solidification grid plus one-cell reinforcement around fragile wing edges and junctions.

### Lower-support-risk alternative

- `W11_8IN_THREE_SECTION_PRINT_PLATE_MM.3mf` — front, center and rear sections arranged across approximately 211.2 mm of a 220 mm bed.
- `THREE_SECTION_OPTION/` — the same three sections as separate watertight STL files.

The sections use flat capped butt joints. Bond them with medium CA glue or a small amount of two-part epoxy after dry fitting.

## CFD airflow visualization

- `W11_8IN_CFD_AIRFLOW_POINTS_FRONTWING_TO_DIFFUSER.glb` — the 8-inch printable car with digital CFD streamlines and airflow points.
- `W11_8IN_CFD_AIRFLOW_POINTS_PREVIEW.png` — side and top projections.

Colors in the GLB:

- Blue: overall solved-field airflow.
- Green: floor and diffuser-seeded paths.
- Orange/red: nine additional continuous paths traced from the front-wing region, along the floor and through the diffuser.

The airflow tubes and points are intentionally **not fused into the printable car**. They are digital analysis markers and would otherwise become floating or support-heavy geometry that changes the car's aerodynamic shape. The car itself remains fully printable.

## FDM recommendations

- Material: PLA or PLA+ for the easiest detailed display print; PETG for greater impact resistance.
- Nozzle: 0.25 mm preferred for wing and floor detail; 0.40 mm is supported.
- Layer height: 0.12–0.16 mm.
- Walls: 3; top/bottom layers: 4–5; infill: 12–18% gyroid.
- Supports: organic/tree supports from the build plate, especially beneath the front wing, suspension and rear wing.
- Adhesion: 5–8 mm brim around tyres and front-wing contact areas.
- Orientation: keep the imported upright orientation with z = 0 on the bed.

The one-piece car fits a 220 mm bed with approximately **8.4 mm longitudinal margin at each end**. Actual print price depends on the service's support strategy; one piece avoids assembly labor, while the three-section version can reduce difficult supports and failed-print risk.

## Validation limits

`PRINT_VALIDATION.json` records dimensions, triangle counts, connectivity and topology. This is a static display derivative, not a moving-wheel model. The associated CFD run remains screening-only and did not meet its force-convergence target; the airflow paths are useful for visualization but are not validated Mercedes W11 performance data.


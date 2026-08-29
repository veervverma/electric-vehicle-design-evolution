# W11 2020 OPEN-SOURCE RESEARCH REBUILD - STATIC 8-INCH MODEL

This release corrects the previous hybrid model using the FIA's 2020 rules, Mercedes' published chassis specification, and contemporary Formula 1 technical reporting. The largest correction is the floor: the W11 used the 2020 flat/reference-plane and step-plane architecture with a plank, bargeboards, floor-edge devices and a short diffuser. It did **not** have the deep 2022-style twin Venturi tunnels used in the earlier V6 study.

The model remains static. The four wheels rotate on separate printed axle pins.

## Start here

- `W11_2020_REFERENCE_RESEARCH_ASSEMBLED.glb` - detailed supplied exterior plus the corrected named chassis/floor systems.
- `W11_2020_REFERENCE_RESEARCH_EXPLODED.glb` - lifted exterior showing the revised systems.
- `W11_2020_PRINTABLE_ASSEMBLED.glb` - exact printable procedural assembly.
- `W11_2020_PRINTABLE_EXPLODED.glb` - all printable systems separated.
- `W11_2020_FLAT_STEPPED_FLOOR_ONLY.glb` - reference plane, step plane, plank, bargeboards, rear-tyre vanes and diffuser.
- `W11_2020_CHASSIS_ONLY.glb` - monocoque, impact structures, hybrid powertrain and W11-inspired suspension.
- `W11_2020_ALL_PRINT_PARTS_220MM_PLATE.3mf` - all 29 physical pieces arranged on one 220 x 220 mm plate.

## Finished size and units

Overall length: **203.2 mm / 8.00 in**. Approximate assembled envelope: 203.20 x 74.80 x 40.05 mm. Import STL files as **millimetres**. The 3MF stores millimetres explicitly.

## Historically informed corrections

- Removed the 2022-style twin Venturi tunnels.
- Added 2020 reference-plane and 50 mm step-plane logic at scale.
- Added the 300 mm regulation plank width at scale, with print-thickened skids.
- Replaced the long tunnel diffuser with a short multi-channel 2020 diffuser.
- Added four-element Spa-spec bargeboard stacks and three vanes ahead of each rear tyre.
- Replaced the open EV frame with a carbon-fibre/honeycomb survival-cell study.
- Replaced the flat battery and hub-motor layout with a compact hybrid energy store, V6 turbo-hybrid power-unit study, rear transaxle and rear impact structure.
- Revised suspension to front pushrod and rear pullrod layouts, including the W11's unusually swept lower rear wishbone geometry.

## Printing

- PLA+ is the simplest material for the body, floor, chassis and wings.
- PETG is useful for axle pins, retainers and suspension; TPU 95A is optional for wheels.
- 0.4 mm nozzle, 0.16-0.20 mm layers, 3-4 walls and 18-25% gyroid infill.
- Use tree/build-plate supports for the body, halo, bargeboards, wings and suspension.
- Print the floor broad upper face down. The flat lower surfaces, plank and diffuser will then remain visible after assembly.

## Assembly order

1. Fit the compact energy store, power unit and transaxle around the survival cell.
2. Add the front, side and rear impact structures.
3. Attach this chassis assembly to the upper face of the flat stepped floor.
4. Install front pushrod and rear swept pullrod suspension at X=-53.6 mm and X=+76.2 mm.
5. Glue axle pins into the uprights, slide on the wheels, and glue retainers only to the pin tips. Leave 0.25-0.35 mm lateral play.
6. Fit cockpit and halo, then install the upper body, nose and static wings.

## Accuracy boundary

The floor rules and public external features are source-backed, but Mercedes did not publish production CAD, laminate schedules, exact internal bulkheads, or full aerodynamic surface coordinates. The hidden chassis and powertrain geometry is therefore an informed educational reconstruction, not a reverse-engineered manufacturing replica or validated CFD model. Small legal-scale details were thickened to approximately 0.7-0.8 mm where required for FDM printing.

See `OPEN_SOURCE_RESEARCH_AND_DESIGN_CHANGES.md` for the source-by-source evidence and dimensional translation.

## Exterior reference credit

Original Sketchfab model: `mercedec f1 2020` by Kevin Love SketchFab / Tyler_Kevin, CC BY 4.0: https://sketchfab.com/3d-models/mercedec-f1-2020-0d97207d829441ba95952598f84e8d63

Source GLB SHA-256: `f63aa9ab4a1225080b5968ebbaa7aeb1bc909b506e1cae9d41df6a08b38ec11f`

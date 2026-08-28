# W11 / V6 STATIC 8-INCH HYBRID

This package combines the supplied high-detail 2020 Mercedes-style exterior reference with a newly built, printable V6-derived twin-Venturi floor and a complete educational EV chassis. The design is **static**: there are no DRS or active-front-wing animations. The four printed wheels can rotate on separate axle pins.

## Start here

- `W11_REFERENCE_V6_SYSTEMS_ASSEMBLED.glb` — best high-detail exterior view with named floor/chassis systems.
- `W11_REFERENCE_V6_SYSTEMS_EXPLODED.glb` — exterior lifted so the chassis and floor are easy to inspect.
- `W11_V6_PRINTABLE_ASSEMBLED.glb` — exact procedural geometry represented by the printable files.
- `W11_V6_PRINTABLE_EXPLODED.glb` — exact print parts separated for inspection.
- `W11_V6_ALL_PRINT_PARTS_220MM_PLATE.3mf` — all 25 physical parts arranged on one 220 x 220 mm plate; units are explicitly millimetres.
- `STL_PRINT_PARTS/` — one STL per unique part, with x4 quantities in filenames.
- `GLB_INDIVIDUAL_PARTS/` — each printable part as an individually viewable GLB.

## Finished size

Nominal overall length: **203.2 mm / 8.00 in**. Approximate assembled envelope: 203.20 x 74.80 x 40.05 mm. STL files do not store units, so choose **millimetres** when importing. The 3MF declares millimetres directly.

## Recommended material and settings

- Best simple choice: **PLA+** for all rigid parts.
- Optional upgrade: **PETG** for axle pins, retainers and suspension; **TPU 95A** for the four wheels.
- 0.4 mm nozzle; 0.16-0.20 mm layers; 3-4 walls; 18-25% gyroid infill.
- Use tree/build-plate supports for the body, halo, wings and suspension.
- Print the floor with its broad upper face on the bed so the Venturi channels face upward; rotate after slicing only if your support preview is cleaner.

## Assembly order

1. Fit the low energy store, motor and inverter into the structural chassis.
2. Attach the chassis to the upper face of the twin-Venturi floor. Keep the floor removable if you want the tunnels visible.
3. Attach front and rear suspension at the marked axle stations, approximately X=-53.6 mm and X=+76.2 mm.
4. Glue axle pins into the uprights. Slide on wheels; glue retainers only to the pin tips. Leave about 0.25-0.35 mm lateral play.
5. Fit cockpit insert and halo to the upper body, then attach the removable nose.
6. Place the upper body over the chassis. Attach the static front and rear wings last.

## What is and is not copied

The supplied GLB is retained as the detailed visual exterior in the two `W11_REFERENCE...` files. It is a rendering mesh rather than watertight CAD. The printable body is therefore a strengthened, simplified derivative matched to the reference silhouette; it is not a direct raw conversion of the fragile source mesh. The V6 tunnel/plank/diffuser architecture is newly rebuilt for this 8-inch model and is not validated CFD or structural engineering.

## Reference credit

Original Sketchfab model: `mercedec f1 2020` by Kevin Love SketchFab / Tyler_Kevin, licensed CC BY 4.0: https://sketchfab.com/3d-models/mercedec-f1-2020-0d97207d829441ba95952598f84e8d63

Source GLB SHA-256: `f63aa9ab4a1225080b5968ebbaa7aeb1bc909b506e1cae9d41df6a08b38ec11f`

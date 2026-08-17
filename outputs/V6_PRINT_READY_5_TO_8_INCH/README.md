# Formula EV V6 — repaired 5-inch and 8-inch print release

Consumer-printer derivatives created after the full-scale V6 CFD STL proved too large and topologically unsuitable for slicing. Models were repaired, reinforced, scaled, voxel-solidified, and audited.

## Recommended use

Use the `PRINT_READY_SOLID_MM` 3MF or STL files. The 8-inch version preserves stronger details; the 5-inch version fits smaller beds.

## Units

Millimeters. 5-inch length ≈127 mm; 8-inch length =203.2 mm. Prefer 3MF because it explicitly stores millimeter units.

## Files

| File | Format | Purpose |
|---|---:|---|
| [`MESH_VALIDATION.txt`](MESH_VALIDATION.txt) | TXT | Documentation, assumptions, guide, or report: mesh validation. |
| [`READ_ME_FIRST.txt`](READ_ME_FIRST.txt) | TXT | Documentation, assumptions, guide, or report: read me first. |
| [`V6_5IN_PRINT_READY_SOLID_MM.3mf`](V6_5IN_PRINT_READY_SOLID_MM.3mf) | 3MF | 3MF print project preserving object structure and millimeter units where authored. |
| [`V6_5IN_PRINT_READY_SOLID_MM.stl`](V6_5IN_PRINT_READY_SOLID_MM.stl) | STL | Validated manifold STL prepared for FDM slicing; import as millimeters. |
| [`V6_5IN_SMOOTH_REPAIRED_MM.stl`](V6_5IN_SMOOTH_REPAIRED_MM.stl) | STL | Smoother repaired reference STL retaining intersecting CFD-derived shells; solid version is preferred for slicing. |
| [`V6_8IN_PRINT_READY_SOLID_MM.3mf`](V6_8IN_PRINT_READY_SOLID_MM.3mf) | 3MF | 3MF print project preserving object structure and millimeter units where authored. |
| [`V6_8IN_PRINT_READY_SOLID_MM.stl`](V6_8IN_PRINT_READY_SOLID_MM.stl) | STL | Validated manifold STL prepared for FDM slicing; import as millimeters. |
| [`V6_8IN_SMOOTH_REPAIRED_MM.stl`](V6_8IN_SMOOTH_REPAIRED_MM.stl) | STL | Smoother repaired reference STL retaining intersecting CFD-derived shells; solid version is preferred for slicing. |

## Limitations

One-piece static display derivatives. Active flaps do not move, and small details remain challenging on a typical 0.4 mm FDM nozzle.

Return to the [repository version history](../../VERSIONS.md).

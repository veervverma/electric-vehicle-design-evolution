# Formula EV V6 — full-scale CFD-preparation rebuild

Separate parametric V6 geometry pipeline with 20 named aerodynamic/mechanical surface groups, full-scale preview, part manifest, and a prepared 300 km/h OpenFOAM case.

## Recommended use

Use `V6_FULL_SCALE_CFD_PREVIEW.glb` for viewing, `geometry/` for separated surfaces, and `OpenFOAM_83ms/` as the unsolved CFD starting case.

## Units

Top-level and `geometry/` STL files are millimeters; OpenFOAM `triSurface` copies are meters. Combined model length is approximately 5,450 mm.

## Files

| File | Format | Purpose |
|---|---:|---|
| [`geometry/body.stl`](geometry/body.stl) | STL | Separate triangle-mesh part for body; STL does not store units. |
| [`geometry/canopy.stl`](geometry/canopy.stl) | STL | Separate triangle-mesh part for canopy; STL does not store units. |
| [`geometry/cooling.stl`](geometry/cooling.stl) | STL | Separate triangle-mesh part for cooling; STL does not store units. |
| [`geometry/diffuser.stl`](geometry/diffuser.stl) | STL | Separate triangle-mesh part for diffuser; STL does not store units. |
| [`geometry/floor.stl`](geometry/floor.stl) | STL | Separate triangle-mesh part for floor; STL does not store units. |
| [`geometry/frontFlaps.stl`](geometry/frontFlaps.stl) | STL | Separate triangle-mesh part for frontflaps; STL does not store units. |
| [`geometry/frontWing.stl`](geometry/frontWing.stl) | STL | Separate triangle-mesh part for frontwing; STL does not store units. |
| [`geometry/halo.stl`](geometry/halo.stl) | STL | Separate triangle-mesh part for halo; STL does not store units. |
| [`geometry/nose.stl`](geometry/nose.stl) | STL | Separate triangle-mesh part for nose; STL does not store units. |
| [`geometry/plank.stl`](geometry/plank.stl) | STL | Separate triangle-mesh part for plank; STL does not store units. |
| [`geometry/rearFlap.stl`](geometry/rearFlap.stl) | STL | Separate triangle-mesh part for rearflap; STL does not store units. |
| [`geometry/rearWing.stl`](geometry/rearWing.stl) | STL | Separate triangle-mesh part for rearwing; STL does not store units. |
| [`geometry/sidepods.stl`](geometry/sidepods.stl) | STL | Separate triangle-mesh part for sidepods; STL does not store units. |
| [`geometry/skids.stl`](geometry/skids.stl) | STL | Separate triangle-mesh part for skids; STL does not store units. |
| [`geometry/suspension.stl`](geometry/suspension.stl) | STL | Separate triangle-mesh part for suspension; STL does not store units. |
| [`geometry/venturi.stl`](geometry/venturi.stl) | STL | Separate triangle-mesh part for venturi; STL does not store units. |
| [`geometry/wheelFL.stl`](geometry/wheelFL.stl) | STL | Separate triangle-mesh part for wheelfl; STL does not store units. |
| [`geometry/wheelFR.stl`](geometry/wheelFR.stl) | STL | Separate triangle-mesh part for wheelfr; STL does not store units. |
| [`geometry/wheelRL.stl`](geometry/wheelRL.stl) | STL | Separate triangle-mesh part for wheelrl; STL does not store units. |
| [`geometry/wheelRR.stl`](geometry/wheelRR.stl) | STL | Separate triangle-mesh part for wheelrr; STL does not store units. |
| [`OpenFOAM_83ms/0/k`](OpenFOAM_83ms/0/k) | FILE | Project support file: k. |
| [`OpenFOAM_83ms/0/nut`](OpenFOAM_83ms/0/nut) | FILE | Project support file: nut. |
| [`OpenFOAM_83ms/0/omega`](OpenFOAM_83ms/0/omega) | FILE | Project support file: omega. |
| [`OpenFOAM_83ms/0/p`](OpenFOAM_83ms/0/p) | FILE | Project support file: p. |
| [`OpenFOAM_83ms/0/U`](OpenFOAM_83ms/0/U) | FILE | Project support file: u. |
| [`OpenFOAM_83ms/Allrun`](OpenFOAM_83ms/Allrun) | FILE | Project support file: allrun. |
| [`OpenFOAM_83ms/constant/transportProperties`](OpenFOAM_83ms/constant/transportProperties) | FILE | Project support file: transportproperties. |
| [`OpenFOAM_83ms/constant/triSurface/body.stl`](OpenFOAM_83ms/constant/triSurface/body.stl) | STL | Separate triangle-mesh part for body; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/canopy.stl`](OpenFOAM_83ms/constant/triSurface/canopy.stl) | STL | Separate triangle-mesh part for canopy; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/cooling.stl`](OpenFOAM_83ms/constant/triSurface/cooling.stl) | STL | Separate triangle-mesh part for cooling; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/diffuser.stl`](OpenFOAM_83ms/constant/triSurface/diffuser.stl) | STL | Separate triangle-mesh part for diffuser; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/floor.stl`](OpenFOAM_83ms/constant/triSurface/floor.stl) | STL | Separate triangle-mesh part for floor; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/frontFlaps.stl`](OpenFOAM_83ms/constant/triSurface/frontFlaps.stl) | STL | Separate triangle-mesh part for frontflaps; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/frontWing.stl`](OpenFOAM_83ms/constant/triSurface/frontWing.stl) | STL | Separate triangle-mesh part for frontwing; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/halo.stl`](OpenFOAM_83ms/constant/triSurface/halo.stl) | STL | Separate triangle-mesh part for halo; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/nose.stl`](OpenFOAM_83ms/constant/triSurface/nose.stl) | STL | Separate triangle-mesh part for nose; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/plank.stl`](OpenFOAM_83ms/constant/triSurface/plank.stl) | STL | Separate triangle-mesh part for plank; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/rearFlap.stl`](OpenFOAM_83ms/constant/triSurface/rearFlap.stl) | STL | Separate triangle-mesh part for rearflap; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/rearWing.stl`](OpenFOAM_83ms/constant/triSurface/rearWing.stl) | STL | Separate triangle-mesh part for rearwing; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/sidepods.stl`](OpenFOAM_83ms/constant/triSurface/sidepods.stl) | STL | Separate triangle-mesh part for sidepods; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/skids.stl`](OpenFOAM_83ms/constant/triSurface/skids.stl) | STL | Separate triangle-mesh part for skids; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/suspension.stl`](OpenFOAM_83ms/constant/triSurface/suspension.stl) | STL | Separate triangle-mesh part for suspension; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/venturi.stl`](OpenFOAM_83ms/constant/triSurface/venturi.stl) | STL | Separate triangle-mesh part for venturi; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/wheelFL.stl`](OpenFOAM_83ms/constant/triSurface/wheelFL.stl) | STL | Separate triangle-mesh part for wheelfl; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/wheelFR.stl`](OpenFOAM_83ms/constant/triSurface/wheelFR.stl) | STL | Separate triangle-mesh part for wheelfr; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/wheelRL.stl`](OpenFOAM_83ms/constant/triSurface/wheelRL.stl) | STL | Separate triangle-mesh part for wheelrl; STL does not store units. |
| [`OpenFOAM_83ms/constant/triSurface/wheelRR.stl`](OpenFOAM_83ms/constant/triSurface/wheelRR.stl) | STL | Separate triangle-mesh part for wheelrr; STL does not store units. |
| [`OpenFOAM_83ms/constant/turbulenceProperties`](OpenFOAM_83ms/constant/turbulenceProperties) | FILE | Project support file: turbulenceproperties. |
| [`OpenFOAM_83ms/README.txt`](OpenFOAM_83ms/README.txt) | TXT | Documentation, assumptions, guide, or report: readme. |
| [`OpenFOAM_83ms/system/blockMeshDict`](OpenFOAM_83ms/system/blockMeshDict) | FILE | Project support file: blockmeshdict. |
| [`OpenFOAM_83ms/system/controlDict`](OpenFOAM_83ms/system/controlDict) | FILE | Project support file: controldict. |
| [`OpenFOAM_83ms/system/fvSchemes`](OpenFOAM_83ms/system/fvSchemes) | FILE | Project support file: fvschemes. |
| [`OpenFOAM_83ms/system/fvSolution`](OpenFOAM_83ms/system/fvSolution) | FILE | Project support file: fvsolution. |
| [`OpenFOAM_83ms/system/snappyHexMeshDict`](OpenFOAM_83ms/system/snappyHexMeshDict) | FILE | Project support file: snappyhexmeshdict. |
| [`OpenFOAM_83ms/system/surfaceFeatureExtractDict`](OpenFOAM_83ms/system/surfaceFeatureExtractDict) | FILE | Project support file: surfacefeatureextractdict. |
| [`V6_ASSUMPTIONS_AND_LIMITATIONS.txt`](V6_ASSUMPTIONS_AND_LIMITATIONS.txt) | TXT | Documentation, assumptions, guide, or report: v6 assumptions and limitations. |
| [`V6_COMPLETE_REBUILD_PACKAGE.zip`](V6_COMPLETE_REBUILD_PACKAGE.zip) | ZIP | Convenience archive containing the v6 complete rebuild package package. |
| [`V6_FULL_SCALE_CFD_PREVIEW.glb`](V6_FULL_SCALE_CFD_PREVIEW.glb) | GLB | Browser-viewable binary glTF model for the v6 full scale cfd preview component/system. |
| [`V6_FULL_SCALE_CFD_SURFACES.stl`](V6_FULL_SCALE_CFD_SURFACES.stl) | STL | Combined triangle-mesh reference of the complete design; read this folder's unit and print limitations. |
| [`V6_OPENFOAM_CFD_PACKAGE.zip`](V6_OPENFOAM_CFD_PACKAGE.zip) | ZIP | Convenience archive containing the v6 openfoam cfd package package. |
| [`V6_PART_MANIFEST.csv`](V6_PART_MANIFEST.csv) | CSV | Structured data or manifest table: v6 part manifest. |
| [`V6_REBUILD_README.md`](V6_REBUILD_README.md) | MD | Documentation, assumptions, guide, or report: v6 rebuild readme. |

## Limitations

CFD preparation only. Components were not production-booleaned, and surface checks, meshing, solver runs, mesh independence, and experimental correlation were not completed.

Return to the [repository version history](../../VERSIONS.md).

# Formula EV V6 CFD rebuild

This package contains a full-scale, parametric Formula-style EV concept rebuilt as 20 separately named closed surface components. Its main aerodynamic features are a twin-Venturi floor, throat regions, plank/skids, progressive diffuser, multi-element front wing with separate active flaps, rear wing with separate active flap, sidepods, cooling elements, suspension and four wheels.

## Main files

- `V6_FULL_SCALE_CFD_PREVIEW.glb` — assembled visual inspection model with 20 named meshes.
- `V6_FULL_SCALE_CFD_SURFACES.stl` — combined full-scale surface export in millimetres.
- `geometry/*.stl` — 20 separate CAD/printing surface exports in millimetres.
- `OpenFOAM_83ms/` — prepared 300 km/h steady-RANS case; its private `triSurface` copies are already in metres.
- `V6_PART_MANIFEST.csv` — part list, dimensions, triangle counts and SHA-256 hashes.
- `V6_ASSUMPTIONS_AND_LIMITATIONS.txt` — required limitations.

## Baseline OpenFOAM setup

- 83.333 m/s freestream and moving ground
- rotating wheels at 231.48 rad/s
- k-omega SST turbulence model
- local refinement for the floor, Venturi tunnels, diffuser and wings
- five requested prism layers on major aerodynamic surfaces
- force/drag/lift coefficient monitoring

From an OpenFOAM terminal, enter `OpenFOAM_83ms`, make `Allrun` executable, and run it. Inspect with `surfaceCheck` and `checkMesh` first. Mesh-independence, domain-independence, transient/yaw studies and experimental correlation are still required before treating outputs as engineering predictions.

## Important

This is a CFD-preparation model, not a verified race-car design and not a ready-to-print mini assembly. The combined model is full scale; scale and engineer clearances/connectors before fabrication. No CFD solver or production mesher was available in the creation environment, so no genuine CFD result is included.

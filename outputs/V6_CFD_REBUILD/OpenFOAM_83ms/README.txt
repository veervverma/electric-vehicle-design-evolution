V6 OPENFOAM CFD TEMPLATE — 300 km/h BASELINE

Requires an OpenFOAM distribution containing simpleFoam, blockMesh, surfaceFeatureExtract and snappyHexMesh.

UNITS
- OpenFOAM_83ms/constant/triSurface/*.stl is already converted to metres. Do not scale it again.
- The separate geometry/*.stl files are CAD/printing exports in millimetres.
- Verify the imported bounds with surfaceCheck before meshing. The car should be about 5.6 m long, 2.0 m wide and 1.05 m high.

BASELINE
- Freestream/moving ground: 83.333 m/s (300 km/h)
- Air density for force coefficients: 1.225 kg/m3
- Kinematic viscosity: 1.46e-5 m2/s
- Wheel angular speed: 231.48 rad/s
- Turbulence model: steady RANS k-omega SST
- Active aero is supplied in its modeled baseline position; create separate surface variants for open/closed comparisons.

RUN
  chmod +x Allrun
  ./Allrun

VALIDATION REQUIRED
This is a prepared starting case, not a completed CFD result. Inspect every surface with surfaceCheck, inspect patch names after snappyHexMesh, run checkMesh, monitor force convergence, and perform mesh/domain/turbulence-model independence studies before trusting coefficients. The 30-million-cell safety cap may require approximately 64–128 GB RAM depending on OpenFOAM version and decomposition.

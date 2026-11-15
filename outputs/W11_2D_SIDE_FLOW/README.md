# W11 2D Flow Studio

Open https://veervverma.github.io/electric-vehicle-design-evolution/side-flow.html

## Reference analysis
The Matheorems post at https://x.com/matheorems/status/2121255501283647778 describes a 2D incompressible Navier–Stokes side-profile calculation. Its visible preview shows a warm yellow/orange high-speed field, purple low-speed wake, white tracer streaks and the equations above the car. Video playback was unavailable; no claim is made about unseen motion, solver details or numerical accuracy.

This original implementation adopts that presentation and computes a new flow around a projection of the user's supplied W11 mesh. It does not copy the reference's software, video or car drawing.

## Live calculation
- D2Q9 BGK lattice Boltzmann, 480 × 144 square cells.
- Equilibrium: w*rho*[1 + 3 c·u + 4.5(c·u)^2 − 1.5 u²].
- Viscosity in lattice units: nu = (tau − 1/2)/3.
- Defaults: U = 0.045 lattice cells/step, nu = 0.045 cells²/step; car-length Reynolds number about 182.
- Stationary projected-car obstacle with halfway bounce-back.
- Inlet, top and road rows impose the freestream equilibrium; outlet copies the adjacent interior post-collision distributions. These are simplified boundary conditions, not a validated rolling-road tunnel.
- All physics controls use lattice units. Mesh coordinates derive from full-size geometry but do not establish physical time or 300 km/h similarity.
- The white tracers are interpolated from the computed velocity and played at a readable presentation speed. They are not independent solver particles. Trail appearance and density do not refine the fluid grid.
- Speed, vorticity and relative pressure views share the same live field. Cp-like color scaling is qualitative and does not provide an integrated load.

## Geometry and scope
The obstacle is the union of exterior triangles in side projection of the supplied Mercedes GLB. Parts at different depths overlap, narrow projected gaps can disappear, and this cannot represent 3D underfloor passages, downwash or full-scale race-car turbulence. The displayed crop is closer to the car; the solver still computes the full domain.

This is a low-Mach, weakly compressible approximation to incompressible flow. Current maximum lattice Mach number and density deviation are shown live. No grid independence, force validation, or wind-tunnel correlation has been established. No downforce/drag figure is claimed.

## Controls
- Particle density and trail length: presentation.
- Inlet speed and viscosity: change the evolving fluid calculation.
- Solver steps/update: computation/playback rate, not a physical inlet-speed change.
- Pause/resume and reset.
- Changing parameters can require time to establish a new flow; unstable runs stop with an error.

## Offline use
Extract W11_2D_FLOW_STUDIO.zip and serve the folder with a local HTTP server, then open side-flow.html. Workers and fetch are not supported reliably by opening an HTML file directly with file://.

## Evidence
SOLVER_SMOKE_TEST.json records checks for uniform empty-domain flow, zero velocity inside the obstacle, finite/stable default flow, and acceleration around the obstacle. These are software/numerical checks, not validation. Source: docs/side-flow-worker.js and work/test_sideflow_solver.cjs.

## Attribution and method reference
W11 mesh: Kevin Love SketchFab / Tyler_Kevin, CC BY 4.0, https://sketchfab.com/3d-models/mercedec-f1-2020-0d97207d829441ba95952598f84e8d63 . The raster projection is a modified derivative.
Lattice Boltzmann overview: https://www.scholarpedia.org/article/Lattice_Boltzmann_Method .

# W11 fine-grid, Reynolds-controlled 2D flow study

The original aerodynamic lab embeds this solver at:
https://veervverma.github.io/electric-vehicle-design-evolution/wind-tunnel.html?view=colored

## What changed
- Default 960 × 288 grid (276,480 cells): 4 times the original fluid-grid cell count.
- Optional 1440 × 432 grid (622,080 cells): 9 times the original cell count.
- 480 × 144 baseline retained for comparisons. Every obstacle is rasterized afresh from the same source triangles; the mask is not image-upscaled.
- D2Q9 TRT collision replaces BGK: independent even/odd relaxation with Lambda = 3/16.
- Direct simulated Reynolds control, 100–2,000, default 1,000.
- nu_lattice = U_lattice * L_car_cells / Re_requested. A grid change automatically changes nu to preserve Re.
- Lower lattice inlet speeds, default 0.030, with maximum Mach and density deviation displayed and bounded.
- Flow age is measured in convective car-length times, accumulated every solver step; iteration count is not labelled physical seconds.
- Derived wake velocity arrows and a streamwise-velocity view reveal reverse flow if the calculation produces it. No synthetic swirls or turbulence forcing were added.
- Particles remain restricted to the lower half of the visible domain.
- The full-scale reference Reynolds number is displayed separately, with the mismatch stated explicitly.

## Reynolds number: correction and remaining limitation
For the supplied model, car length is approximately 5.699 m. At 300 km/h, rho = 1.225 kg/m³ and mu = 1.7894e-5 Pa·s give a full-scale length Reynolds number of approximately 32.5 million.

The default simulated Re = 1,000 is a controlled reduced-Re experiment, not a full-scale match. Entering 32.5 million into this grid would not establish a physically accurate F1 wake. At the ultra-grid lattice velocity and length, matching that number would drive the even relaxation time to roughly 0.5000015 while leaving the real boundary layer and 3D turbulence unresolved. A supported numerical input alone does not establish similarity, resolution or validation.

Changing the separate full-scale reference speed changes that comparison only. It does not claim the 2D field has been solved at that dimensional speed. Changing the lattice inlet speed at fixed Re also changes the numerical viscosity, so Reynolds similarity within the reduced-Re 2D model is preserved.

## Geometry and boundaries
The side projection is a union of all selected source exterior triangles. It merges depth-separated wings, tyres and bodywork; it is neither a physical centre-plane cut nor a 3D aerodynamic boundary. The solver domain and simple inlet/top/road equilibrium rows and extrapolated outlet are unchanged. No rotating wheels, resolved wall layers, 3D wake, aeroelasticity or cooling flow.

## Numerical checks
CHECK_coarse.json and CHECK_fine.json document the same Re and comparable convective time, plus maximum Mach, density deviation, mean wake speed and reverse-flow fraction. The wake sampling rectangle is x = 3.1–6.0 m, z = 0.05–1.2 m.

This is an early transient volume/obstacle raster sensitivity check, not a grid-convergence proof. One car-length flow time is too short for a statistically settled wake. PARAMETER_SMOKE_CHECKS.json contains short additional runs, not proof of long-term stability for every setting.

No downforce accuracy, drag accuracy, turbulence spectrum, Strouhal number, statistical wake convergence or physical validation is claimed.

## What remains uncompleted
A full-scale, Reynolds-matched and validated W11 wake requires a suitable 3D geometry and near-wall/wake mesh, transient turbulence treatment, rotating-wheel/moving-road conditions, numerical sensitivity studies and matching experimental evidence. Those requirements are not fulfilled by this browser release.

## Reproduce
Build masks: work/build_w11_fine_masks.py.
Solve/test: work/test_w11_trt.cjs coarse and work/test_w11_trt.cjs fine.
Endpoint smoke checks: work/test_w11_trt_extremes.cjs.
Browser implementation: docs/side-flow-worker.js, docs/side-flow.js, docs/side-flow.html and docs/side-flow.css.

Default TRT formulas:
tau_even = 1/2 + 3 nu
tau_odd = 1/2 + (3/16)/(tau_even - 1/2)
Collision relaxes symmetric and antisymmetric opposite-population pairs separately.

## Sources and attribution
- TRT formulation: Ginzburg, Verhaeghe & d'Humières (2008), https://www.global-sci.com/cicp/article/view/5523 .
- Reynolds similarity: NASA Glenn, https://www.grc.nasa.gov/www/k-12/airplane/reynolds.html .
- W11 source: Kevin Love SketchFab / Tyler_Kevin, CC BY 4.0, https://sketchfab.com/3d-models/mercedec-f1-2020-0d97207d829441ba95952598f84e8d63 . Raster masks are modified derivatives. Source SHA-256 is preserved in each mask.

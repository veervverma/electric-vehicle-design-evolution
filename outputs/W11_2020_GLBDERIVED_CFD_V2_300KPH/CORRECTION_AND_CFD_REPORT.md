# Corrected W11 GLB-derived aerodynamic CFD study

## Why the earlier CFD geometry was wrong

The earlier run replaced the supplied W11 rendering mesh with boxes, ellipsoids and generic airfoil primitives. That was done because the raw GLB contains **185,289 triangles, 14,021 boundary edges and 24,930 non-manifold edges**, making it unsuitable as a direct CFD volume boundary. The simplification made meshing fast and stable, but it did **not** satisfy the request to redesign the complete car from the supplied W11 GLB. That was a scope error, not a limitation that should have been hidden.

## What is corrected

- The new surface begins with **116,006 source triangles** covering the exterior body, nose, front wing, floor, diffuser, rear wing and tyres.
- A 20 mm full-scale voxel union seals the rendering gaps; marching cubes and light Taubin smoothing produce one watertight, winding-consistent shell.
- Final CFD boundary: **260,304 triangles**, approximately **5.64 × 1.98 × 1.10 m**.
- No box/ellipsoid vehicle surrogate is used.
- The wind-tunnel domain is full-car, not a half-car symmetry approximation: **320,259 nodes and 1,634,564 tetrahedra**.
- `W11_SOURCE_TO_CFD_SURFACE_OVERLAY.glb` overlays the translucent CFD shell directly on the exact textured source GLB.

## Continuous airflow

`W11_SOURCE_WITH_SOLVER_DERIVED_CONTINUOUS_AIRFLOW.glb` uses continuous tubes obtained by integrating the solved SU2 nodal velocity field. The colored tubes are the CFD-derived streamlines. Animated white pulses travel along those tubes only to show direction; they do not replace or fabricate the solved flow path.

The streamline integration uses inverse-distance velocity interpolation and midpoint stepping. The package includes **31 continuous streamlines**, including **9 floor/diffuser-seeded lines**. Floor lines are traced in both directions from an in-field seed so a solid front-wing cell cannot numerically terminate the path before it enters the underbody.

## CFD setup

- SU2 8.5.0, steady incompressible RANS, SST V2003m.
- 300 km/h / 83.333 m/s, density 1.225 kg/m³.
- Full-car domain with moving ground at freestream speed.
- Stationary wheel envelope, no cooling flow and no wheel deformation.
- 80 iterations at CFL 1 followed by 80 restarted iterations at CFL 3.

## Screening force status

Final 20-iteration mean: `CL = -0.3188 ± 0.1214`, `CD = 1.8138 ± 0.0664` using a 1.50 m² reference area. The corresponding raw screening forces at 300 km/h are **2.03 kN downforce** and **11.57 kN drag**.

These force values are **not validated performance predictions**. Drag-Cauchy convergence was not reached (0.00639 vs 0.0002); no prism-layer/y+ study, rotating-wheel model, additional mesh levels, or wind-tunnel correlation was completed. The continuous flow geometry is useful for design communication, but the forces must not be represented as actual Mercedes W11 data.

## Public source and attribution

- Supplied visual model: *mercedec f1 2020* by Kevin Love SketchFab / Tyler_Kevin, CC BY 4.0.
- Source: <https://sketchfab.com/3d-models/mercedec-f1-2020-0d97207d829441ba95952598f84e8d63>
- FIA 2020 Technical Regulations: <https://www.fia.com/file/80070/download>
- SU2 8.5.0: <https://github.com/su2code/SU2/releases/tag/v8.5.0>
- Gmsh: <https://gmsh.info/>

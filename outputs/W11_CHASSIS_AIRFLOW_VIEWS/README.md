# W11 underfloor and conceptual cooling airflow views

## Open the views
- Underfloor: https://veervverma.github.io/electric-vehicle-design-evolution/wind-tunnel.html?view=underfloor
- Cooling channels: https://veervverma.github.io/electric-vehicle-design-evolution/wind-tunnel.html?view=cooling

Both are live, reduced-Reynolds-number **2D calculations** with the existing TRT solver. Tracers and arrows sample the computed velocity in fluid cells. No path is drawn through solid chassis members.

## Underfloor / diffuser
The mask comes from a geometric plane section at lateral y = +0.45 m of the repaired, source-derived W11 shell. Unlike the full side silhouette, it does not project tyres and outboard structures across the entire floor passage.

The floor is solid; air can pass through the clearance between its underside and the road and leave at the rear. Labels mark the entry, floor region and diffuser/exit. Vertical scale is exaggerated so the narrow clearance is visible.

The shell was formed from the supplied GLB using a 20 mm voxel repair and a 60k-triangle reduction. It seals some narrow gaps and is not proprietary W11 CAD. The 2D slice does not recover the actual 3D floor aerodynamics.

## Internal cooling / sidepods — conceptual geometry
The supplied model does **not** provide usable internal cooling ducts or calibrated radiator geometry. This view uses a source-derived top projection with two explicitly hypothetical open corridors through the sidepod regions. The central monocoque remains solid.

Channel geometry is an assumption. The computed air follows that assumed geometry; it is not a reconstruction of Mercedes' internal airflow. Radiator cores, heat exchange, fans, calibrated pressure loss, engine-bay outlets, full 3D curvature and wheel motion are not modeled. No cooling capacity or component temperature is reported.

The top-plan vertical coordinate is lateral y shifted by +2.25 m. Reynolds number remains referenced to the source car length, not a duct hydraulic diameter.

## Grid and controls
480 × 144, 960 × 288 and 1440 × 432 masks are independently generated. Flow-region selection is available both in the main lab and within the 2D controls. Re defaults to 1,000 and numerical viscosity preserves the requested Re when the grid changes.

The particle seed bands change with the region: exterior lower half, the floor clearance for the underfloor section, and both assumed internal channels in cooling mode. Solid cells retain zero stored velocity. The solver computes the full domain even when the presentation is cropped.

The full-scale Re mismatch and numerical limits of the earlier fine-grid study remain applicable. These views do not supply validated full-scale forces.

## Checks and interpretation
PASSAGE_CHECKS.json records short runs on the 480 and 960 grids, checking finite flow in representative fluid passage cells and zero velocity in solids. These are smoke checks, not settled passage flow rates, thermal validation, grid independence or an experimental correlation. Startup density transients can be significant; the interface flags density variations above 5%.

## Source and reproduction
work/build_w11_chassis_flow_masks.py regenerates the six masks. It reads the archived shell below and the supplied source GLB already stored under references/. The existing side-flow-worker.js solves the masks without synthetic passage streamlines or vortex forcing.

GEOMETRY/W11_SOURCE_SHELL_METRES_NOT_PRINT_SIZE.stl is the exact shell used to derive the floor section. **Its units are full-scale metres. It is not the 8-inch print model.**

Attribution: Kevin Love SketchFab / Tyler_Kevin, CC BY 4.0. https://sketchfab.com/3d-models/mercedec-f1-2020-0d97207d829441ba95952598f84e8d63 . The masks and repaired shell are modified derivatives.

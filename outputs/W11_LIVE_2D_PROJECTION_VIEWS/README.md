# W11 Live 2D projection views

Both use the existing Colored CFD Live 2D interface and unchanged D2Q9 TRT worker: computed color fields, particle advection, speed/vorticity/pressure display, Reynolds and grid controls. They are not 3D inspection replacements.

Lower car: exact same solid cell list as the existing exterior side-projection simulation at each resolution. Only the display framing and particle seed region change. No repaired shell, invented section or enlarged vertical geometry. Projected body/tyres can overlap and seal the apparent floor gap; this does not represent actual 3D underfloor passages.

Sidepods: unmodified top projection of the original GLB exterior triangles, rasterized with the same projection approach as the exterior side view. No corridors carved through the mask. This calculates EXTERIOR sidepod flow, not internal cooling, radiator pressure loss or heat transfer. Existing solver bottom wall remains a computational boundary; it is not a physical road in this top view. Domain-boundary sensitivity has not been established.

Both show reduced-Re 2D educational flow. Neither has experimental validation, full-scale similarity, grid-independent forces, nor reliable downforce/thermal predictions. Particle density does not refine the solver mesh. Source: references/mercedec-f1-2020/mercedec-f1-2020.glb, Kevin Love SketchFab / Tyler_Kevin, CC BY 4.0.

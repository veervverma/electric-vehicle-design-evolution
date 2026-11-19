# W11 front-wing / tyres / floor-edge / wake flow lab

Open docs/flow-journey.html through a web server, or the published GitHub Pages URL.

Dedicated live colored 2D presentation with two independent solver workers: W11 side projection and W11 top projection. 36,000 animated tracers per view at 100% (72,000 total); shared density, trail, color, grid, pause and reset controls. Coarse grid is the responsive default; fine and ultra remain selectable. Particle count does not change fluid resolution or accuracy.

Source obstacle geometry is unchanged from the W11 projection studies. No new underfloor passages or internal ducts were fabricated. Selected seeding regions cover the front wing/tyres, all longitudinal lower-car regions and downstream wake in side view, and the full exterior floor perimeter/sidepod region in top view. Seeds that fall inside the obstacle are rejected; advection rejects solid-adjacent samples and crossing segments. Some drawn seeds may not be visible when masked or after rejection; the displayed count is the configured tracer population, not measured visible particles.

These are local fluid-motion tracers distributed across regions, not all front-wing-origin pathlines or a continuous solved passage from front wing to diffuser. The projected car can close physical floor gaps, so this cannot calculate the requested whole 3D underfloor or internal chassis/sidepod flow. The top-view lower solver boundary is computational, not a physical road. The two fields are not coupled, and neither provides validated downforce, cooling, or full-scale Reynolds similarity. Diffuser-region wake labels locate the rear region; they are not proof of correct diffuser physics. The underlying reduced-Re D2Q9 TRT worker is unchanged. Startup density warnings and flow age remain visible.

Source model: Kevin Love SketchFab / Tyler_Kevin, CC BY 4.0, references/mercedec-f1-2020/mercedec-f1-2020.glb.

# Reference-inspired W11 learning tools — 24 November 2026

## What was inspected
All three original X post captions were read directly in the browser. Each embedded video reported that media could not be played. No claim is made to have analyzed the actual video motion or reproduced unseen frames.

1. https://x.com/matharium/status/2124201568899883036 — wing incidence, separation, thin-airfoil attached-flow limits.
2. https://x.com/themathpulse/status/2123494395274240216 — pressure/speed relationships and idealized bodies/wakes.
3. https://x.com/matharium/status/2124982069285785662 — illustrative movable-wing downforce/drag trade-offs.

Physics cross-checks: NASA Glenn lift equation, https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation/ and boundary-layer/separation explanation, https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/boundary-layer/ .

## Incorporated into the existing flow-journey page
- Existing W11 side/top projection masks and fluid worker unchanged.
- Qualitative pressure-force direction arrows, computed from adjacent fluid density pressure and mask gradient. Not surface-integrated loads; stair-stepped normals are approximate.
- Click-to-probe local speed ratio and solver Cp = (rho-1)/(1.5 U²), compared with ideal 1 - (speed/U)². The ideal relation is only a comparison, not enforced on viscous unsteady flow.
- Speed/vorticity/pressure presets; no manually injected wake vortices.
- Analytically generated generic NACA 2412 wing, 0–24° static incidence and optional inverted camber. This is NOT the W11 wing. Incidence changes rebuild the mask and restart the field; this is not moving-boundary pitching or dynamic stall. Chord-based Re400, default480×144. W11 remains car-length-based Re1000. Confined 2D reduced-Re learning models, not validated forces or stall thresholds.
- Up to108,000 configured tracers across three independent fields; not all visible simultaneously and not a physical air-density control.
- Hypothetical force calculator with reference estimate sets (Cdown,CD)=(3.8,.85),(2,.55), rho1.225 kg/m³, default area1.5m². Force=qSC; q=.5rho(speed/3.6)². Changing this calculator does NOT alter CFD or W11 geometry. These are NOT W11 aerodynamic coefficients. No claim that the 2020 W11 had later active front/rear wings.

## Checks and remaining limits
SMOKE_CHECKS.json records1200-step coarse-grid checks at4° and20°, Re400: finite output, zero solid-cell velocity, low computed Mach and density variation. A further20° continuation to3680steps yielded maxMa0.09870, max density variation0.00502. These are numerical smoke checks, not convergence, accuracy, mesh independence or physical validation.
Browser tests confirmed wing incidence reset, pressure preset/arrows, calculator outputs, and a live fluid probe. Example probe near the wing showed speed ratio1.21, Cp-0.48 versus ideal comparison-0.46; location/time dependent, not a validation target.
No genuine 3D underfloor/internal duct/radiator flow, accurate full-scale Reynolds similarity, validated downforce or physically calibrated cooling performance is supplied.

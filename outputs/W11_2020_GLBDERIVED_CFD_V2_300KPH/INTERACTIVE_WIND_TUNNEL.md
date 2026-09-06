# Interactive W11 aerodynamic lab

Public viewer: <https://veervverma.github.io/electric-vehicle-design-evolution/wind-tunnel.html>

## Purpose

This page combines the supplied detailed W11 visual model with the latest GLB-derived aerodynamic screening data in an accessible browser presentation. It is designed for visual inspection and portfolio communication, not as a replacement for a CFD solver or physical wind tunnel.

## Controls

- **Drive + Flow:** starts an automatic moving presentation of the W11 with its CFD overlay attached. Press `WASD` or the arrow keys—or hold the on-screen direction buttons—to take manual control. `Space` brakes, `R` resets and `M` toggles the automatic tour.
- **Full Flow:** returns the car to the wind-tunnel datum and shows all 40 solver-integrated flow paths, ambient freestream points and the W11.
- **Front to Diffuser:** isolates the solver-derived floor/diffuser paths and the disclosed upstream continuity traces.
- **Car Inspection:** hides airflow so the detailed source car can be inspected.
- **ISO / Side / Top / Floor:** moves between fixed inspection views while preserving mouse or touch orbiting.
- **Air Speed:** changes particle travel rate and recalculates dynamic pressure using `q = 1/2 rho V^2` at 1.225 kg/m³.
- **Flow Density / Display switches:** reduce animated points or hide path lines, freestream points and the tunnel reference scene.

## Data provenance

- The cyan and green geometry comes from `CFD_RESULTS/SOLVER_DERIVED_STREAMLINES.json`.
- The 40 displayed CFD paths were integrated from the 300 km/h SU2 screening field.
- Orange paths retain each solved floor/diffuser segment but add a smooth upstream visualization guide from ahead of the front wing because the coarse, unconverged field terminated the original floor-seeded integration farther downstream.
- The speed slider does **not** recompute the flow field. It only scales presentation motion and the equation-based dynamic-pressure readout.

## Validation status

The CFD run did not satisfy its convergence target, mesh independence, rotating-wheel treatment, boundary-layer study, or physical wind-tunnel correlation. Therefore neither this page nor the underlying results should be represented as measured Mercedes W11 aerodynamic performance.

## Implementation and attribution

The page is an original Three.js implementation. Its compact mode-selector presentation was inspired by Patrick Heintzmann's public Formula demo, but no source code, branded assets or car model were copied from that site. The W11 visual reference is *mercedec f1 2020* by Kevin Love SketchFab / Tyler_Kevin under CC BY 4.0; full attribution is preserved in `REFERENCE_LICENSE_AND_ATTRIBUTION.txt`.

The supplied W11 GLB contains one fused mesh rather than independently transformable wheel objects. Drive mode therefore moves the complete car and displays rotating wheel-motion arcs; true tyre rotation would require a future wheel-separation/remodeling pass. The attached CFD overlay moves with the presentation rig, but this motion is not a moving-body CFD recomputation.

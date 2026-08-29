# Reproducing the corrected full-car SU2 screening run

## Requirements

- SU2 8.5.0 with `SU2_CFD` available on the command line.
- Approximately 15 GB free working space and enough memory for a 1.63-million-tetrahedron incompressible RANS case.

## Initial 80 iterations

1. Copy the two configuration files and `W11_2020_GLBDERIVED_FULL_DOMAIN.su2.gz` into an empty working folder.
2. Decompress the mesh and rename it `w11_glb_faithful_full.su2`.
3. Run `SU2_CFD w11_glb_faithful_moving_ground.cfg`.

## Restarted 80 iterations

After the initial run has written `restart_w11_glb_faithful.dat`, run:

`SU2_CFD w11_glb_faithful_continue.cfg`

The restart raises CFL from 1 to 3 and writes separate `*_continue` histories and fields. Retain both histories when evaluating convergence. A completed run is not automatically a validated result: inspect residuals and force histories, repeat on multiple mesh levels, add near-wall prism layers with controlled y+, model rotating wheels, and correlate against rolling-road wind-tunnel data before making performance claims.


# OPEN-SOURCE RESEARCH AND DESIGN CHANGES

Research date: 2026-08-28

## What the public evidence supports

### 1. The W11 floor was a 2020 flat/stepped floor, not a 2022 tunnel floor

The FIA 2020 Formula One Technical Regulations, Article 3.7, required the sprung underbody visible from below through the central axle region to lie on either a reference plane or a parallel step plane 50 mm above it. The regulation also specified a 300 mm-wide plank, a diffuser no wider than 1050 mm below the stated height, a maximum 350 mm diffuser extension behind the rear axle in the outer region, and a maximum permitted diffuser-body height of 175 mm in the regulated rear zone.

Source: https://www.fia.com/file/80070/download

Design translation at this model's approximately 1:28.05 scale:

| Full-size rule | True scale | Model implementation |
|---|---:|---:|
| 50 mm step-plane offset | 1.78 mm | 1.8 mm |
| 300 mm plank width | 10.69 mm | 10.7 mm |
| 10 mm plank thickness | 0.36 mm | 0.8 mm, print-thickened |
| 1050 mm diffuser width | 37.42 mm | 37.4-38.0 mm |
| 350 mm diffuser length aft of axle | 12.47 mm | 12.5 mm |
| 175 mm diffuser height | 6.23 mm | approximately 6.2 mm rise |
| 430 mm floor datum aft of front axle | 15.32 mm | 15.3 mm |

This regulatory geometry is why the previous V6 twin-tunnel floor was removed.

### 2. W11 floor edge and bargeboards

Formula 1's September 2020 technical review states that Mercedes' Spa package reduced the lattice-like bargeboard stack from five elements to four and added three vanes ahead of the rear tyre. Those visible features are represented here as separate, printable relief geometry.

Source: https://www.formula1.com/en/latest/article/a-close-look-at-the-w11-upgrades-that-show-how-hard-mercedes-are-pushing-to.9gN4Z9e1WyQLz7hofTf46.9gN4Z9e1WyQLz7hofTf46

### 3. Rear suspension was swept backward to help the diffuser

Formula 1's W11 suspension analysis explains that the lower rear wishbone was swept unusually far rearward. Its front leg mounted well back and the rear leg fed into the rear crash structure, creating more open flow area beside and above the diffuser. The model now uses a narrow-angle, swept lower wishbone and rear pullrod arrangement instead of the earlier symmetric generic module.

Sources:
- https://www.formula1.com/en/latest/article/tech-tuesday-why-das-is-only-the-second-most-impressive-innovation-on-the.2EfeudguxvleJcSV7GJ2TZ
- https://www.formula1.com/en/latest/article/tech-tuesday-how-ferrari-and-hamilton-pushed-mercedes-to-create-the.1zMRmGDpJtpDXrlZBbjIs9

### 4. Chassis and suspension construction

Mercedes' published 2020 technical specification describes a moulded carbon-fibre and honeycomb composite chassis, carbon-fibre bodywork/floor, front carbon wishbones with pushrod-actuated torsion springs and rockers, and rear carbon wishbones with pullrod-actuated inboard springs and dampers. The model now follows that architecture and includes representative impact structures, compact hybrid energy store, power unit and transaxle packaging.

Source: https://media.mercedes-benz.com/article/95002cb8-fdee-4190-82fb-c2b00feaf8db

## Before/after summary

| System | Previous hybrid | Corrected W11 research rebuild |
|---|---|---|
| Main floor | Deep twin Venturi tunnels | Flat reference plane plus raised step plane |
| Floor edge | 2022-style fences | 2020 slots/reliefs, four-stack bargeboards and three rear-tyre vanes |
| Diffuser | Long progressive tunnel diffuser | Short 2020 multi-channel diffuser |
| Chassis | Open frame-like EV rails | Carbon/honeycomb survival-cell study |
| Energy | Flat EV pack | Compact hybrid energy-store packaging |
| Drive unit | Electric motor/gear housing | V6 turbo-hybrid study and rear transaxle |
| Front suspension | Generic static double wishbone | W11-inspired pushrod, multi-link lower arrangement and DAS rack study |
| Rear suspension | Generic symmetric module | Pullrod with swept, narrow-angle lower wishbone and crash-structure pickup |

## Limits

Exact W11 production CAD and internal composite construction remain proprietary. Public photographs and technical reporting support the visible architecture, but not every curvature, laminate, duct or pickup coordinate. This is a source-informed scale study optimized for 3D printing, not an exact Mercedes engineering drawing.

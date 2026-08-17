# Formula EV V5 — first-order aerodynamic estimate

Equation-based force estimate using assumed effective ClA/CdA values, including downforce at speed and a component breakdown.

## Recommended use

Read `AERO_SIMULATION_REPORT.txt`, inspect the source CSV tables, and use the SVG chart for presentation.

## Units

SI units in the CSV and report: m/s, kN, kgf equivalents, square meters, and kW as labeled.

## Files

| File | Format | Purpose |
|---|---:|---|
| [`AERO_SIMULATION_REPORT.txt`](AERO_SIMULATION_REPORT.txt) | TXT | Documentation, assumptions, guide, or report: aero simulation report. |
| [`downforce_breakdown_300kph.csv`](downforce_breakdown_300kph.csv) | CSV | Structured data or manifest table: downforce breakdown 300kph. |
| [`downforce_chart.svg`](downforce_chart.svg) | SVG | Scalable vector presentation graphic or chart: downforce chart. |
| [`downforce_estimate.csv`](downforce_estimate.csv) | CSV | Structured data or manifest table: downforce estimate. |

## Limitations

Not CFD or wind-tunnel validation. Reported uncertainty is at least ±25% and excludes coupled vehicle behavior.

Return to the [repository version history](../../VERSIONS.md).

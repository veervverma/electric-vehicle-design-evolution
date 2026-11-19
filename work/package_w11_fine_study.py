from pathlib import Path
import json,zipfile,shutil,hashlib,math
root=Path(__file__).resolve().parents[1];out=root/'outputs/W11_2D_FINE_GRID_RE1K'
coarse=json.loads((out/'CHECK_coarse.json').read_text());fine=json.loads((out/'CHECK_fine.json').read_text())
assert abs(coarse['re']-fine['re'])<1e-6
assert abs(coarse['flowTimes']-fine['flowTimes'])<0.002
comparison={
 'simulated_Re':fine['re'],'coarse_grid':coarse['grid'],'fine_grid':fine['grid'],
 'coarse_flow_times':coarse['flowTimes'],'fine_flow_times':fine['flowTimes'],
 'coarse_mean_wake_speed_ratio':coarse['wake']['meanSpeedRatio'],'fine_mean_wake_speed_ratio':fine['wake']['meanSpeedRatio'],
 'coarse_reverse_flow_fraction':coarse['wake']['reverseFlowFraction'],'fine_reverse_flow_fraction':fine['wake']['reverseFlowFraction'],
 'wake_speed_relative_change_percent':abs(fine['wake']['meanSpeedRatio']-coarse['wake']['meanSpeedRatio'])/abs(fine['wake']['meanSpeedRatio'])*100,
 'reverse_fraction_change_percentage_points':100*(fine['wake']['reverseFlowFraction']-coarse['wake']['reverseFlowFraction']),
 'grid_independence_established':False,
 'physical_validation_performed':False,
 'reason':'Only two raster grids and one convective time. No settled wake statistics, systematic wall refinement, domain study or experimental correlation.'
}
(out/'GRID_SENSITIVITY.json').write_text(json.dumps(comparison,indent=2)+'\n')
length=json.loads((out/'w11-side-mask-960.json').read_text())['car_length_m'];fullRe=(300/3.6)*length/(1.7894e-5/1.225)
report=f"""# Fine-grid W11 numerical check

Default simulated Reynolds number: **{fine['re']:.0f}**. Full-scale reference at 300 km/h: **{fullRe:,.0f}** (car length {length:.6f} m). These conditions are not matched.

| Check | Coarse | Fine |
|---|---:|---:|
| Grid | {coarse['grid']} | {fine['grid']} |
| Cells | {math.prod(coarse['grid']):,} | {math.prod(fine['grid']):,} |
| Simulated Re | {coarse['re']:.0f} | {fine['re']:.0f} |
| Convective car-length times | {coarse['flowTimes']:.6f} | {fine['flowTimes']:.6f} |
| Numerical viscosity (lattice units) | {coarse['nu']:.8f} | {fine['nu']:.8f} |
| Final maximum lattice Mach | {coarse['maxMach']:.4f} | {fine['maxMach']:.4f} |
| Final maximum density deviation | {100*coarse['maxRhoError']:.3f}% | {100*fine['maxRhoError']:.3f}% |
| Wake mean speed / inlet speed | {coarse['wake']['meanSpeedRatio']:.4f} | {fine['wake']['meanSpeedRatio']:.4f} |
| Wake cells with reverse streamwise flow | {100*coarse['wake']['reverseFlowFraction']:.2f}% | {100*fine['wake']['reverseFlowFraction']:.2f}% |

The final maximum values above describe a snapshot, not the maximum over the entire startup. Early acoustic startup transients produce larger deviations. Complete sampled histories are retained in the JSON checks.

Wake mean-speed difference: **{comparison['wake_speed_relative_change_percent']:.2f}%** relative to the fine-grid snapshot. Reverse-flow fraction differs by **{comparison['reverse_fraction_change_percentage_points']:.2f} percentage points**.

These are diagnostic early-transient differences, not an accuracy percentage or proof of grid independence. Both runs span only one car-length convective time. Reverse flow is recirculation evidence within this numerical model; it is not proof of turbulent shedding or accurate W11 vortices.

The ultra grid and high-Re endpoint have shorter stability checks documented separately in PARAMETER_SMOKE_CHECKS.json. The ultra grid has not been compared at the same convective age.

## What passed
- Uniform empty-domain flow preservation.
- Re arithmetic and grid-consistent viscosity.
- Zero stored velocity inside solid obstacle cells.
- Finite calculations within the stated Mach/density screening bounds for the recorded runs.
- No artificial vortex forcing.

## What remains unverified
Full-scale Reynolds similarity, settled wake statistics, grid independence, boundary/domain sensitivity, 3D turbulence, accurate force coefficients, physical wind-tunnel correlation.

The numerical update improves the reduced-Re browser experiment; it does not complete the full-scale aerodynamic validation requested earlier.
"""
(out/'NUMERICAL_CHECK_REPORT.md').write_text(report)
for n in ['side-flow.html','side-flow.css','side-flow.js','side-flow-worker.js']:
 shutil.copy2(root/'docs'/n,out/n);shutil.copy2(root/'docs'/n,root/'work/fine-flow/docs'/n)
for n in ['lab-view-switch.js']:
 shutil.copy2(root/'docs'/n,root/'work/fine-flow/docs'/n)
for n in [480,960,1440]:
 shutil.copy2(root/f'docs/w11-side-mask-{n}.json',root/f'work/fine-flow/docs/w11-side-mask-{n}.json')
files=[p for p in out.iterdir() if p.is_file() and p.suffix!='.zip' and p.name!='MANIFEST.json']
manifest=[dict(path=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(files)]
(out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
with zipfile.ZipFile(out/'W11_FINE_GRID_REYNOLDS_STUDY.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in out.iterdir():
  if p.is_file() and p.suffix!='.zip':z.write(p,p.name)
print(json.dumps(comparison,indent=2))

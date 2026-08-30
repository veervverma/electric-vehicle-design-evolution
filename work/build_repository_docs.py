#!/usr/bin/env python3
"""Regenerate version READMEs, file manifests, and the GitHub Pages model catalog."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"

FOLDERS = {
    "ev_chassis_model": {
        "title": "Early EV chassis and sedan visual studies",
        "summary": "Rendered concept images documenting the transition from a bare skateboard chassis to an assembled sedan package.",
        "units": "Images only; no printable geometry is stored in this folder.",
        "use": "Use the isometric, side, rear, top, underbody, assembled, and exploded PNGs as visual development evidence.",
        "limit": "These are presentation renders rather than manufacturing or simulation files.",
    },
    "advanced_ev_sedan": {
        "title": "Advanced EV sedan V1",
        "summary": "First modular printable fastback sedan with separate structural, body, wheel, suspension, and retaining components.",
        "units": "Model dimensions are intended as millimeters. Prefer the 3MF print plate when available because 3MF records units.",
        "use": "Start with `advanced_ev_sedan_print_plate.3mf` for printing or `advanced_sedan_assembled_reference.stl` for inspection.",
        "limit": "Educational display model; test fit all moving or retained interfaces before a complete print.",
    },
    "advanced_ev_sedan_v2": {
        "title": "Advanced EV sedan V2",
        "summary": "More detailed modular sedan with monocoque, fastback cabin, removable vented hood, interior, swan-neck wing, steering/suspension, wheels, brakes, lights, mirrors, battery tray, and 130-size motor cradle.",
        "units": "Millimeters. The assembled envelope is approximately 195 × 105 × 70 mm.",
        "use": "Use `advanced_ev_sedan_v2_WHITE_FIXED.3mf` for the corrected white viewer/print project, the kit 3MF for separate objects, and the assembled STL as a reference.",
        "limit": "The motor-to-wheel drivetrain remains a custom engineering step; this is not a road-safe or validated RC-car design.",
    },
    "portfolio_ev_sedan_v3": {
        "title": "Portfolio EV sedan V3",
        "summary": "College-portfolio system model combining exterior design, skateboard battery packaging, rear e-axle motor and reduction gearbox, inverter, charging unit, suspension, brakes, interior, and exploded technical communication.",
        "units": "Millimeters for STL and 3MF geometry.",
        "use": "Open `EV_SEDAN_V3_ASSEMBLED_SHOWCASE.3mf` for the color-coded assembly and `EV_SEDAN_V3_EXPLODED_TECHNICAL.3mf` for system explanation.",
        "limit": "Educational scale prototype. Powered operation requires independent tolerance, thermal, electrical, and structural engineering.",
    },
    "formula_ev_prototype": {
        "title": "Formula EV prototype / V1",
        "summary": "First complete open-wheel Formula EV study with monocoque, detachable nose, ground-effect floor, sidepods, wings, halo, cockpit, pushrod-style suspension, wheels, battery, motor/gearbox, and inverter.",
        "units": "Millimeters. Approximate assembled envelope: 210 × 153 × 65 mm.",
        "use": "Use `FORMULA_EV_DETAILED_VIEWER.glb` for browser inspection, the assembled STL/3MF for reference, and numbered STLs for modular printing.",
        "limit": "The assembled STL is static; use the separate wheel parts when rotation or multi-material printing is required.",
    },
    "formula_ev_v2_detailed": {
        "title": "Formula EV V2 — detailed GLB and rear DRS",
        "summary": "Detailed presentation release with named mechanical and aerodynamic systems, individual GLBs, and an animated 28-degree rear DRS flap.",
        "units": "GLB is unit-aware for viewing; treat scale as an educational model rather than fabrication authority.",
        "use": "Start with `FORMULA_EV_V2_COMPLETE_ANIMATED_DRS.glb`; numbered files isolate each major system.",
        "limit": "Some viewers do not play glTF animation tracks; Blender or the included GitHub Pages viewer is recommended.",
    },
    "formula_ev_v3_2022_2025_floor": {
        "title": "Formula EV V3 — 2022–2025-inspired floor study",
        "summary": "Original educational ground-effect interpretation adding twin Venturi paths, inlet fences, floor-edge structures, plank and skids, bib, multi-stage diffuser, strakes, keel, and wake fences.",
        "units": "Presentation GLBs; use the full-scale V6 folder for later CFD-preparation units and the print folders for explicit print scale.",
        "use": "Compare the complete car, assembled underfloor, and exploded underfloor GLBs; numbered GLBs isolate every floor element.",
        "limit": "Not a scan or exact copy of a team car and not a validated CFD surface.",
    },
    "formula_ev_v4_dual_active_aero": {
        "title": "Formula EV V4 — dual active aero",
        "summary": "Adds left and right active front flaps and an actuator while retaining the separately animated rear DRS system.",
        "units": "Presentation GLBs; not a fabrication release.",
        "use": "Use `FORMULA_EV_V4_COMPLETE_DUAL_ACTIVE_AERO.glb` for the whole car and `FORMULA_EV_V4_FRONT_ACTIVE_AERO_SYSTEM.glb` to isolate the front mechanism.",
        "limit": "Conceptual active front aero, not a regulation-compliant 2022–2025 Formula 1 system.",
    },
    "formula_ev_v5_all_active_flaps": {
        "title": "Formula EV V5 — six active front flaps and synchronized assembly",
        "summary": "Final V5 presentation release with a fixed mainplane, six moving front flaps, rear DRS, named components, whole-car animation fix, and complete 55-part 3MF kits.",
        "units": "GLB for viewing; 3MF print projects use millimeter-scale objects. Read the print guide before arranging plates.",
        "use": "Prefer `FORMULA_EV_V5_COMPLETE_SYNCED_AERO_FIXED.glb` for the final whole-car animation and the `55_PARTS.3mf` kit for printing.",
        "limit": "The print kit exceeds one 220 × 220 mm plate and must be distributed across multiple plates; active mechanisms require practical hinge/clearance development.",
    },
    "FORMULA_EV_V5_PRINT_PARTS": {
        "title": "Formula EV V5 — separate 55-part STL print release",
        "summary": "Every V5 physical part exported separately for slicing, material assignment, selective reprinting, and assembly planning.",
        "units": "Millimeters. Confirm scale on import because STL itself does not record units.",
        "use": "Use `PARTS_AND_MATERIALS.csv` as the authoritative quantity/material list and the numbered files as individual print jobs.",
        "limit": "Test-fit joints and use suitable rods/fasteners for practical moving mechanisms; this is an educational print kit.",
    },
    "aero_estimate_v5": {
        "title": "Formula EV V5 — first-order aerodynamic estimate",
        "summary": "Equation-based force estimate using assumed effective ClA/CdA values, including downforce at speed and a component breakdown.",
        "units": "SI units in the CSV and report: m/s, kN, kgf equivalents, square meters, and kW as labeled.",
        "use": "Read `AERO_SIMULATION_REPORT.txt`, inspect the source CSV tables, and use the SVG chart for presentation.",
        "limit": "Not CFD or wind-tunnel validation. Reported uncertainty is at least ±25% and excludes coupled vehicle behavior.",
    },
    "v5_track_setups_spa_silverstone_monaco": {
        "title": "Formula EV V5 — Spa, Silverstone, and Monaco setup study",
        "summary": "Track-specific conceptual setup changes and downforce points for three circuits with different speed and load requirements.",
        "units": "SI units and degrees as labeled in the report and CSV files.",
        "use": "Use the report for narrative and the two CSV files for setup parameters and track-specific downforce data.",
        "limit": "Starting hypotheses only; not a seven-post, driver-in-loop, tire, energy, or validated track model.",
    },
    "v5_wind_tunnel_and_track_sim": {
        "title": "Formula EV V5 — wind-tunnel animation and reduced-order track study",
        "summary": "Presentation airflow/underfloor animation plus conceptual qualifying, race-fastest, and race-pace estimates across a 22-round calendar study.",
        "units": "Times and assumptions are labeled in the CSV/report; GLB is a visual presentation asset.",
        "use": "Open `V5_VENTURI_WIND_TUNNEL_ANIMATION.glb` in the browser gallery and use the CSV/SVG/report for lap-study documentation.",
        "limit": "No solved pressure field or full vehicle-dynamics model. Typical stated uncertainty is about ±2.5% qualifying and ±4% race pace, with additional uncertainty for new circuits.",
    },
    "V6_CFD_REBUILD": {
        "title": "Formula EV V6 — full-scale CFD-preparation rebuild",
        "summary": "Separate parametric V6 geometry pipeline with 20 named aerodynamic/mechanical surface groups, full-scale preview, part manifest, and a prepared 300 km/h OpenFOAM case.",
        "units": "Top-level and `geometry/` STL files are millimeters; OpenFOAM `triSurface` copies are meters. Combined model length is approximately 5,450 mm.",
        "use": "Use `V6_FULL_SCALE_CFD_PREVIEW.glb` for viewing, `geometry/` for separated surfaces, and `OpenFOAM_83ms/` as the unsolved CFD starting case.",
        "limit": "CFD preparation only. Components were not production-booleaned, and surface checks, meshing, solver runs, mesh independence, and experimental correlation were not completed.",
    },
    "V6_PRINT_READY_5_TO_8_INCH": {
        "title": "Formula EV V6 — repaired 5-inch and 8-inch print release",
        "summary": "Consumer-printer derivatives created after the full-scale V6 CFD STL proved too large and topologically unsuitable for slicing. Models were repaired, reinforced, scaled, voxel-solidified, and audited.",
        "units": "Millimeters. 5-inch length ≈127 mm; 8-inch length =203.2 mm. Prefer 3MF because it explicitly stores millimeter units.",
        "use": "Use the `PRINT_READY_SOLID_MM` 3MF or STL files. The 8-inch version preserves stronger details; the 5-inch version fits smaller beds.",
        "limit": "One-piece static display derivatives. Active flaps do not move, and small details remain challenging on a typical 0.4 mm FDM nozzle.",
    },
    "W11_V6_HYBRID_STATIC_8IN": {
        "title": "W11 reference / V6 — static 8-inch printable hybrid",
        "summary": "Static final-form study combining the supplied high-detail 2020 Mercedes-style exterior reference with a newly built twin-Venturi floor, structural EV chassis, low energy store, rear motor/gearbox, inverter, suspension, and rolling-wheel print hardware.",
        "units": "Printable STL geometry is millimeters; the complete 3MF explicitly declares millimeters. Overall printable assembly length is exactly 203.2 mm / 8.00 inches.",
        "use": "Start with `W11_REFERENCE_V6_SYSTEMS_ASSEMBLED.glb` for the detailed exterior, `W11_REFERENCE_V6_SYSTEMS_EXPLODED.glb` for the chassis/floor reveal, and `W11_V6_ALL_PRINT_PARTS_220MM_PLATE.3mf` for printing.",
        "limit": "Static educational display design. The exterior source is a rendering mesh and the printable body is a strengthened procedural derivative; the floor is V6-inspired but not validated CFD or structural engineering.",
        "preserve_readme": True,
    },
    "W11_2020_RESEARCH_REBUILD_STATIC_8IN": {
        "title": "W11 2020 — open-source research rebuild, static 8-inch print model",
        "summary": "Historically corrected release based on the FIA 2020 floor rules, Mercedes' published chassis specification, and contemporary W11 technical analysis. Replaces the inaccurate 2022-style tunnel floor with a flat reference/step-plane floor, plank, bargeboards, rear-tyre vanes and short diffuser, plus a carbon-honeycomb monocoque and W11-inspired suspension.",
        "units": "Printable STL geometry is millimeters; the complete 3MF explicitly declares millimeters. Overall printable assembly length is exactly 203.2 mm / 8.00 inches.",
        "use": "Open `W11_2020_REFERENCE_RESEARCH_ASSEMBLED.glb` for the detailed corrected car, `W11_2020_REFERENCE_RESEARCH_EXPLODED.glb` for the system reveal, and `W11_2020_ALL_PRINT_PARTS_220MM_PLATE.3mf` for the 29-piece print kit.",
        "limit": "Publicly documented architecture, not proprietary Mercedes CAD. Hidden bulkheads, laminates, ducts and exact pickup coordinates are informed approximations; legal-scale details are thickened for FDM.",
        "preserve_readme": True,
    },
    "W11_2020_AERO_CFD_VALIDATION_300KPH": {
        "title": "W11 2020 — 300 km/h aerodynamic visualization and SU2 CFD screening",
        "summary": "Rerun aerodynamic package for the public-reference-based W11 study: animated whole-car airflow presentation, transparent equation estimate, full-scale half-car SU2 meshes, four solved RANS/SST cases, ParaView output, force histories, grid sensitivity, and validation-status reporting.",
        "units": "CFD geometry and fields use SI units (metres, seconds, kilograms). The airflow GLB is a presentation model; the printable W11 release remains millimetre-scale.",
        "use": "Read `CFD_VALIDATION_REPORT.md`, inspect the animated GLB in the browser gallery, review the solved PNG/VTU fields, and use `RUN_CFD.md` with the supplied SU2 cases to reproduce or improve the study.",
        "limit": "CFD screening and numerical verification only. The geometry is a de-featured public-information surrogate; the medium moving-ground run did not pass the force-Cauchy target, grid independence was not achieved, and no rolling-road wind-tunnel correlation was performed.",
        "preserve_readme": True,
    },
    "W11_2020_GLBDERIVED_CFD_V2_300KPH": {
        "title": "W11 2020 — source-GLB-derived full-car CFD correction",
        "summary": "Corrective aerodynamic release replacing the earlier boxy primitive surrogate with a single watertight full-car shell derived directly from the supplied textured W11 GLB, a full-domain SU2 screening case, and continuous streamlines integrated from the solved velocity field.",
        "units": "CFD geometry, mesh and fields use SI units (metres, seconds, kilograms). The exact source GLB retains its original presentation transform; this release is not a printable-scale model.",
        "use": "Start with `W11_SOURCE_WITH_SOLVER_DERIVED_CONTINUOUS_AIRFLOW.glb`, compare the source and CFD shell in `W11_SOURCE_TO_CFD_SURFACE_OVERLAY.glb`, and read `CORRECTION_AND_CFD_REPORT.md` before interpreting the force history.",
        "limit": "Source-faithful public rendering geometry, not proprietary Mercedes CAD. The SU2 result is screening-only: stationary unified tyre envelopes, no cooling, no prism-layer/y+ study, no demonstrated mesh independence, and no rolling-road wind-tunnel correlation.",
        "preserve_readme": True,
    },
    "W11_2020_GLBDERIVED_PRINT_READY_8IN": {
        "title": "W11 2020 — source-derived exact 8-inch print release and CFD airflow points",
        "summary": "Printer-strengthened derivative of the corrected W11 GLB-derived aerodynamic shell, including an exact 203.2 mm one-piece model, a three-section alternative, millimeter-aware 3MF projects, and a digital CFD airflow-point view emphasizing front-wing-to-diffuser paths.",
        "units": "All STL and 3MF print geometry is millimeter-scale. The complete car is exactly 203.2 mm / 8.000 inches long; the 3MF files explicitly declare millimeters.",
        "use": "Use `W11_8IN_ONE_PIECE_PRINT_READY_MM.3mf` for the lowest-assembly-cost one-object print, `W11_8IN_THREE_SECTION_PRINT_PLATE_MM.3mf` to reduce support risk, and `W11_8IN_CFD_AIRFLOW_POINTS_FRONTWING_TO_DIFFUSER.glb` for the airflow presentation.",
        "limit": "Static display model. The airflow points are solver-derived digital markers and are deliberately not fused into the printable car. The underlying CFD field remains unconverged screening rather than validated W11 performance.",
        "preserve_readme": True,
    },
}

FAMILY_ORDER = {name: i for i, name in enumerate(FOLDERS)}


def human(stem: str) -> str:
    text = stem.replace("_", " ").replace("-", " ")
    return " ".join(text.split()).strip()


def describe(path: Path) -> str:
    name = path.stem.lower()
    ext = path.suffix.lower()
    label = human(path.stem)
    if ext == ".glb":
        base = "Browser-viewable binary glTF model"
        if "complete" in name or "assembled" in name: base += " of the complete assembly"
        elif "exploded" in name: base += " in an exploded technical layout"
        elif "underfloor" in name: base += " focused on the underfloor system"
        elif "wind_tunnel" in name: base += " containing the conceptual airflow presentation"
        elif "airflow_presentation" in name: base += " containing the explanatory airflow presentation"
        else: base += f" for the {label.lower()} component/system"
        if any(k in name for k in ("animated", "active", "drs", "synced", "wind_tunnel")): base += "; may contain animation"
        return base + "."
    if ext == ".stl":
        if "print_ready_solid" in name: return "Validated manifold STL prepared for FDM slicing; import as millimeters."
        if "smooth_repaired" in name: return "Smoother repaired reference STL retaining intersecting CFD-derived shells; solid version is preferred for slicing."
        if "assembled" in name or "complete" in name or "surfaces" in name: return "Combined triangle-mesh reference of the complete design; read this folder's unit and print limitations."
        return f"Separate triangle-mesh part for {label.lower()}; STL does not store units."
    if ext == ".3mf":
        if "compatibility" in name: return "Compatibility 3MF with simplified material handling for slicers that reject richer assignments."
        if "exploded" in name: return "3MF presentation project with systems arranged in an exploded technical layout."
        if "showcase" in name or "white" in name or "color" in name: return "Color/material presentation 3MF for assembled viewing and slicer import."
        return "3MF print project preserving object structure and millimeter units where authored."
    if ext == ".png": return f"Rendered PNG view: {label.lower()}."
    if ext == ".svg": return f"Scalable vector presentation graphic or chart: {label.lower()}."
    if ext == ".csv": return f"Structured data or manifest table: {label.lower()}."
    if ext in (".txt", ".md"): return f"Documentation, assumptions, guide, or report: {label.lower()}."
    if ext == ".zip": return f"Convenience archive containing the {label.lower()} package."
    if ext == ".obj": return "Wavefront OBJ viewer geometry; use together with the matching MTL file."
    if ext == ".mtl": return "Wavefront material definition used by the matching OBJ viewer geometry."
    return f"Project support file: {label.lower()}."


def folder_files(folder: Path) -> list[Path]:
    return sorted(
        (p for p in folder.rglob("*") if p.is_file() and p.name not in {".DS_Store", "README.md"}),
        key=lambda p: str(p.relative_to(folder)).lower(),
    )


def write_folder_readmes() -> None:
    for name, meta in FOLDERS.items():
        folder = OUTPUTS / name
        if not folder.exists():
            continue
        if meta.get("preserve_readme") and (folder / "README.md").exists():
            continue
        rows = []
        for path in folder_files(folder):
            rel = path.relative_to(folder).as_posix()
            rows.append(f"| [`{rel}`]({rel.replace(' ', '%20')}) | {path.suffix.lstrip('.').upper() or 'FILE'} | {describe(path)} |")
        body = f"""# {meta['title']}

{meta['summary']}

## Recommended use

{meta['use']}

## Units

{meta['units']}

## Files

| File | Format | Purpose |
|---|---:|---|
{chr(10).join(rows)}

## Limitations

{meta['limit']}

Return to the [repository version history](../../VERSIONS.md).
"""
        (folder / "README.md").write_text(body, encoding="utf-8")


def model_label(path: Path) -> str:
    return human(path.stem).title().replace("Glb", "GLB").replace("Stl", "STL")


def model_catalog() -> list[dict[str, str]]:
    result = []
    for name in FOLDERS:
        folder = OUTPUTS / name
        if not folder.exists(): continue
        for path in folder.rglob("*"):
            ext = path.suffix.lower().lstrip(".")
            if path.is_file() and ext in {"glb", "stl"}:
                rel_root = path.relative_to(ROOT).as_posix()
                result.append({
                    "family": FOLDERS[name]["title"],
                    "label": model_label(path),
                    "path": "../" + rel_root,
                    "ext": ext,
                })
    def priority(item: dict[str, str]) -> tuple:
        label = item["label"].lower()
        major = 0 if any(k in label for k in ("complete", "assembled", "viewer", "full scale", "underfloor", "wind tunnel", "print ready")) else 1
        family_name = next((n for n, m in FOLDERS.items() if m["title"] == item["family"]), "")
        return FAMILY_ORDER.get(family_name, 999), major, label
    return sorted(result, key=priority)


def write_catalogs() -> None:
    models = model_catalog()
    (ROOT / "docs" / "models.json").write_text(json.dumps({"models": models}, indent=2), encoding="utf-8")

    major = [m for m in models if any(k in m["label"].lower() for k in ("complete", "assembled", "viewer", "full scale cfd preview", "underfloor", "wind tunnel", "airflow presentation", "print ready solid"))]
    lines = [
        "# Model catalog",
        "",
        "The GitHub Pages gallery reads `docs/models.json` and can display every GLB and STL below the `outputs/` tree. This shorter table highlights assembled models and major study views. Click an STL in the GitHub repository for GitHub's native 3D viewer, or use the Pages gallery for searchable GLB/STL viewing and glTF animation playback.",
        "",
        "| Design family | Model | Format | Purpose |",
        "|---|---|---:|---|",
    ]
    for m in major:
        rel = m["path"].removeprefix("../")
        lines.append(f"| {m['family']} | [`{Path(rel).name}`]({rel.replace(' ', '%20')}) | {m['ext'].upper()} | {describe(ROOT / rel)} |")
    lines += ["", f"The interactive catalog currently indexes **{len(models)}** GLB/STL files.", ""]
    (ROOT / "MODEL_CATALOG.md").write_text("\n".join(lines), encoding="utf-8")


def ignored(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return (
        "/.git/" in f"/{rel}/"
        or path.name == ".DS_Store"
        or "__pycache__" in path.parts
        or path.suffix == ".pyc"
        or rel.startswith("outputs/V6_PRINT_READY_5_TO_8_INCH 2/")
        or rel == "FILE_MANIFEST.csv"
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest() -> None:
    paths = sorted((p for p in ROOT.rglob("*") if p.is_file() and not ignored(p)), key=lambda p: p.relative_to(ROOT).as_posix())
    with (ROOT / "FILE_MANIFEST.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["path", "bytes", "format", "sha256"])
        for path in paths:
            writer.writerow([path.relative_to(ROOT).as_posix(), path.stat().st_size, path.suffix.lower().lstrip(".") or "file", sha256(path)])


def main() -> None:
    write_folder_readmes()
    write_catalogs()
    write_manifest()
    print(f"Documented {len(FOLDERS)} output folders and {len(model_catalog())} viewable GLB/STL files.")


if __name__ == "__main__":
    main()

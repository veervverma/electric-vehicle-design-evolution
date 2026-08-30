#!/usr/bin/env python3
"""Build exact-8-inch one-piece and three-section W11 GLB-derived print files."""

from __future__ import annotations

import json
import math
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from scipy import ndimage
import trimesh
from trimesh.voxel import ops
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "outputs" / "W11_2020_GLBDERIVED_CFD_V2_300KPH"
SOURCE_STL = SOURCE_DIR / "W11_2020_GLBDERIVED_CFD_SURFACE.stl"
STREAMLINES = SOURCE_DIR / "CFD_RESULTS" / "SOLVER_DERIVED_STREAMLINES.json"
OUT = ROOT / "outputs" / "W11_2020_GLBDERIVED_PRINT_READY_8IN"
PARTS = OUT / "THREE_SECTION_OPTION"
TARGET_LENGTH_MM = 203.2
VOXEL_PITCH_MM = 0.40


def centered_on_bed(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    result = mesh.copy()
    lo, hi = result.bounds
    result.apply_translation((-lo[0], -(lo[1] + hi[1]) / 2.0, -lo[2]))
    return result


def build_reinforced() -> tuple[trimesh.Trimesh, dict]:
    full = trimesh.load(SOURCE_STL, force="mesh", process=True)
    source_bounds = full.bounds.copy()
    scale = TARGET_LENGTH_MM / float(np.ptp(full.bounds[:, 0]))
    full.apply_scale(scale)
    full = centered_on_bed(full)

    # Solidify on a printer-scale grid and expand by one cell. This keeps the
    # aerodynamic envelope while reinforcing wing edges and fragile junctions.
    vg = full.voxelized(VOXEL_PITCH_MM, method="subdivide").fill()
    pad = 2
    matrix = np.pad(vg.matrix.copy(), pad, mode="constant")
    matrix = ndimage.binary_dilation(matrix, iterations=1)
    matrix = ndimage.binary_closing(matrix, iterations=1)
    matrix = ndimage.binary_fill_holes(matrix)
    solid = ops.matrix_to_marching_cubes(matrix, pitch=VOXEL_PITCH_MM)
    solid.apply_translation(vg.transform[:3, 3] - pad * VOXEL_PITCH_MM)
    solid.remove_unreferenced_vertices()
    solid.fix_normals()
    # Dilation adds a fraction of a millimetre at each end; restore exact length.
    solid.apply_scale(TARGET_LENGTH_MM / float(np.ptp(solid.bounds[:, 0])))
    solid = centered_on_bed(solid)
    solid.visual.face_colors = [242, 242, 239, 255]
    return solid, {
        "source_bounds_m": source_bounds.tolist(),
        "source_to_initial_print_scale": scale,
        "voxel_pitch_mm": VOXEL_PITCH_MM,
        "reinforcement": "one printer-scale voxel outward dilation followed by closing and solidification",
    }


def cut_sections(mesh: trimesh.Trimesh) -> list[tuple[str, trimesh.Trimesh]]:
    # Split positions are percentages of the final length so regeneration remains stable.
    front_cut = TARGET_LENGTH_MM * 0.335
    rear_cut = TARGET_LENGTH_MM * 0.745
    front = trimesh.intersections.slice_mesh_plane(mesh, [-1, 0, 0], [front_cut, 0, 0], cap=True)
    middle = trimesh.intersections.slice_mesh_plane(mesh, [1, 0, 0], [front_cut, 0, 0], cap=True)
    middle = trimesh.intersections.slice_mesh_plane(middle, [-1, 0, 0], [rear_cut, 0, 0], cap=True)
    rear = trimesh.intersections.slice_mesh_plane(mesh, [1, 0, 0], [rear_cut, 0, 0], cap=True)
    result = []
    for name, part in (("01_FRONT_SECTION", front), ("02_CENTER_SECTION", middle), ("03_REAR_SECTION", rear)):
        part.remove_unreferenced_vertices(); part.fix_normals()
        result.append((name, centered_on_bed(part)))
    return result


def mesh_xml(mesh: trimesh.Trimesh) -> tuple[str, str]:
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    vs = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in vertices)
    fs = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in faces)
    return vs, fs


def write_3mf(path: Path, objects: list[tuple[str, trimesh.Trimesh, tuple[float, float, float]]], title: str):
    resources, build = [], []
    for oid, (name, mesh, translation) in enumerate(objects, 1):
        vertices, faces = mesh_xml(mesh)
        resources.append(
            f'<object id="{oid}" name="{escape(name)}" type="model"><mesh><vertices>{vertices}</vertices>'
            f'<triangles>{faces}</triangles></mesh></object>'
        )
        tx, ty, tz = translation
        build.append(f'<item objectid="{oid}" transform="1 0 0 0 1 0 0 0 1 {tx:.5f} {ty:.5f} {tz:.5f}"/>')
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
        f'<metadata name="Title">{escape(title)}</metadata>'
        '<metadata name="Description">Exact 203.2 mm W11-derived static display print; millimeter units.</metadata>'
        '<resources>' + "".join(resources) + '</resources><build>' + "".join(build) + '</build></model>'
    )
    rels = '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="r0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    content = '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("3D/3dmodel.model", model)
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"3MF verification failed: {path}")


def cylinder_between(a, b, radius, sections=7):
    a, b = np.asarray(a), np.asarray(b)
    delta = b - a; length = np.linalg.norm(delta)
    if length < 1e-5:
        return None
    cylinder = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    cylinder.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], delta))
    cylinder.apply_translation((a + b) / 2)
    return cylinder


def airflow_preview(car: trimesh.Trimesh, source_bounds_m: np.ndarray):
    data = json.loads(STREAMLINES.read_text())
    scale = TARGET_LENGTH_MM / float(np.ptp(source_bounds_m[:, 0]))
    offset = np.array([-source_bounds_m[0, 0], 0.0, -source_bounds_m[0, 2]])
    colors = {
        "whole_car": [45, 170, 225, 255],
        "underfloor": [55, 205, 120, 255],
        "front_wing_to_diffuser": [255, 92, 40, 255],
    }
    groups = {key: [] for key in colors}
    points = {key: [] for key in colors}
    for line in data["streamlines"]:
        region = line["region"]
        path = (np.asarray(line["points_m"]) + offset) * scale
        path[:, 1] -= (source_bounds_m[0, 1] + source_bounds_m[1, 1]) * 0.5 * scale
        path = path[::4] if len(path) > 4 else path
        for a, b in zip(path[:-1], path[1:]):
            tube = cylinder_between(a, b, 0.42 if region == "whole_car" else 0.58)
            if tube is not None: groups[region].append(tube)
        for point in path[::5]:
            sphere = trimesh.creation.icosphere(subdivisions=1, radius=0.85 if region == "whole_car" else 1.05)
            sphere.apply_translation(point); points[region].append(sphere)
    scene = trimesh.Scene()
    car_copy = car.copy(); car_copy.visual.face_colors = [242, 242, 239, 255]
    scene.add_geometry(car_copy, node_name="W11_8IN_PRINTABLE_CAR")
    for region, meshes in groups.items():
        if meshes:
            joined = trimesh.util.concatenate(meshes); joined.visual.face_colors = colors[region]
            scene.add_geometry(joined, node_name=f"CFD_CONTINUOUS_{region.upper()}")
        if points[region]:
            joined = trimesh.util.concatenate(points[region]); joined.visual.face_colors = colors[region]
            scene.add_geometry(joined, node_name=f"CFD_AIRFLOW_POINTS_{region.upper()}")
    scene.export(OUT / "W11_8IN_CFD_AIRFLOW_POINTS_FRONTWING_TO_DIFFUSER.glb")

    # Static QA/communication view with the front-wing-to-diffuser paths called out.
    sampled, _ = trimesh.sample.sample_surface(car, 45000)
    fig, axes = plt.subplots(2, 1, figsize=(13, 8.2))
    axes[0].scatter(sampled[:, 0], sampled[:, 2], s=0.16, c="#30353a", alpha=0.34)
    axes[1].scatter(sampled[:, 0], sampled[:, 1], s=0.16, c="#30353a", alpha=0.34)
    labels_used = set()
    labels = {"whole_car": "overall flow", "underfloor": "floor/diffuser seeds", "front_wing_to_diffuser": "front wing → diffuser"}
    line_colors = {"whole_car": "#39a9dc", "underfloor": "#39c77d", "front_wing_to_diffuser": "#ff4f25"}
    for line in data["streamlines"]:
        region = line["region"]
        path = (np.asarray(line["points_m"]) + offset) * scale
        path[:, 1] -= (source_bounds_m[0, 1] + source_bounds_m[1, 1]) * 0.5 * scale
        label = labels[region] if region not in labels_used else None
        labels_used.add(region)
        width = 1.8 if region == "front_wing_to_diffuser" else 0.9
        alpha = 0.95 if region == "front_wing_to_diffuser" else 0.62
        axes[0].plot(path[:, 0], path[:, 2], color=line_colors[region], lw=width, alpha=alpha, label=label)
        axes[1].plot(path[:, 0], path[:, 1], color=line_colors[region], lw=width, alpha=alpha)
        if region == "front_wing_to_diffuser":
            axes[0].scatter(path[::12, 0], path[::12, 2], s=11, c=line_colors[region], edgecolors="white", linewidths=0.25, zorder=5)
            axes[1].scatter(path[::12, 0], path[::12, 1], s=11, c=line_colors[region], edgecolors="white", linewidths=0.25, zorder=5)
    axes[0].set(title="Side view — solver-derived continuous airflow points", ylabel="Height (mm)")
    axes[1].set(title="Top view — front-wing paths emphasized through floor and diffuser", xlabel="Longitudinal position (mm)", ylabel="Lateral position (mm)")
    for axis in axes:
        axis.grid(alpha=0.18); axis.set_aspect("equal", adjustable="box")
    axes[0].legend(loc="upper right", ncol=3)
    fig.suptitle("W11 8-inch print model with CFD airflow paths", fontsize=18)
    fig.tight_layout(); fig.savefig(OUT / "W11_8IN_CFD_AIRFLOW_POINTS_PREVIEW.png", dpi=190); plt.close(fig)


def audit(mesh: trimesh.Trimesh):
    return {
        "vertices": int(len(mesh.vertices)), "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight), "winding_consistent": bool(mesh.is_winding_consistent),
        "connected_bodies": int(mesh.body_count), "positive_volume_mm3": float(mesh.volume),
        "dimensions_mm": np.ptp(mesh.bounds, axis=0).round(5).tolist(),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True); PARTS.mkdir(parents=True, exist_ok=True)
    one, metadata = build_reinforced()
    one.export(OUT / "W11_8IN_ONE_PIECE_PRINT_READY_MM.stl")
    one.export(OUT / "W11_8IN_ONE_PIECE_PRINT_READY_PREVIEW.glb")
    write_3mf(OUT / "W11_8IN_ONE_PIECE_PRINT_READY_MM.3mf", [("W11 8-inch one-piece car", one, ((220.0 - TARGET_LENGTH_MM) / 2.0, 110.0, 0))], "W11 8-inch one-piece print-ready car")

    sections = cut_sections(one)
    for name, mesh in sections:
        mesh.export(PARTS / f"{name}_PRINT_READY_MM.stl")
    # All three sections fit on one 220 mm plate in a single row.
    placements, x_cursor = [], 0.0
    for name, mesh in sections:
        placements.append((name, mesh, (x_cursor, 40.0, 0.0)))
        x_cursor += float(np.ptp(mesh.bounds[:, 0])) + 4.0
    write_3mf(OUT / "W11_8IN_THREE_SECTION_PRINT_PLATE_MM.3mf", placements, "W11 8-inch three-section print plate")
    airflow_preview(one, np.asarray(metadata["source_bounds_m"]))

    validation = {
        "target_length_mm": TARGET_LENGTH_MM,
        "target_length_in": 8.0,
        "one_piece": audit(one),
        "three_section_option": {name: audit(mesh) for name, mesh in sections},
        "bed_fit": {"one_piece_220x220": bool(np.ptp(one.bounds[:, 0]) <= 220 and np.ptp(one.bounds[:, 1]) <= 220), "three_section_plate_width_mm": x_cursor - 4.0},
        **metadata,
        "airflow_visualization": "solver-field-derived digital GLB; deliberately not fused into the printable car",
    }
    (OUT / "PRINT_VALIDATION.json").write_text(json.dumps(validation, indent=2) + "\n")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()

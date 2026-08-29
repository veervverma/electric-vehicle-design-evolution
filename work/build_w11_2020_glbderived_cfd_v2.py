#!/usr/bin/env python3
"""Build a watertight, full-car CFD surface from the supplied W11 GLB.

Unlike the earlier primitive surrogate, this workflow starts from the actual
reference triangles for the exterior, wings, floor, diffuser and tyres. A
20 mm full-scale voxel union resolves the rendering mesh's open/non-manifold
interfaces, marching cubes creates one watertight shell, and light Taubin
smoothing removes voxel stair-stepping. The optional Gmsh step places that
surface in a full-car moving-ground wind-tunnel domain for SU2.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path

import gmsh
import numpy as np
from scipy import ndimage
import trimesh
from trimesh import smoothing
from trimesh.voxel import ops

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "references" / "mercedec-f1-2020" / "mercedec-f1-2020.glb"
DEFAULT_OUT = ROOT / "outputs" / "W11_2020_GLBDERIVED_CFD_V2_300KPH"

# Exterior/body materials plus the four source tyres. Brake internals,
# steering-wheel/interior display materials and wheel-hub detail are excluded.
EXTERIOR_MATERIALS = (set(range(43)) - set(range(10, 20)) - set(range(29, 43))) | {14}


def glb_arrays(path: Path, selected: set[int]):
    raw = path.read_bytes()
    json_len = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20 : 20 + json_len])
    pos = 20 + json_len
    binary_len = struct.unpack_from("<I", raw, pos)[0]
    binary = raw[pos + 8 : pos + 8 + binary_len]
    component = {5120: ("b", 1), 5121: ("B", 1), 5122: ("h", 2), 5123: ("H", 2), 5125: ("I", 4), 5126: ("f", 4)}
    width = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}

    def accessor(index):
        item = doc["accessors"][index]
        view = doc["bufferViews"][item["bufferView"]]
        fmt, size = component[item["componentType"]]
        count = width[item["type"]]
        stride = view.get("byteStride", size * count)
        offset = view.get("byteOffset", 0) + item.get("byteOffset", 0)
        return np.asarray([struct.unpack_from("<" + fmt * count, binary, offset + row * stride) for row in range(item["count"])])

    vertices, faces, offset = [], [], 0
    for primitive in doc["meshes"][0]["primitives"]:
        if primitive["material"] not in selected:
            continue
        points = accessor(primitive["attributes"]["POSITION"]).astype(float)
        indices = accessor(primitive["indices"]).reshape(-1).astype(int).reshape(-1, 3)
        vertices.append(points)
        faces.append(indices + offset)
        offset += len(points)
    return np.vstack(vertices), np.vstack(faces)


def build_surface(source: Path, outdir: Path, pitch: float):
    vertices, faces = glb_arrays(source, EXTERIOR_MATERIALS)
    source_mesh = trimesh.Trimesh(vertices, faces, process=False)
    voxels = source_mesh.voxelized(pitch, method="subdivide")
    matrix = voxels.matrix.copy()
    # Join physical intersections, seal rendering gaps and solidify the outer
    # envelope. The exact source remains available in the overlay GLB.
    matrix = ndimage.binary_dilation(matrix, iterations=1)
    matrix = ndimage.binary_closing(matrix, iterations=2)
    matrix = ndimage.binary_fill_holes(matrix)
    shell = ops.matrix_to_marching_cubes(matrix, pitch=pitch)
    shell.apply_translation(voxels.transform[:3, 3])
    smoothing.filter_taubin(shell, lamb=0.18, nu=0.19, iterations=2)
    # Source coordinates: x=lateral, y=longitudinal, z=negative-up.
    # CFD coordinates: x=flow direction (front to rear), y=lateral, z=up.
    p = shell.vertices.copy()
    shell.vertices = np.column_stack((-p[:, 1], p[:, 0], -p[:, 2]))
    shell.fix_normals()
    outdir.mkdir(parents=True, exist_ok=True)
    stl = outdir / "W11_2020_GLBDERIVED_CFD_SURFACE.stl"
    glb = outdir / "W11_2020_GLBDERIVED_CFD_SURFACE.glb"
    shell.export(stl)
    shell.visual.face_colors = [225, 228, 232, 255]
    shell.export(glb)
    metadata = {
        "source": str(source.relative_to(ROOT)),
        "source_selected_triangles": int(len(faces)),
        "voxel_pitch_m": pitch,
        "surface_vertices": int(len(shell.vertices)),
        "surface_triangles": int(len(shell.faces)),
        "watertight": bool(shell.is_watertight),
        "winding_consistent": bool(shell.is_winding_consistent),
        "connected_components": int(len(shell.split(only_watertight=False))),
        "bounds_m": shell.bounds.tolist(),
        "method": "source triangle voxel union, morphological sealing, marching cubes, light Taubin smoothing",
    }
    (outdir / "SOURCE_DERIVATION_METADATA.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return stl, metadata


def build_mesh(surface: Path, output: Path):
    output.parent.mkdir(parents=True, exist_ok=True)
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.option.setNumber("General.NumThreads", 8)
    gmsh.model.add("w11_glbderived_full_car_domain")
    gmsh.merge(str(surface))
    car = gmsh.model.getEntities(2)[0][1]
    geo = gmsh.model.geo
    coords = [
        (-12, -6, 0), (18, -6, 0), (18, 6, 0), (-12, 6, 0),
        (-12, -6, 6), (18, -6, 6), (18, 6, 6), (-12, 6, 6),
    ]
    points = [geo.addPoint(*point, 1.2) for point in coords]
    line = lambda a, b: geo.addLine(points[a], points[b])
    edge = [line(0, 1), line(1, 2), line(2, 3), line(3, 0), line(4, 5), line(5, 6), line(6, 7), line(7, 4), line(0, 4), line(1, 5), line(2, 6), line(3, 7)]
    plane = lambda tags: geo.addPlaneSurface([geo.addCurveLoop(tags)])
    ground = plane([-edge[3], -edge[2], -edge[1], -edge[0]])
    top = plane([edge[4], edge[5], edge[6], edge[7]])
    inlet = plane([edge[8], -edge[7], -edge[11], edge[3]])
    outlet = plane([edge[1], edge[10], -edge[5], -edge[9]])
    side_a = plane([edge[0], edge[9], -edge[4], -edge[8]])
    side_b = plane([edge[11], -edge[6], -edge[10], edge[2]])
    outer = geo.addSurfaceLoop([ground, top, inlet, outlet, side_a, side_b])
    inner = geo.addSurfaceLoop([car])
    fluid = geo.addVolume([outer, inner])
    geo.synchronize()
    gmsh.model.addPhysicalGroup(3, [fluid], 1); gmsh.model.setPhysicalName(3, 1, "fluid")
    for tag, name, surfaces in [
        (10, "inlet", [inlet]), (11, "outlet", [outlet]), (12, "ground", [ground]),
        (13, "farfield", [top, side_a, side_b]), (20, "car", [car]),
    ]:
        gmsh.model.addPhysicalGroup(2, surfaces, tag); gmsh.model.setPhysicalName(2, tag, name)
    field = gmsh.model.mesh.field.add("Box")
    for name, value in [
        ("VIn", 0.18), ("VOut", 1.2), ("XMin", -3.6), ("XMax", 6.5),
        ("YMin", -2.2), ("YMax", 2.2), ("ZMin", 0), ("ZMax", 2.0),
    ]:
        gmsh.model.mesh.field.setNumber(field, name, value)
    gmsh.model.mesh.field.setAsBackgroundMesh(field)
    gmsh.option.setNumber("Mesh.MeshSizeMin", 0.025)
    gmsh.option.setNumber("Mesh.MeshSizeMax", 1.2)
    gmsh.option.setNumber("Mesh.Algorithm3D", 10)  # HXT
    gmsh.option.setNumber("Mesh.MaxNumThreads3D", 8)
    gmsh.option.setNumber("Mesh.Optimize", 0)
    gmsh.model.mesh.generate(3)
    gmsh.write(str(output))
    node_count = len(gmsh.model.mesh.getNodes()[0])
    tetrahedra = sum(len(tags) for tags in gmsh.model.mesh.getElements(3)[1])
    gmsh.finalize()
    metadata = {
        "mesh": output.name,
        "nodes": node_count,
        "tetrahedra_in_physical_fluid": tetrahedra,
        "domain_m": {"x": [-12, 18], "y": [-6, 6], "z": [0, 6]},
        "surface_source": surface.name,
        "mesher": "Gmsh HXT, optimization disabled after boundary recovery",
    }
    (output.parent / "MESH_METADATA.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--pitch", type=float, default=0.020)
    parser.add_argument("--surface-only", action="store_true")
    args = parser.parse_args()
    surface, surface_meta = build_surface(args.source, args.outdir, args.pitch)
    print(json.dumps(surface_meta, indent=2))
    if not args.surface_only:
        mesh = args.outdir / "CFD_CASE" / "W11_2020_GLBDERIVED_FULL_DOMAIN.su2"
        print(json.dumps(build_mesh(surface, mesh), indent=2))


if __name__ == "__main__":
    main()

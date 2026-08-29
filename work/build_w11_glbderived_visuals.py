#!/usr/bin/env python3
"""Add the source-derived CFD shell or solved streamlines to the supplied W11 GLB.

The source GLB keeps its original textures and geometry. Added CFD geometry is
stored under a node with the same orientation transform as the reference car.
Streamlines are continuous tubes integrated from the solved velocity field;
animated beads only communicate flow direction along those tubes.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path

import numpy as np
import trimesh


def read_glb(path: Path):
    raw = path.read_bytes()
    magic, version, total = struct.unpack_from("<4sII", raw, 0)
    if magic != b"glTF" or version != 2 or total != len(raw):
        raise ValueError(f"Invalid GLB: {path}")
    json_len, json_type = struct.unpack_from("<I4s", raw, 12)
    if json_type != b"JSON":
        raise ValueError("Missing JSON chunk")
    doc = json.loads(raw[20 : 20 + json_len])
    pos = 20 + json_len
    bin_len, bin_type = struct.unpack_from("<I4s", raw, pos)
    if bin_type != b"BIN\0":
        raise ValueError("Missing BIN chunk")
    return doc, bytearray(raw[pos + 8 : pos + 8 + bin_len])


def write_glb(path: Path, doc: dict, binary: bytearray):
    while len(binary) % 4:
        binary.append(0)
    doc["buffers"][0]["byteLength"] = len(binary)
    encoded = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    encoded += b" " * ((4 - len(encoded) % 4) % 4)
    total = 12 + 8 + len(encoded) + 8 + len(binary)
    with path.open("wb") as handle:
        handle.write(struct.pack("<4sII", b"glTF", 2, total))
        handle.write(struct.pack("<I4s", len(encoded), b"JSON"))
        handle.write(encoded)
        handle.write(struct.pack("<I4s", len(binary), b"BIN\0"))
        handle.write(binary)


class Appender:
    def __init__(self, doc: dict, binary: bytearray):
        self.doc, self.binary = doc, binary
        for key in ("bufferViews", "accessors", "meshes", "materials", "nodes"):
            doc.setdefault(key, [])

    def view(self, data: bytes, target: int | None = None):
        while len(self.binary) % 4:
            self.binary.append(0)
        offset = len(self.binary)
        self.binary.extend(data)
        item = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target:
            item["target"] = target
        self.doc["bufferViews"].append(item)
        return len(self.doc["bufferViews"]) - 1

    def accessor(self, view: int, component: int, count: int, kind: str, minimum=None, maximum=None):
        item = {"bufferView": view, "componentType": component, "count": count, "type": kind}
        if minimum is not None:
            item["min"] = np.asarray(minimum).astype(float).tolist()
        if maximum is not None:
            item["max"] = np.asarray(maximum).astype(float).tolist()
        self.doc["accessors"].append(item)
        return len(self.doc["accessors"]) - 1

    def material(self, name: str, rgba, emissive=None):
        item = {
            "name": name,
            "pbrMetallicRoughness": {
                "baseColorFactor": list(rgba),
                "metallicFactor": 0.05,
                "roughnessFactor": 0.35,
            },
            "doubleSided": True,
            "extensions": {"KHR_materials_unlit": {}},
        }
        if rgba[3] < 1:
            item["alphaMode"] = "BLEND"
        if emissive is not None:
            item["emissiveFactor"] = list(emissive)
        self.doc["materials"].append(item)
        if "KHR_materials_unlit" not in self.doc.setdefault("extensionsUsed", []):
            self.doc["extensionsUsed"].append("KHR_materials_unlit")
        return len(self.doc["materials"]) - 1

    def mesh(self, name: str, vertices, faces, material: int):
        vertices = np.asarray(vertices, dtype="<f4")
        faces = np.asarray(faces, dtype="<u4").reshape(-1)
        pv = self.view(vertices.tobytes(), 34962)
        iv = self.view(faces.tobytes(), 34963)
        pa = self.accessor(pv, 5126, len(vertices), "VEC3", vertices.min(axis=0), vertices.max(axis=0))
        ia = self.accessor(iv, 5125, len(faces), "SCALAR", [int(faces.min())], [int(faces.max())])
        self.doc["meshes"].append(
            {"name": name, "primitives": [{"attributes": {"POSITION": pa}, "indices": ia, "material": material}]}
        )
        return len(self.doc["meshes"]) - 1


def cfd_to_source(points):
    """CFD (longitudinal, lateral, up) -> source mesh coordinates."""
    p = np.asarray(points, dtype=float)
    return np.column_stack((p[:, 1], -p[:, 0], -p[:, 2]))


def tube(path, radius=0.009, sides=8):
    p = np.asarray(path, dtype=float)
    if len(p) < 2:
        raise ValueError("A tube needs at least two points")
    tangents = np.gradient(p, axis=0)
    tangents /= np.maximum(np.linalg.norm(tangents, axis=1, keepdims=True), 1e-12)
    rings = []
    normal = np.cross(tangents[0], [0.0, 0.0, 1.0])
    if np.linalg.norm(normal) < 0.2:
        normal = np.cross(tangents[0], [0.0, 1.0, 0.0])
    normal /= np.linalg.norm(normal)
    for point, tangent in zip(p, tangents):
        normal -= tangent * np.dot(normal, tangent)
        if np.linalg.norm(normal) < 1e-8:
            normal = np.cross(tangent, [0.0, 0.0, 1.0])
        normal /= np.linalg.norm(normal)
        binormal = np.cross(tangent, normal)
        rings.append(
            [point + radius * (math.cos(2 * math.pi * j / sides) * normal + math.sin(2 * math.pi * j / sides) * binormal) for j in range(sides)]
        )
    vertices = np.asarray(rings).reshape(-1, 3)
    faces = []
    for i in range(len(rings) - 1):
        for j in range(sides):
            k = (j + 1) % sides
            a, b, c, d = i * sides + j, i * sides + k, (i + 1) * sides + k, (i + 1) * sides + j
            faces.extend(((a, b, c), (a, c, d)))
    return vertices, np.asarray(faces)


def resample(path, count=80):
    path = np.asarray(path, dtype=float)
    distance = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    if distance[-1] <= 1e-9:
        return np.repeat(path[:1], count, axis=0)
    target = np.linspace(0.0, distance[-1], count)
    return np.column_stack([np.interp(target, distance, path[:, axis]) for axis in range(3)])


def add_parent(doc: dict, name: str):
    rotation = doc["nodes"][0].get("rotation", [0.0, 0.0, 0.0, 1.0])
    doc["nodes"].append({"name": name, "rotation": rotation, "children": []})
    parent = len(doc["nodes"]) - 1
    doc["scenes"][doc.get("scene", 0)].setdefault("nodes", []).append(parent)
    return parent


def add_overlay(source: Path, shell: Path, output: Path):
    doc, binary = read_glb(source)
    app = Appender(doc, binary)
    parent = add_parent(doc, "SOURCE-DERIVED CFD SURFACE OVERLAY")
    material = app.material("CFD shell — translucent cyan", (0.05, 0.75, 1.0, 0.33), (0.0, 0.20, 0.28))
    mesh = trimesh.load(shell, force="mesh", process=False)
    mesh_id = app.mesh("Watertight CFD surface derived from supplied W11 GLB", cfd_to_source(mesh.vertices), mesh.faces, material)
    doc["nodes"].append({"name": "CFD shell", "mesh": mesh_id})
    doc["nodes"][parent]["children"].append(len(doc["nodes"]) - 1)
    write_glb(output, doc, binary)


def add_streamlines(source: Path, streamline_json: Path, output: Path):
    data = json.loads(streamline_json.read_text())
    doc, binary = read_glb(source)
    app = Appender(doc, binary)
    parent = add_parent(doc, "SOLVER-INTEGRATED CONTINUOUS AIRFLOW")
    colors = [
        app.material("Low-speed solved flow", (0.05, 0.45, 1.0, 0.72), (0.0, 0.08, 0.35)),
        app.material("Freestream solved flow", (0.08, 0.95, 0.72, 0.72), (0.0, 0.28, 0.16)),
        app.material("Accelerated solved flow", (1.0, 0.55, 0.04, 0.78), (0.35, 0.10, 0.0)),
    ]
    pulse_material = app.material("Flow-direction pulses", (1.0, 1.0, 1.0, 0.95), (0.8, 0.8, 0.8))
    pulse = trimesh.creation.icosphere(subdivisions=1, radius=0.026)
    pulse_mesh = app.mesh("Flow pulse", pulse.vertices, pulse.faces, pulse_material)
    animated = []
    for index, line in enumerate(data["streamlines"]):
        cfd_path = np.asarray(line["points_m"], dtype=float)
        if len(cfd_path) < 4:
            continue
        source_path = cfd_to_source(cfd_path)
        speed = float(line["mean_speed_ratio"])
        category = 0 if speed < 0.72 else 2 if speed > 1.08 else 1
        vertices, faces = tube(source_path, radius=0.008 if line.get("region") != "underfloor" else 0.006)
        mesh_id = app.mesh(f"Solved streamline {index + 1}", vertices, faces, colors[category])
        doc["nodes"].append({"name": f"Continuous solved streamline {index + 1}", "mesh": mesh_id})
        doc["nodes"][parent]["children"].append(len(doc["nodes"]) - 1)
        sampled = resample(source_path, 80)
        doc["nodes"].append({"name": f"Direction pulse {index + 1}", "mesh": pulse_mesh, "translation": sampled[0].tolist()})
        node = len(doc["nodes"]) - 1
        doc["nodes"][parent]["children"].append(node)
        animated.append((node, sampled))
    times = np.linspace(0.0, 5.0, 80, dtype="<f4")
    tv = app.view(times.tobytes())
    ta = app.accessor(tv, 5126, len(times), "SCALAR", [0.0], [5.0])
    samplers, channels = [], []
    for node, sampled in animated:
        vv = app.view(np.asarray(sampled, dtype="<f4").tobytes())
        va = app.accessor(vv, 5126, len(sampled), "VEC3")
        samplers.append({"input": ta, "output": va, "interpolation": "LINEAR"})
        channels.append({"sampler": len(samplers) - 1, "target": {"node": node, "path": "translation"}})
    doc.setdefault("animations", []).append(
        {"name": "SOLVER-DERIVED CONTINUOUS AIRFLOW DIRECTION", "samplers": samplers, "channels": channels}
    )
    write_glb(output, doc, binary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--shell", type=Path)
    parser.add_argument("--streamlines", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.streamlines:
        add_streamlines(args.source, args.streamlines, args.output)
    elif args.shell:
        add_overlay(args.source, args.shell, args.output)
    else:
        parser.error("Supply --shell or --streamlines")
    print(args.output)


if __name__ == "__main__":
    main()

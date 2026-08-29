#!/usr/bin/env python3
"""Render source-vs-CFD silhouette and CFD-shell isometric QA figures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


def source_external_mesh(path: Path):
    raw = path.read_bytes()
    json_len = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20 : 20 + json_len])
    pos = 20 + json_len
    bin_len = struct.unpack_from("<I", raw, pos)[0]
    binary = raw[pos + 8 : pos + 8 + bin_len]
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

    selected = (set(range(43)) - set(range(10, 20)) - set(range(29, 43))) | {14}
    vertices, faces, offset = [], [], 0
    for primitive in doc["meshes"][0]["primitives"]:
        if primitive["material"] not in selected:
            continue
        points = accessor(primitive["attributes"]["POSITION"]).astype(float)
        indices = accessor(primitive["indices"]).reshape(-1).astype(int).reshape(-1, 3)
        vertices.append(points)
        faces.append(indices + offset)
        offset += len(points)
    mesh = trimesh.Trimesh(np.vstack(vertices), np.vstack(faces), process=False)
    p = mesh.vertices.copy()
    mesh.vertices = np.column_stack((-p[:, 1], p[:, 0], -p[:, 2]))
    return mesh


def sampled_polygons(mesh, axes, limit, seed=12):
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(mesh.faces), min(limit, len(mesh.faces)), replace=False)
    return mesh.vertices[mesh.faces[pick]][:, :, axes]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--shell", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    source = source_external_mesh(args.source)
    shell = trimesh.load(args.shell, force="mesh", process=False)
    # Decimation is used only for raster rendering; the exported CFD shell is
    # unchanged and remains the full 260k-triangle watertight mesh.
    source_render = source.simplify_quadric_decimation(face_count=min(80000, len(source.faces)), aggression=5)
    shell_render = shell.simplify_quadric_decimation(face_count=min(90000, len(shell.faces)), aggression=5)

    fig, axes = plt.subplots(2, 1, figsize=(12, 7.4))
    for ax, dims, labels, title in [
        (axes[0], [0, 2], ("Longitudinal x (m)", "Height z (m)"), "Side silhouette"),
        (axes[1], [0, 1], ("Longitudinal x (m)", "Lateral y (m)"), "Top silhouette"),
    ]:
        ax.add_collection(PolyCollection(sampled_polygons(shell_render, dims, len(shell_render.faces), 14), facecolor="#22c6e8", edgecolor="none", alpha=0.50, label="Watertight CFD shell"))
        ax.add_collection(PolyCollection(sampled_polygons(source_render, dims, len(source_render.faces)), facecolor="#20252b", edgecolor="none", alpha=0.48, label="Supplied W11 GLB"))
        all_points = np.vstack((source.vertices[:, dims], shell.vertices[:, dims]))
        ax.set_xlim(all_points[:, 0].min() - 0.15, all_points[:, 0].max() + 0.15)
        ax.set_ylim(all_points[:, 1].min() - 0.08, all_points[:, 1].max() + 0.08)
        ax.set_aspect("equal")
        ax.set_xlabel(labels[0]); ax.set_ylabel(labels[1]); ax.set_title(title)
        ax.grid(alpha=0.18); ax.legend(loc="upper right")
    fig.suptitle("Supplied W11 rendering mesh vs source-derived CFD surface", fontsize=16)
    fig.tight_layout()
    fig.savefig(args.outdir / "SOURCE_VS_CFD_SILHOUETTE.png", dpi=190)
    plt.close(fig)

    tris = shell_render.vertices[shell_render.faces]
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
    light = np.clip(0.30 + 0.70 * np.abs(normals @ np.array([0.35, -0.55, 0.76])), 0, 1)
    colors = np.column_stack((0.20 + 0.52 * light, 0.24 + 0.52 * light, 0.30 + 0.55 * light, np.ones(len(light))))
    fig = plt.figure(figsize=(12, 7.5))
    ax = fig.add_subplot(111, projection="3d")
    ax.add_collection3d(Poly3DCollection(tris, facecolors=colors, edgecolors="none"))
    bounds = shell.bounds
    margin = np.array([0.15, 0.12, 0.08])
    ax.set_xlim(bounds[0, 0] - margin[0], bounds[1, 0] + margin[0])
    ax.set_ylim(bounds[0, 1] - margin[1], bounds[1, 1] + margin[1])
    ax.set_zlim(0, bounds[1, 2] + margin[2])
    ax.view_init(elev=22, azim=-58)
    ax.set_box_aspect((5.8, 2.2, 1.25)); ax.set_axis_off()
    ax.set_title("W11 GLB-derived watertight CFD surface — not box primitives", fontsize=16, pad=15)
    fig.tight_layout()
    fig.savefig(args.outdir / "W11_GLBDERIVED_CFD_SURFACE_ISOMETRIC.png", dpi=190, transparent=False)
    plt.close(fig)
    print(args.outdir)


if __name__ == "__main__":
    main()

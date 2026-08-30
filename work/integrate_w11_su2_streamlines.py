#!/usr/bin/env python3
"""Integrate continuous streamlines from a raw-appended SU2 VTU field."""

from __future__ import annotations

import argparse
import json
import math
import re
import struct
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
import matplotlib.tri as mtri
import numpy as np
from scipy.spatial import cKDTree
import trimesh


TYPE = {
    "Float32": np.dtype("<f4"), "Float64": np.dtype("<f8"),
    "Int32": np.dtype("<i4"), "UInt32": np.dtype("<u4"),
    "Int64": np.dtype("<i8"), "UInt64": np.dtype("<u8"), "UInt8": np.dtype("u1"),
}


def read_raw_vtu(path: Path):
    raw = path.read_bytes()
    marker = raw.index(b'<AppendedData encoding="raw">')
    start = raw.index(b"_", marker) + 1
    header = raw[:marker].decode("utf-8")
    piece = re.search(r'<Piece NumberOfPoints="(\d+)" NumberOfCells="(\d+)">', header)
    point_count = int(piece.group(1))
    arrays = []
    for tag in re.findall(r"<DataArray[^>]+/>", header):
        attrs = dict(re.findall(r'(\w+)=\s*"([^"]*)"', tag))
        arrays.append(attrs)

    def array(name, components=None, offset=None):
        candidates = [item for item in arrays if item.get("Name", "") == name]
        if components is not None:
            candidates = [item for item in candidates if int(item.get("NumberOfComponents", "1")) == components]
        if offset is not None:
            candidates = [item for item in candidates if int(item["offset"]) == offset]
        if not candidates:
            raise KeyError(name)
        item = candidates[0]
        position = start + int(item["offset"])
        byte_count = struct.unpack_from("<Q", raw, position)[0]
        dtype = TYPE[item["type"]]
        count = int(item.get("NumberOfComponents", "1"))
        data = np.frombuffer(raw, dtype=dtype, count=byte_count // dtype.itemsize, offset=position + 8).copy()
        return data.reshape(-1, count) if count > 1 else data

    points = array("", components=3, offset=0)
    velocity = array("Velocity", components=3)
    pressure_coefficient = array("Pressure_Coefficient")
    if len(points) != point_count:
        raise ValueError("Point count mismatch")
    return points.astype(float), velocity.astype(float), pressure_coefficient.astype(float)


class VelocitySampler:
    def __init__(self, points, velocity):
        self.points = points
        self.velocity = velocity
        self.tree = cKDTree(points)

    def sample(self, point):
        distance, index = self.tree.query(point, k=4)
        if distance[0] > 0.30:
            return None, float(distance[0])
        weight = 1.0 / np.maximum(distance, 1e-5) ** 2
        vector = np.sum(self.velocity[index] * weight[:, None], axis=0) / weight.sum()
        return vector, float(distance[0])


def integrate(sampler, seed, step=0.045, max_steps=400, direction_sign=1.0):
    point = np.asarray(seed, dtype=float)
    path, speeds = [point.copy()], []
    for _ in range(max_steps):
        vector, distance = sampler.sample(point)
        if vector is None:
            break
        speed = np.linalg.norm(vector)
        if not np.isfinite(speed) or speed < 0.02:
            break
        direction = direction_sign * vector / speed
        midpoint = point + 0.5 * step * direction
        middle_vector, _ = sampler.sample(midpoint)
        if middle_vector is None or np.linalg.norm(middle_vector) < 0.02:
            break
        point = point + direction_sign * step * middle_vector / np.linalg.norm(middle_vector)
        if not (-4.5 <= point[0] <= 8.0 and -3.0 <= point[1] <= 3.0 and 0.0 <= point[2] <= 3.2):
            break
        path.append(point.copy()); speeds.append(speed)
        if (direction_sign > 0 and point[0] > 7.0) or (direction_sign < 0 and point[0] < -4.0):
            break
    return np.asarray(path), np.asarray(speeds)


def integrate_bidirectional(sampler, seed):
    """Trace one continuous streamline upstream and downstream from a seed."""
    forward, forward_speed = integrate(sampler, seed, direction_sign=1.0)
    backward, backward_speed = integrate(sampler, seed, direction_sign=-1.0)
    if len(backward) < 2:
        return forward, forward_speed
    points = np.vstack((backward[:0:-1], forward))
    # Speed arrays have one fewer entry than their point arrays.
    back_vertex_speed = np.r_[backward_speed, backward_speed[-1] if len(backward_speed) else 0.0]
    fwd_vertex_speed = np.r_[forward_speed, forward_speed[-1] if len(forward_speed) else 0.0]
    vertex_speed = np.r_[back_vertex_speed[:0:-1], fwd_vertex_speed]
    return points, vertex_speed


def projected_shell(mesh, axes):
    render = mesh.simplify_quadric_decimation(face_count=min(90000, len(mesh.faces)), aggression=5)
    return render.vertices[render.faces][:, :, axes]


def streamline_collection(ax, lines, axes, freestream=83.333333):
    segments, values = [], []
    for line in lines:
        p = np.asarray(line["points_m"])
        q = np.asarray(line["speed_ratio"])
        if len(p) < 2:
            continue
        segments.extend(np.stack((p[:-1, axes], p[1:, axes]), axis=1))
        values.extend(q[: len(p) - 1])
    collection = LineCollection(segments, cmap="turbo", norm=plt.Normalize(0.15, 1.35), linewidths=1.45, alpha=0.94)
    collection.set_array(np.asarray(values))
    ax.add_collection(collection)
    return collection


def plots(points, velocity, cp, lines, shell, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 1, figsize=(12, 7.6))
    for ax, dims, title, ylim in [
        (axes[0], [0, 2], "Continuous solver-integrated airflow — side projection", (-0.02, 2.25)),
        (axes[1], [0, 1], "Continuous solver-integrated airflow — top projection", (-2.0, 2.0)),
    ]:
        ax.add_collection(PolyCollection(projected_shell(shell, dims), facecolor="#343b45", edgecolor="none", alpha=0.78))
        collection = streamline_collection(ax, lines, dims)
        ax.set_xlim(-4.2, 7.2); ax.set_ylim(*ylim); ax.set_aspect("equal")
        ax.grid(alpha=0.16); ax.set_title(title)
        ax.set_xlabel("Longitudinal x (m)"); ax.set_ylabel("Height z (m)" if dims[1] == 2 else "Lateral y (m)")
    fig.colorbar(collection, ax=axes, label="Velocity / 83.333 m/s", fraction=0.025, pad=0.02)
    fig.suptitle("W11 GLB-derived SU2 field at 300 km/h — continuous streamlines", fontsize=16)
    fig.subplots_adjust(left=0.08, right=0.90, top=0.91, bottom=0.07, hspace=0.34)
    fig.savefig(outdir / "SOLVER_DERIVED_CONTINUOUS_STREAMLINES.png", dpi=190)
    plt.close(fig)

    mask = np.abs(points[:, 1]) < 0.10
    # Velocity is nondimensional in this SU2 VTU; freestream magnitude is 1.
    plane = points[mask]; ratio = np.linalg.norm(velocity[mask], axis=1); plane_cp = cp[mask]
    tri = mtri.Triangulation(plane[:, 0], plane[:, 2])
    bad = []
    for face in tri.triangles:
        x, z = plane[face, 0], plane[face, 2]
        bad.append((x.max() - x.min() > 0.35) or (z.max() - z.min() > 0.25))
    tri.set_mask(bad)
    for values, limits, cmap, title, filename, label in [
        (ratio, (0, 1.45), "turbo", "Solved symmetry-plane velocity field", "SOLVED_VELOCITY_SIDEPLANE.png", "Velocity / freestream"),
        (plane_cp, (-1.5, 1.5), "coolwarm", "Solved symmetry-plane pressure coefficient", "SOLVED_PRESSURE_SIDEPLANE.png", "Cp"),
    ]:
        fig, ax = plt.subplots(figsize=(12, 4.8))
        contour = ax.tricontourf(tri, values, levels=np.linspace(*limits, 55), cmap=cmap, extend="both")
        ax.add_collection(PolyCollection(projected_shell(shell, [0, 2]), facecolor="white", edgecolor="#111820", linewidth=0.2, alpha=0.98))
        ax.set(xlim=(-3.5, 6.5), ylim=(0, 2.2), xlabel="Longitudinal x (m)", ylabel="Height z (m)", title=title)
        ax.set_aspect("equal"); fig.colorbar(contour, ax=ax, label=label)
        fig.tight_layout(); fig.savefig(outdir / filename, dpi=190); plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vtu", type=Path, required=True)
    parser.add_argument("--shell", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--figures", type=Path, required=True)
    args = parser.parse_args()
    points, velocity, cp = read_raw_vtu(args.vtu)
    sampler = VelocitySampler(points, velocity)
    seeds = []
    for z in (0.18, 0.30, 0.52, 0.78, 1.05, 1.35, 1.70, 2.05):
        for y in (-1.35, -0.90, -0.55, 0.0, 0.55, 0.90, 1.35):
            seeds.append((-4.0, y, z))
    # Bidirectional floor seeds trace the solved path both upstream and through
    # the diffuser. Seeding inside the flow avoids a front-wing solid blocking
    # a forward-only numerical trace on this coarse screening mesh.
    for x in (0.50, 1.00):
        for z in (0.045, 0.070):
            for y in (-0.62, -0.32, 0.0, 0.32, 0.62):
                seeds.append((x, y, z))
    for y in (-1.22, 1.22):
        for z in (0.28, 0.48, 0.72, 0.95):
            seeds.append((-2.25, y, z))
    # Solved-field paths selected specifically because their bidirectional
    # traces pass the front-wing region, remain close to the floor and continue
    # through the rear diffuser. These are not hand-drawn presentation curves.
    front_diffuser_seeds = [
        (-1.40, -0.30, 0.20), (-1.40, -0.30, 0.22),
        (-1.40, -0.20, 0.12), (-1.20, -0.30, 0.16),
        (-1.20, -0.20, 0.14), (-1.20, -0.20, 0.22),
        (-1.00, -0.50, 0.28), (-1.00, -0.40, 0.24),
        (-0.80, -0.70, 0.32),
    ]
    seeds.extend(front_diffuser_seeds)
    lines = []
    for seed in seeds:
        is_floor = seed[2] < 0.20 and seed[0] > 0.0
        is_front_diffuser = seed in front_diffuser_seeds
        path, speeds = integrate_bidirectional(sampler, seed) if (is_floor or is_front_diffuser) else integrate(sampler, seed)
        if len(path) < 24 or path[-1, 0] < 2.7:
            continue
        # SU2 stores velocity nondimensionally here; freestream magnitude is 1.
        ratio = speeds if len(speeds) == len(path) else np.r_[speeds, speeds[-1]]
        lines.append({
            "seed_m": list(seed),
            "region": "front_wing_to_diffuser" if is_front_diffuser else ("underfloor" if is_floor else "whole_car"),
            "points_m": np.round(path, 5).tolist(),
            "speed_ratio": np.round(ratio, 5).tolist(),
            "mean_speed_ratio": float(np.mean(ratio)),
            "minimum_speed_ratio": float(np.min(ratio)),
            "maximum_speed_ratio": float(np.max(ratio)),
        })
    payload = {
        "source": args.vtu.name,
        "method": "steady streamline integration using inverse-distance interpolation of the solved SU2 nodal velocity field and midpoint stepping",
        "freestream_m_s": 83.333333,
        "streamline_count": len(lines),
        "streamlines": lines,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, separators=(",", ":")) + "\n")
    shell = trimesh.load(args.shell, force="mesh", process=False)
    plots(points, velocity, cp, lines, shell, args.figures)
    print(json.dumps({"streamlines": len(lines), "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import livery

HERE = Path(__file__).resolve().parent


def top_map(P, N, cell, samples=40):
    fn = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    fn *= np.where((fn * N.sum(1)).sum(1) < 0, -1.0, 1.0)[:, None]
    rng = np.random.default_rng(0)
    pts = np.concatenate([np.einsum("fk,fkc->fc", rng.dirichlet([1, 1, 1], len(P)), P) for _ in range(samples)])
    fz = np.tile(fn[:, 2], samples)
    key = np.floor(pts[:, :2] / cell).astype(np.int64)
    order = np.lexsort((pts[:, 2], key[:, 1], key[:, 0]))
    key, z, fz = key[order], pts[order, 2], fz[order]
    last = np.ones(len(key), bool)
    last[:-1] = np.any(key[1:] != key[:-1], axis=1)
    return key[last], z[last], fz[last]


def main():
    p = argparse.ArgumentParser(prog="fit.py", description="Show where a top-view emblem can go on a jet: flat spine, wing leading edge, and a top-view preview of the emblem.")
    p.add_argument("jet", help="warthunder/jets/<jet>.json")
    p.add_argument("--livery", default="dragon-crew", help="livery model: warthunder/liveries/<livery>/")
    p.add_argument("--svg", help="emblem SVG to preview instead of the one in the jet file")
    p.add_argument("--center", type=float, nargs=2, help="emblem center X Y instead of the jet file's")
    p.add_argument("--length", type=float, help="emblem length instead of the jet file's")
    p.add_argument("--facing", type=float, default=0.93, help="flat means the face normal points up by more than this")
    p.add_argument("--out", default=str(HERE / "out" / "fit"), help="folder for <jet>_top.png")
    a = p.parse_args()

    cfg = json.loads((HERE / "jets" / f"{a.jet}.json").read_text(encoding="utf-8"))
    gltf = HERE / "models" / cfg["model"] / f"{cfg['model']}.gltf"
    P, N, _, _, _ = livery.load_mesh(gltf, f"{cfg['prefix'].lower()}_c")
    cell = 0.02
    key, z, fz = top_map(P, N, cell)
    flat = fz > a.facing
    lo, hi = P.reshape(-1, 3).min(0), P.reshape(-1, 3).max(0)
    print(f"mesh X {lo[0]:.2f} to {hi[0]:.2f}, Y {lo[1]:.2f} to {hi[1]:.2f}, Z {lo[2]:.2f} to {hi[2]:.2f} m")

    cells = {(int(k[0]), int(k[1])): f for k, f in zip(key, flat)}
    print("\nflat spine half-width (m) by X station (facing > %.2f, contiguous from the centerline):" % a.facing)
    for xs in np.arange(np.floor(lo[0] * 10) / 10, hi[0], 0.2):
        kx = int(np.floor(xs / cell))
        w = 0
        while cells.get((kx, w)) or cells.get((kx, w + 1)):
            w += 1
        if w:
            print(f"  X {xs:6.2f}: {w * cell:.2f}")

    print("\nforemost flat top surface (m) by Y station, beyond 0.4 m (a wing leading edge on a wing):")
    for ys in np.arange(0.4, hi[1], 0.2):
        ky = int(np.floor(ys / cell))
        xs = [kx for (kx, kyy), f in cells.items() if kyy == ky and f]
        if xs:
            print(f"  Y {ys:5.2f}: X {(max(xs) + 1) * cell:6.2f} front, {min(xs) * cell:6.2f} back")

    em = next((e for e in cfg.get("emblems", [])), None)
    svg = Path(a.svg) if a.svg else (HERE / "liveries" / a.livery / f"{em['svg']}.svg" if em else None)
    S = 100
    W, H = int((hi[0] - lo[0] + 0.4) * S), int((2 * max(abs(lo[1]), hi[1]) + 0.4) * S)
    x0, ymid = lo[0] - 0.2, H / 2

    def to_px(x, y):
        return (x - x0) * S, ymid - y * S

    img = np.full((H, W, 3), 128, np.uint8)
    u = ((key[:, 0] + 0.5) * cell - x0) * S
    v = ymid - (key[:, 1] + 0.5) * cell * S
    ok = (u >= 0) & (u < W - 1) & (v >= 0) & (v < H - 1)
    shade = np.where(fz > a.facing, 40, np.where(fz > 0.7, 75, 105)).astype(np.uint8)
    for du in (0, 1):
        for dv in (0, 1):
            img[v[ok].astype(int) + dv, u[ok].astype(int) + du] = shade[ok, None]
    if svg is not None:
        shape = livery.load_shape(svg, "emblem")
        smin, smax = shape.min(0), shape.max(0)
        cx, cy = a.center if a.center else em["center"]
        length = a.length if a.length else em["length"]
        scale = length / (smax[1] - smin[1])
        mid = (smin + smax) / 2
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon([to_px(cx - (sy - mid[1]) * scale, cy - (sx - mid[0]) * scale) for sx, sy in shape], fill=255)
        mask = np.asarray(m) > 0
        if em and em.get("bands"):
            yy = np.abs(ymid - np.arange(H)) / S
            keep = np.zeros(H, bool)
            for b0, b1 in em["bands"]:
                keep |= (yy >= b0) & (yy <= b1)
            mask &= keep[:, None]
        img[mask] = 240
        print(f"\nemblem {svg.name}: center {cx}, {cy}, length {length} m, X {cx - length / 2:.2f} to {cx + length / 2:.2f}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img).save(out / f"{a.jet}_top.png")
    print(f"\nwrote {out / (a.jet + '_top.png')}: nose to the right, dark = flat top, mid = curved, light = steep; white = emblem after bands")


if __name__ == "__main__":
    main()

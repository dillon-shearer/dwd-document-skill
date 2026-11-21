import argparse
import json
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree

Image.MAX_IMAGE_PIXELS = None

HERE = Path(__file__).resolve().parent
USER_SKINS = Path(r"C:\Program Files (x86)\Steam\steamapps\common\War Thunder\UserSkins")
CT = {5126: np.float32, 5123: np.uint16, 5125: np.uint32, 5121: np.uint8}
NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
SVG = "{http://www.w3.org/2000/svg}"


def log(msg, t0=[time.time()]):
    print(f"[{time.time() - t0[0]:6.1f}s] {msg}", flush=True)


def hex_rgb(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def read_blk(path):
    text = path.read_text(encoding="utf-8", errors="replace")
    pairs = re.findall(r'from:t="([^"]+)"\s*to:t="([^"]+)"', text)
    if not pairs:
        raise SystemExit(f"no replace_tex entries in {path}")
    return pairs


def template_files(tdir, prefix):
    blks = sorted(tdir.glob("*.blk"))
    if len(blks) != 1:
        raise SystemExit(f"expected one .blk in {tdir}, found {len(blks)}")
    color = normal = None
    for src, dst in read_blk(blks[0]):
        src = src.lower().rstrip("*")
        if src == f"{prefix}_c":
            color = tdir / dst
        elif src == f"{prefix}_n":
            normal = tdir / dst
    if color is None or normal is None:
        raise SystemExit(f"{blks[0]} has no replace_tex for {prefix}_c and {prefix}_n")
    for p in (color, normal):
        if not p.exists():
            raise SystemExit(f"missing template file {p}")
    return blks[0], color, normal


def load_mesh(gltf, image_stem):
    g = json.loads(gltf.read_text(encoding="utf-8"))
    buf = (gltf.parent / g["buffers"][0]["uri"]).read_bytes()

    def acc(i):
        a = g["accessors"][i]
        bv = g["bufferViews"][a["bufferView"]]
        n = NC[a["type"]]
        dt = np.dtype(CT[a["componentType"]])
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        stride = bv.get("byteStride", 0)
        if stride and stride != n * dt.itemsize:
            raw = np.frombuffer(buf, np.uint8, count=stride * a["count"], offset=off).reshape(-1, stride)
            return raw[:, :n * dt.itemsize].copy().view(dt).reshape(a["count"], n)
        return np.frombuffer(buf, dt, count=a["count"] * n, offset=off).reshape(a["count"], n)

    if len(g.get("nodes", [])) != 1 or any(k in g["nodes"][0] for k in ("matrix", "translation", "rotation", "scale")):
        raise SystemExit(f"{gltf}: expected one untransformed node, as wt-unpack writes")
    P, N, U, prim, normal = [], [], [], [], None
    for pi, pr in enumerate(g["meshes"][0]["primitives"]):
        mat = g["materials"][pr["material"]] if "material" in pr else {}
        t = mat.get("pbrMetallicRoughness", {}).get("baseColorTexture")
        if not t:
            continue
        uri = g["images"][g["textures"][t["index"]]["source"]]["uri"]
        if Path(uri).stem.lower() != image_stem:
            continue
        nt = mat.get("normalTexture")
        if nt and normal is None:
            normal = Path(g["images"][g["textures"][nt["index"]]["source"]]["uri"]).name
        idx = acc(pr["indices"]).ravel().astype(np.int64)
        P.append(acc(pr["attributes"]["POSITION"])[idx])
        N.append(acc(pr["attributes"]["NORMAL"])[idx])
        U.append(acc(pr["attributes"]["TEXCOORD_0"])[idx])
        prim.append(np.full(len(idx) // 3, pi, dtype=np.int32))
    if not P:
        raise SystemExit(f"no primitive in {gltf} uses {image_stem}")
    P = np.concatenate(P).astype(np.float64)
    N = np.concatenate(N).astype(np.float64)
    U = np.concatenate(U).astype(np.float64)
    P = np.stack([P[:, 0], -P[:, 2], P[:, 1]], 1).reshape(-1, 3, 3)
    N = np.stack([N[:, 0], -N[:, 2], N[:, 1]], 1).reshape(-1, 3, 3)
    return P, N, U.reshape(-1, 3, 2), np.concatenate(prim), normal


def rasterize(U, W, H, budget=4_000_000):
    px = U[..., 0] * W - 0.5
    py = U[..., 1] * H - 0.5
    x0 = np.clip(np.floor(px.min(1)), 0, W - 1).astype(np.int64)
    x1 = np.clip(np.ceil(px.max(1)), 0, W - 1).astype(np.int64)
    y0 = np.clip(np.floor(py.min(1)), 0, H - 1).astype(np.int64)
    y1 = np.clip(np.ceil(py.max(1)), 0, H - 1).astype(np.int64)
    bw = x1 - x0 + 1
    bh = y1 - y0 + 1
    order = np.argsort(bw * bh, kind="stable")
    ts, pixs, bs = [], [], []
    i, T = 0, len(order)
    while i < T:
        mw, mh = bw[order[i]], bh[order[i]]
        j = i + 1
        while j < T:
            nw, nh = max(mw, bw[order[j]]), max(mh, bh[order[j]])
            if (j + 1 - i) * nw * nh > budget:
                break
            mw, mh = nw, nh
            j += 1
        k = order[i:j]
        gx = x0[k, None, None] + np.arange(mw)[None, None, :]
        gy = y0[k, None, None] + np.arange(mh)[None, :, None]
        ax, ay = px[k, 0, None, None], py[k, 0, None, None]
        bx, by = px[k, 1, None, None], py[k, 1, None, None]
        cx, cy = px[k, 2, None, None], py[k, 2, None, None]
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        den = np.where(np.abs(den) < 1e-12, 1e-12, den)
        l0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l2 = 1.0 - l0 - l1
        eps = -1e-6
        inside = (l0 >= eps) & (l1 >= eps) & (l2 >= eps) & (gx <= x1[k, None, None]) & (gy <= y1[k, None, None])
        ti, yy, xx = np.nonzero(inside)
        ts.append(k[ti].astype(np.int32))
        pixs.append(((y0[k][ti] + yy) * W + x0[k][ti] + xx).astype(np.int32))
        bs.append(np.stack([l0[ti, yy, xx], l1[ti, yy, xx], l2[ti, yy, xx]], 1).astype(np.float32))
        i = j
    return np.concatenate(ts), np.concatenate(pixs), np.concatenate(bs)


def texel_size(P, U, W, H):
    e1, e2 = P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]
    a3 = 0.5 * np.linalg.norm(np.cross(e1, e2), axis=1)
    f1 = (U[:, 1] - U[:, 0]) * (W, H)
    f2 = (U[:, 2] - U[:, 0]) * (W, H)
    a2 = 0.5 * np.abs(f1[:, 0] * f2[:, 1] - f1[:, 1] * f2[:, 0])
    return np.maximum(np.sqrt(a3 / np.maximum(a2, 1e-9)), 1e-5).astype(np.float32)


def splinter_mask(pos, cfg, lo, hi):
    cell = np.array(cfg["cell"], dtype=np.float64)
    rng = np.random.default_rng(int(cfg["seed"]))
    mirror = bool(cfg.get("mirror", True))
    q = pos.astype(np.float64)
    if mirror:
        q[:, 1] = np.abs(q[:, 1])
        lo = np.array([lo[0], 0.0, lo[2]])
        hi = np.array([hi[0], max(abs(lo[1]), abs(hi[1])), hi[2]])
    n = np.ceil((hi - lo) / cell).astype(int) + 3
    grid = np.stack(np.meshgrid(*[np.arange(c) for c in n], indexing="ij"), -1).reshape(-1, 3)
    seeds = (grid - 1 + rng.random(grid.shape)) * cell + lo
    dark = rng.random(len(seeds)) < float(cfg.get("share", 0.5))
    tree = cKDTree(seeds / cell)
    _, idx = tree.query(q / cell, workers=-1)
    return ~dark[idx]


def flatten_path(d, steps=24):
    toks = re.findall(r"[MLHVCQZmlhvcqz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    pts, cur, cmd, i = [], np.zeros(2), None, 0

    def num(k):
        return [float(t) for t in toks[i:i + k]]

    while i < len(toks):
        if re.match(r"[A-Za-z]", toks[i]):
            cmd = toks[i]
            i += 1
            if cmd in "Zz":
                continue
        if cmd != cmd.upper():
            raise SystemExit("insignia.svg: use absolute path commands only")
        if cmd in ("M", "L"):
            cur = np.array(num(2))
            i += 2
            pts.append(cur)
        elif cmd == "H":
            cur = np.array([num(1)[0], cur[1]])
            i += 1
            pts.append(cur)
        elif cmd == "V":
            cur = np.array([cur[0], num(1)[0]])
            i += 1
            pts.append(cur)
        elif cmd == "C":
            c1, c2, e = (np.array(num(6)[k:k + 2]) for k in (0, 2, 4))
            i += 6
            for t in np.linspace(0, 1, steps + 1)[1:]:
                pts.append((1 - t) ** 3 * cur + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t * t * c2 + t ** 3 * e)
            cur = e
        elif cmd == "Q":
            c1, e = (np.array(num(4)[k:k + 2]) for k in (0, 2))
            i += 4
            for t in np.linspace(0, 1, steps + 1)[1:]:
                pts.append((1 - t) ** 2 * cur + 2 * (1 - t) * t * c1 + t * t * e)
            cur = e
        else:
            raise SystemExit(f"insignia.svg: unsupported path command {cmd}")
    pts = np.array(pts)
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    return pts


def load_insignia(path):
    root = ET.parse(path).getroot()
    found = {el.get("id"): el for el in root.iter() if el.get("id")}
    for need in ("shield", "zero", "slash"):
        if need not in found:
            raise SystemExit(f"{path}: no element with id {need}")
    shield = flatten_path(found["shield"].get("d"))
    z = found["zero"]
    if z.get("d"):
        zero = flatten_path(z.get("d"))
    else:
        cx, cy, rx, ry = (float(z.get(k)) for k in ("cx", "cy", "rx", "ry"))
        a = np.linspace(0, 2 * np.pi, 241)[:-1]
        zero = np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], 1)
    s = found["slash"]
    slash = np.array([[float(s.get("x1")), float(s.get("y1"))], [float(s.get("x2")), float(s.get("y2"))]])
    return {
        "shield": shield,
        "zero": zero,
        "zero_w": float(z.get("stroke-width")),
        "slash": slash,
        "slash_w": float(s.get("stroke-width")),
    }


def load_shape(path, el_id):
    root = ET.parse(path).getroot()
    el = next((e for e in root.iter() if e.get("id") == el_id), None)
    if el is None:
        raise SystemExit(f"{path}: no element with id {el_id}")
    return flatten_path(el.get("d"))


def seg_dist(p, a, b):
    ab = b - a
    t = np.clip(((p[:, None, :] - a) * ab).sum(-1) / np.maximum((ab * ab).sum(-1), 1e-12), 0, 1)
    d = p[:, None, :] - (a + t[..., None] * ab)
    return np.sqrt((d * d).sum(-1)).min(1)


def poly_sdf(p, poly):
    a, b = poly, np.roll(poly, -1, axis=0)
    d = seg_dist(p, a, b)
    x, y = p[:, 0:1], p[:, 1:2]
    cond = ((a[:, 1] > y) != (b[:, 1] > y)) & (x < (b[:, 0] - a[:, 0]) * (y - a[:, 1]) / (b[:, 1] - a[:, 1] + 1e-12) + a[:, 0])
    inside = (cond.sum(1) % 2) == 1
    return np.where(inside, -d, d)


def poly_sdf_chunked(p, poly, chunk=200_000):
    return np.concatenate([poly_sdf(p[i:i + chunk], poly) for i in range(0, len(p), chunk)]) if len(p) else np.zeros(0)


def badge_alpha(p, px_size, ins, outline):
    shield_d = poly_sdf(p, ins["shield"])
    a_shield = np.clip(0.5 - shield_d / px_size, 0, 1)
    a_outline = a_shield * np.clip(0.5 + (shield_d + outline) / px_size, 0, 1)
    ring_d = np.abs(poly_sdf(p, ins["zero"])) - ins["zero_w"] / 2
    a_ring = np.clip(0.5 - ring_d / px_size, 0, 1)
    a0, a1 = ins["slash"]
    axis = (a1 - a0) / np.linalg.norm(a1 - a0)
    rel = p - a0
    along = rel @ axis
    across = np.abs(rel @ np.array([-axis[1], axis[0]]))
    length = np.linalg.norm(a1 - a0)
    slash_d = np.maximum(across - ins["slash_w"] / 2, np.maximum(-along, along - length))
    a_slash = np.clip(0.5 - slash_d / px_size, 0, 1)
    a_white = np.maximum(a_outline, a_shield * np.maximum(a_ring, a_slash))
    return a_shield, a_white


def side_frags(pos, nrm, cx, cz, half_w, half_h, max_offset=None):
    near = (np.abs(pos[:, 0] - cx) <= half_w) & (np.abs(pos[:, 2] - cz) <= half_h)
    if max_offset is not None:
        near &= np.abs(pos[:, 1]) <= float(max_offset)
    for side, sign in (("left", -1.0), ("right", 1.0)):
        sel = np.nonzero(near & (nrm[:, 1] * sign > 0.5))[0]
        if len(sel):
            yield side, sel, (pos[sel, 0] - cx) * -sign, pos[sel, 2] - cz


def text_mask(text, font_name, height_m, texel_m, slashed_zero=False):
    from PIL import ImageDraw, ImageFont
    path = Path(r"C:\Windows\Fonts") / f"{font_name.lower()}.ttf"
    if not path.exists():
        raise SystemExit(f"font {font_name} not found at {path}")
    font = ImageFont.truetype(str(path), 512)
    try:
        font.set_variation_by_name("SemiBold")
    except (OSError, ValueError):
        pass
    x0, y0, x1, y1 = font.getbbox(text)
    gx0, gy0, gx1, gy1 = font.getbbox("0")
    pad = int((gy1 - gy0) * 0.25) + 8
    img = Image.new("L", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), 0)
    draw = ImageDraw.Draw(img)
    draw.text((pad - x0, pad - y0), text, font=font, fill=255)
    if slashed_zero:
        hw, hh = (gx1 - gx0) / 2, (gy1 - gy0) / 2
        for i, ch in enumerate(text):
            if ch != "0":
                continue
            cx = pad - x0 + font.getlength(text[:i]) + (gx0 + gx1) / 2
            cy = pad - y0 + (gy0 + gy1) / 2
            draw.line([(cx - hw, cy + 1.22 * hh), (cx + hw, cy - 1.22 * hh)], fill=255, width=max(1, int(round(hh * 0.24))))
    total = img.height / (y1 - y0)
    rows = max(16, min(2048, int(round(height_m * total / texel_m * 2))))
    small = img.resize((max(16, int(round(img.width * rows / img.height))), rows), Image.LANCZOS)
    return np.asarray(small, dtype=np.float32) / 255.0, img.width / img.height, total


def high_pass_color(img, size):
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-3)
    decal = (sat > 0.18) | (lum > 0.8)
    decal = ndimage.binary_dilation(decal, iterations=max(2, rgb.shape[0] // 1024))
    hp = lum - ndimage.gaussian_filter(lum, rgb.shape[0] / 340.0)
    hp[decal] = 0
    hp = np.clip(hp, -0.12, 0.12)
    return np.asarray(Image.fromarray(hp).resize(size, Image.BILINEAR), dtype=np.float32)


def panel_lines(path, size):
    n = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    dev = np.sqrt((n[..., 0] - 0.5) ** 2 + (n[..., 1] - 0.5) ** 2) * 2
    line = np.clip((dev - 0.04) / 0.2, 0, 1)
    return np.asarray(Image.fromarray(line).resize(size, Image.BILINEAR), dtype=np.float32)


def bake(label, cfg, style, mesh, bounds, tmpl, line_png, weather_img, opts):
    P, N, U, prim = mesh
    H, W = tmpl.shape[:2]
    tri, pix, bary = rasterize(U, W, H)
    log(f"{label}: {len(P)} triangles, {len(pix)} fragments on {len(np.unique(pix))} texels")

    pos = np.einsum("fk,fkc->fc", bary, P[tri].astype(np.float32))
    nrm = np.einsum("fk,fkc->fc", bary, N[tri].astype(np.float32))
    tsz = texel_size(P, U, W, H)[tri]

    base = hex_rgb(style["base"])
    shade = hex_rgb(style["splinter"])
    white = hex_rgb(style["white"])
    detail_w = np.ones(len(pix), dtype=np.float32)
    if np.array_equal(shade, base):
        col = np.repeat(base[None, :], len(pix), 0)
        log(f"{label}: one base color, no splinter")
    else:
        light = splinter_mask(pos, cfg["splinter"], *bounds)
        col = np.where(light[:, None], shade, base).astype(np.float32)
        log(f"{label}: splinter, {light.mean():.2f} of fragments in the lighter shade")

    tips = cfg.get("wingtips", [])
    for wt in [tips] if isinstance(tips, dict) else tips:
        inbox = (pos[:, 0] >= wt["x"][0]) & (pos[:, 0] <= wt["x"][1]) & (pos[:, 2] >= wt["z"][0]) & (pos[:, 2] <= wt["z"][1])
        edge = float(wt["tip"]) - float(wt["width"])
        a = np.clip(0.5 + (np.abs(pos[:, 1]) - edge) / tsz, 0, 1) * inbox
        col = col + (white - col) * a[:, None]
        detail_w *= 1 - a
        if (a > 0.5).any():
            log(f"{label}: {wt.get('what', 'wingtips')}, {int((a > 0.5).sum())} fragments white from |y| {edge:.3f} m out")

    if cfg.get("emblems"):
        fn = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
        fn *= np.where((fn * N.sum(1)).sum(1) < 0, -1.0, 1.0)[:, None]
        face_z = fn[tri, 2].astype(np.float32)
    for em in cfg.get("emblems", []):
        shape = load_shape(opts["art"] / f"{em['svg']}.svg", "emblem")
        smin, smax = shape.min(0), shape.max(0)
        scale = float(em["length"]) / (smax[1] - smin[1])
        mid = (smin + smax) / 2
        cx, cy = em["center"]
        near = (np.abs(pos[:, 0] - cx) <= (smax[1] - smin[1]) / 2 * scale + 0.02) & (np.abs(pos[:, 1] - cy) <= (smax[0] - smin[0]) / 2 * scale + 0.02)
        if em.get("bands"):
            off = np.abs(pos[:, 1] - cy)
            near &= np.any([(off >= lo_b) & (off <= hi_b) for lo_b, hi_b in em["bands"]], axis=0)
        tint = hex_rgb(style[em.get("color", "white")])
        for side, sign in (("top", 1.0), ("bottom", -1.0)):
            if side not in em.get("surfaces", ["top"]):
                continue
            cand = np.nonzero(near)[0]
            if not len(cand):
                continue
            cell = float(em.get("cell", 0.02))
            _, inv = np.unique(np.floor(pos[cand, :2] / cell).astype(np.int64), axis=0, return_inverse=True)
            inv = inv.ravel()
            zs = pos[cand, 2] * sign
            zmax = np.full(inv.max() + 1, -np.inf, dtype=np.float32)
            np.maximum.at(zmax, inv, zs)
            front = zs >= zmax[inv] - float(em.get("depth_tol", 0.03))
            sel = cand[front & (face_z[cand] * sign > float(em.get("min_facing", 0.2))) & (nrm[cand, 2] * sign > 0)]
            if not len(sel):
                continue
            p = np.stack([mid[0] - sign * (pos[sel, 1] - cy) / scale, mid[1] - (pos[sel, 0] - cx) / scale], 1)
            a = np.clip(0.5 - poly_sdf_chunked(p, shape) / (tsz[sel] / scale), 0, 1)
            col[sel] = col[sel] + (tint - col[sel]) * a[:, None]
            detail_w[sel] *= 1 - a
            log(f"{label}: {em.get('what', em['svg'])} {side}, {int((a > 0.5).sum())} fragments")

    accent = hex_rgb(style.get("accent", style["white"]))
    for box in cfg.get("accents", []):
        tint = hex_rgb(style[box["color"]]) if box.get("color") else accent
        lo_b, hi_b = np.array(box["min"], np.float32), np.array(box["max"], np.float32)
        if box.get("whole"):
            ids = [p_id for p_id in np.unique(prim)
                   if np.all(P[prim == p_id].reshape(-1, 3).min(0) >= lo_b) and np.all(P[prim == p_id].reshape(-1, 3).max(0) <= hi_b)]
            a = np.isin(prim[tri], ids).astype(np.float32)
        else:
            inside = np.minimum(pos - lo_b, hi_b - pos).min(1)
            a = np.clip(0.5 + inside / tsz, 0, 1)
        col = col + (tint - col) * a[:, None]
        if not box.get("color"):
            detail_w *= 1 - a
        if (a > 0.5).any():
            log(f"{label}: accent {box.get('what', '')}, {int((a > 0.5).sum())} fragments")

    band = cfg.get("lead_band")
    if band and opts.get("lead"):
        a = np.clip(0.5 + np.minimum(pos[:, 2] - band["z"][0], band["z"][1] - pos[:, 2]) / tsz, 0, 1)
        a *= (pos[:, 0] >= band["x"][0]) & (pos[:, 0] <= band["x"][1]) & (np.abs(np.abs(pos[:, 1]) - float(band.get("y", 0))) <= band["max_offset"])
        col = col + (white - col) * a[:, None]
        detail_w *= 1 - a
        if (a > 0.5).any():
            log(f"{label}: flight lead fin band, {int((a > 0.5).sum())} fragments")

    lt = cfg.get("lettering")
    if lt:
        mask, aspect, total = text_mask(lt["text"], style["font"], float(lt["height"]), float(np.median(tsz)), bool(lt.get("slashed_zero")))
        cx, cz = lt["center"]
        h = float(lt["height"]) * total
        hits = {}
        for side, sel, s, t in side_frags(pos, nrm, cx, cz, h * aspect / 2 + 0.02, h / 2 + 0.02, lt.get("max_offset")):
            u = (s / h + aspect / 2) / aspect * (mask.shape[1] - 1)
            v = (0.5 - t / h) * (mask.shape[0] - 1)
            a = ndimage.map_coordinates(mask, [v, u], order=1, mode="constant", cval=0.0)
            col[sel] = col[sel] + (white - col[sel]) * a[:, None]
            detail_w[sel] *= 1 - a
            hits[side] = set(pix[sel[a > 0.01]].tolist())
            log(f"{label}: lettering {lt['text']} {side}, {int((a > 0.5).sum())} fragments")
        if len(hits) == 2 and hits["left"] & hits["right"]:
            raise SystemExit(f"{label}: lettering lands on texture space both sides share (mirrored UVs); move it")

    km = cfg.get("kill_marks")
    kills = int(opts.get("kills", 0))
    if km and kills > 0:
        root = ET.parse(opts["art"] / "kill.svg").getroot()
        shape = next((el for el in root.iter() if el.get("id") == "kill"), None)
        if shape is None:
            raise SystemExit(f"{opts['art'] / 'kill.svg'}: no element with id kill")
        shape = flatten_path(shape.get("d"))
        smin, smax = shape.min(0), shape.max(0)
        h = float(km["height"])
        scale = h / (smax[1] - smin[1])
        w = (smax[0] - smin[0]) * scale
        pitch = w + float(km["gap"])
        x0, cz = km["start"]
        length = kills * pitch
        for side, sel, s, t in side_frags(pos, nrm, x0 - length / 2, cz, length / 2 + 0.02, h / 2 + 0.02, km.get("max_offset")):
            along = x0 - pos[sel, 0]
            k = np.floor(along / pitch)
            ok = (k >= 0) & (k < kills)
            local = along - k * pitch - w / 2
            p = np.stack([(smin[0] + smax[0]) / 2 + local / scale, (smin[1] + smax[1]) / 2 - t / scale], 1)
            a = np.clip(0.5 - poly_sdf(p, shape) / (tsz[sel] / scale), 0, 1) * ok
            col[sel] = col[sel] + (white - col[sel]) * a[:, None]
            detail_w[sel] *= 1 - a
            log(f"{label}: {kills} kill marks {side}, {int((a > 0.5).sum())} fragments")

    fb = cfg.get("fin_badge")
    if fb:
        ins = load_insignia(opts["art"] / "insignia.svg")
        smin, smax = ins["shield"].min(0), ins["shield"].max(0)
        scale = float(fb["height"]) / (smax[1] - smin[1])
        mid = (smin + smax) / 2
        cx, cz = fb["center"]
        half_w = (smax[0] - smin[0]) / 2 * scale + 0.02
        half_h = (smax[1] - smin[1]) / 2 * scale + 0.02
        near = (np.abs(pos[:, 0] - cx) <= half_w) & (np.abs(pos[:, 2] - cz) <= half_h)
        fill = hex_rgb(style.get("badge_fill", style["base"]))
        for side, sign in (("left", -1.0), ("right", 1.0)):
            on_fin = np.abs(pos[:, 1] - sign * float(fb.get("y", 0))) <= float(fb["max_offset"])
            sel = np.nonzero(near & on_fin & (nrm[:, 1] * sign > 0.5))[0]
            if not len(sel):
                continue
            s = (pos[sel, 0] - cx) * -sign
            t = pos[sel, 2] - cz
            p = np.stack([mid[0] + s / scale, mid[1] - t / scale], 1)
            a_sh, a_wh = badge_alpha(p, tsz[sel] / scale, ins, float(style["badge_outline"]))
            c = col[sel]
            c = c + (fill - c) * a_sh[:, None]
            c = c + (white - c) * a_wh[:, None]
            col[sel] = c
            detail_w[sel] *= 1 - a_sh
            log(f"{label}: fin badge {side}, {int((a_sh > 0.5).sum())} fragments")

    if cfg.get("keep"):
        kept = []
        for p_id in np.unique(prim):
            pts = P[prim == p_id].reshape(-1, 3)
            pmin, pmax = pts.min(0), pts.max(0)
            if any(np.all(pmin >= box["min"]) and np.all(pmax <= box["max"]) for box in cfg["keep"]):
                kept.append(p_id)
        keep = np.isin(prim[tri], kept)
        col[keep] = tmpl[pix[keep] // W, pix[keep] % W, :3]
        detail_w[keep] = 0
        if kept:
            log(f"{label}: {len(kept)} parts left as the template has them")

    n_px = W * H
    cnt = np.bincount(pix, minlength=n_px).astype(np.float32)
    covered = cnt > 0
    acc = np.stack([np.bincount(pix, weights=col[:, c], minlength=n_px) for c in range(3)], 1).astype(np.float32)
    dw = np.bincount(pix, weights=detail_w, minlength=n_px).astype(np.float32)
    acc[covered] /= cnt[covered, None]
    dw[covered] /= cnt[covered]
    del pos, nrm, tsz, col, detail_w, bary, tri

    lines = panel_lines(line_png, (W, H)).ravel() if line_png and line_png.exists() else np.zeros(n_px, np.float32)
    weather = high_pass_color(weather_img, (W, H)).ravel() if weather_img is not None else np.zeros(n_px, np.float32)
    detail = lines * float(style["panel_lines"]) + weather * 255.0 * float(style["weathering"])
    acc += (detail * dw)[:, None]
    del lines, weather, detail, dw

    _, (iy, ix) = ndimage.distance_transform_edt(~covered.reshape(H, W), return_indices=True)
    rgb = acc.reshape(H, W, 3)[iy, ix]
    out = tmpl.copy()
    out[..., :3] = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
    return out


def skin_normal(model_dir, normal_png, size, style):
    n = np.asarray(Image.open(model_dir / normal_png).convert("RGB"))
    mr_path = model_dir / normal_png.replace("_normal.png", "_metal_rough.png")
    mr = np.asarray(Image.open(mr_path).convert("RGB")) if mr_path.exists() else None
    chans = [
        255 - mr[..., 1] if mr is not None else np.zeros(n.shape[:2], np.uint8),
        255 - n[..., 1],
        mr[..., 2] if mr is not None else np.zeros(n.shape[:2], np.uint8),
        n[..., 0],
    ]
    for i, key in ((0, "smoothness"), (2, "metalness")):
        if style.get(key) is not None:
            chans[i] = np.full(n.shape[:2], int(round(float(style[key]) * 255)), np.uint8)
        elif style.get(f"{key}_scale") is not None:
            chans[i] = np.clip(np.rint(chans[i] * float(style[f"{key}_scale"])), 0, 255).astype(np.uint8)
    out = [np.asarray(Image.fromarray(np.ascontiguousarray(c)).resize(size, Image.BILINEAR)) for c in chans]
    return np.stack(out, -1)


def save_like(rgba, mode, path):
    img = Image.fromarray(rgba)
    if mode != "RGBA":
        img = img.convert(mode)
    img.save(path)


def build(jet, name, style_path, out_root, opts):
    cfg = json.loads((HERE / "jets" / f"{jet}.json").read_text(encoding="utf-8"))
    style = json.loads(Path(style_path).read_text(encoding="utf-8"))
    prefix = cfg["prefix"].lower()
    model_dir = HERE / "models" / cfg["model"]
    gltf = model_dir / f"{cfg['model']}.gltf"
    tdir = HERE / "templates" / jet
    if not gltf.exists():
        raise SystemExit(f"missing mesh {gltf}; extract it first (see README)")
    if not tdir.exists():
        raise SystemExit(f"missing template folder {tdir}; copy it from UserSkins/template_{jet}")
    blk, color_path, normal_path = template_files(tdir, prefix)
    dest = out_root / name
    dest.mkdir(parents=True, exist_ok=True)

    tmpl_img = Image.open(color_path)
    tmpl_img.load()
    tmpl = np.asarray(tmpl_img.convert("RGBA"))
    log(f"template {color_path.name}: {tmpl_img.size[0]}x{tmpl_img.size[1]} {tmpl_img.mode}")
    *mesh, normal_png = load_mesh(gltf, f"{prefix}_c")
    pts = mesh[0].reshape(-1, 3)
    bounds = (pts.min(0), pts.max(0))
    game_c = model_dir / f"{prefix}_c.png"
    game_img = Image.open(game_c) if game_c.exists() else None
    size = tuple(int(v) for v in cfg.get("size", tmpl_img.size))
    if game_img is not None:
        size = (max(size[0], game_img.size[0]), max(size[1], game_img.size[1]))
    if size != tmpl_img.size:
        src = game_img if game_img is not None else tmpl_img
        src.load()
        log(f"template is {tmpl_img.size[0]}x{tmpl_img.size[1]}: building at {size[0]}x{size[1]} from {Path(src.filename).name}")
        tmpl = np.asarray(src.convert("RGBA").resize(size, Image.BILINEAR)).copy()
        tmpl[..., 3] = np.asarray(tmpl_img.convert("RGBA").resize(size, Image.NEAREST))[..., 3]
        weather_img = src
    elif tmpl[..., :3].astype(np.float32).mean(-1).std() > 1.0:
        weather_img = tmpl_img
    else:
        weather_img = Image.open(game_c) if game_c.exists() else None
    line_png = model_dir / normal_png if normal_png else None
    out = bake(prefix, cfg, style, mesh, bounds, tmpl, line_png, weather_img, opts)
    save_like(out, tmpl_img.mode, dest / color_path.name)
    del out, tmpl

    extra = []
    for part in cfg.get("parts", []):
        if isinstance(part, str):
            stem = part.lower()
            sources = [(model_dir, gltf)]
            part_cfg = {k: v for k, v in cfg.items() if k != "emblems"}
        else:
            stem = part["name"].lower()
            models = part["model"] if isinstance(part["model"], list) else [part["model"]]
            sources = [(HERE / "models" / m, HERE / "models" / m / f"{m}.gltf") for m in models]
            part_cfg = {"splinter": cfg["splinter"], "accents": list(part.get("accents", []))}
            for _, g in sources:
                if not g.exists():
                    raise SystemExit(f"part {stem}: missing mesh {g}; extract it first (see README)")
        meshes, part_normal = [], None
        for _, g in sources:
            *m, n = load_mesh(g, f"{stem}_c")
            meshes.append(m)
            part_normal = part_normal or n
            if not isinstance(part, str) and part.get("nose"):
                tip = float(m[0][..., 0].max())
                part_cfg["accents"].append({"what": "nose", "min": [tip - float(part["nose"]), -50, -50], "max": [tip + 1, 50, 50]})
        part_mesh = [np.concatenate([m[i] for m in meshes]) for i in range(4)]
        part_dir = sources[0][0]
        src = part_dir / f"{stem}_c.png"
        if not src.exists():
            raise SystemExit(f"part {stem}: missing {src}")
        part_img = Image.open(src)
        part_img.load()
        part_line = part_dir / part_normal if part_normal else None
        out = bake(stem, part_cfg, style, part_mesh, bounds, np.asarray(part_img.convert("RGBA")), part_line, part_img, opts)
        save_like(out, "RGBA", dest / f"{stem}.tga")
        extra.append(f'replace_tex{{\n  from:t="{stem}_c*"\n  to:t="{stem}.tga"\n}}\n')

    if normal_png and (model_dir / normal_png).exists():
        nimg = Image.open(normal_path)
        size = tuple(max(a, b, int(c)) for a, b, c in zip(nimg.size, Image.open(model_dir / normal_png).size, cfg.get("size", (0, 0))))
        save_like(skin_normal(model_dir, normal_png, size, style), nimg.mode, dest / normal_path.name)
        log(f"{normal_path.name}: game normal map at {size[0]}x{size[1]}")
    else:
        shutil.copyfile(normal_path, dest / normal_path.name)
    text = blk.read_text(encoding="utf-8", errors="replace")
    if extra:
        text = text.rstrip("\n") + "\n\n" + "\n".join(extra)
    (dest / blk.name).write_text(text, encoding="utf-8", newline="\n")
    log(f"wrote {dest}")
    return dest


def install(src, name):
    if name.lower().startswith("template_"):
        raise SystemExit(f"refusing to install over {name}: template folders are never overwritten")
    if not USER_SKINS.exists():
        raise SystemExit(f"no UserSkins folder at {USER_SKINS}")
    dest = USER_SKINS / name
    same = [d for d in USER_SKINS.iterdir() if d.name.lower() == name.lower()]
    if same and same[0].name != name:
        tmp = USER_SKINS / f"{name}.rename"
        same[0].rename(tmp)
        tmp.rename(dest)
    dest.mkdir(exist_ok=True)
    keep = {f.name.lower() for f in src.iterdir()}
    for f in dest.iterdir():
        if f.is_file() and f.suffix.lower() in (".tga", ".blk", ".dds") and f.name.lower() not in keep:
            f.unlink()
    for f in src.iterdir():
        shutil.copyfile(f, dest / f.name)
    log(f"installed to {dest}")


def main():
    p = argparse.ArgumentParser(prog="livery.py", description="Generate a livery model (default: the Dragon Crew skin) for one jet.")
    p.add_argument("jet", help="jet name: warthunder/jets/<jet>.json and warthunder/templates/<jet>/")
    p.add_argument("--livery", default="dragon-crew", help="livery model: warthunder/liveries/<livery>/")
    p.add_argument("--name", help="skin folder name; default the style's skin_name with <jet> filled in, plus _lead with --lead")
    p.add_argument("--kills", type=int, help="number of kill marks under the canopy; default: kill_marks count in the jet file")
    p.add_argument("--lead", action="store_true", help="add the flight lead band on the fin")
    p.add_argument("--style", help="style file; default warthunder/liveries/<livery>/style.json")
    p.add_argument("--out", default=str(HERE / "out" / "skins"), help="parent folder for the skin")
    p.add_argument("--install", action="store_true", help="also copy the skin to War Thunder's UserSkins")
    a = p.parse_args()
    art = HERE / "liveries" / a.livery
    if not art.is_dir():
        raise SystemExit(f"no livery model at {art}")
    style_path = Path(a.style) if a.style else art / "style.json"
    style = json.loads(style_path.read_text(encoding="utf-8"))
    name = a.name or style.get("skin_name", "{jet}").replace("{jet}", a.jet) + ("_lead" if a.lead else "")
    if name.lower().startswith("template_"):
        raise SystemExit("the skin name must not start with template_")
    cfg = json.loads((HERE / "jets" / f"{a.jet}.json").read_text(encoding="utf-8"))
    kills = a.kills if a.kills is not None else int(cfg.get("kill_marks", {}).get("count", 0))
    dest = build(a.jet, name, style_path, Path(a.out).resolve(), {"kills": kills, "lead": a.lead, "art": art})
    if a.install:
        install(dest, name)


if __name__ == "__main__":
    main()

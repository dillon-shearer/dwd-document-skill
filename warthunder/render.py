import argparse
import math
import re
import sys
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

VIEWS = [
    ("left", (0, -1, 0), (0, 0, 1), True),
    ("right", (0, 1, 0), (0, 0, 1), True),
    ("top", (0, 0, 1), (0, 1, 0), True),
    ("bottom", (0, 0, -1), (0, -1, 0), True),
    ("front", (1, 0, 0), (0, 0, 1), True),
    ("front_three_quarter", (1.0, -1.1, 0.55), (0, 0, 1), False),
    ("rear_three_quarter", (-1.0, -1.1, 0.55), (0, 0, 1), False),
]

CLOSE = [
    ("close_fin_left", (-4.7, 0.0, 1.5), (0.15, -1.0, 0.12), 4.2),
    ("close_fin_right", (-4.7, 0.0, 1.5), (0.15, 1.0, 0.12), 4.2),
    ("close_nose", (4.2, 0.0, 0.2), (0.9, -1.0, 0.45), 6.5),
    ("close_wing", (-0.4, -2.0, 0.0), (-0.25, -0.55, 1.0), 6.0),
    ("close_rear", (-3.8, 0.0, 0.6), (-1.0, -0.8, 0.5), 6.5),
]

DEFAULT_HIDE = "apu_,aku_,su_apu_,gunfire,jet_flame"


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="render.py", description="Render a War Thunder skin on an extracted glTF mesh.")
    p.add_argument("--mesh", required=True, help="glTF exported by wt-unpack")
    p.add_argument("--color", help="color texture (TGA or PNG), the skin's replacement for <prefix>_c")
    p.add_argument("--skin", help="skin folder; applies every replace_tex in its .blk instead of --color and --normal")
    p.add_argument("--normal", help="Dagor packed normal map (the skin's <prefix>_n.tga); omit to keep the mesh's own")
    p.add_argument("--out", required=True, help="output folder for the PNG renders")
    p.add_argument("--prefix", help="texture prefix to replace, e.g. mig_21_bison; default: color file name without _c")
    p.add_argument("--hide", default=DEFAULT_HIDE, help="comma-separated texture name prefixes whose faces are removed")
    p.add_argument("--width", type=int, default=1600)
    p.add_argument("--height", type=int, default=1000)
    p.add_argument("--samples", type=int, default=32)
    p.add_argument("--close", action="store_true", help="also render close-up views of the fin, nose, wing and rear")
    p.add_argument("--sheet", action="store_true", help="also write contact_sheet.png with every view at half size")
    args = p.parse_args(argv)
    if bool(args.color) == bool(args.skin):
        p.error("give either --color or --skin")
    return args


def image_stem(img):
    name = Path(bpy.path.abspath(img.filepath)).stem if img.filepath else img.name
    return name.lower()


def material_images(mat):
    if not mat or not mat.node_tree:
        return []
    return [n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]


def load_image(path, non_color):
    img = bpy.data.images.load(str(Path(path).resolve()), check_existing=False)
    img.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    return img


def split_packed_normal(path):
    src = load_image(path, True)
    w, h = src.size
    px = np.empty(w * h * 4, dtype=np.float32)
    src.pixels.foreach_get(px)
    px = px.reshape(-1, 4)
    x = px[:, 3] * 2.0 - 1.0
    y = -(px[:, 1] * 2.0 - 1.0)
    z = np.sqrt(np.clip(1.0 - x * x - y * y, 0.0, None))
    ones = np.ones_like(x)
    nrm = np.stack([x * 0.5 + 0.5, y * 0.5 + 0.5, z * 0.5 + 0.5, ones], axis=1)
    mr = np.stack([np.zeros_like(x), 1.0 - px[:, 0], px[:, 2], ones], axis=1)
    out = []
    for name, data in (("skin_normal", nrm), ("skin_metal_rough", mr)):
        img = bpy.data.images.new(name, w, h, alpha=False)
        img.colorspace_settings.name = "Non-Color"
        img.pixels.foreach_set(data.astype(np.float32).ravel())
        img.pack()
        out.append(img)
    bpy.data.images.remove(src)
    return out


def skin_textures(args):
    if not args.skin:
        prefix = (args.prefix or Path(args.color).stem).lower()
        if not args.prefix and prefix.endswith("_c"):
            prefix = prefix[:-2]
        return {prefix: args.color}, ({prefix: args.normal} if args.normal else {})
    folder = Path(args.skin)
    blks = sorted(folder.glob("*.blk"))
    if len(blks) != 1:
        raise SystemExit(f"expected one .blk in {folder}, found {len(blks)}")
    pairs = re.findall(r'from:t="([^"]+)"\s*to:t="([^"]+)"', blks[0].read_text(encoding="utf-8", errors="replace"))
    colors, normals = {}, {}
    for src, dst in pairs:
        src = src.lower().rstrip("*")
        if src.endswith("_c"):
            colors[src[:-2]] = folder / dst
        elif src.endswith("_n"):
            normals[src[:-2]] = folder / dst
    if not colors:
        raise SystemExit(f"{blks[0]} replaces no color texture")
    return colors, normals


def apply_skin(args, meshes):
    colors, normals = skin_textures(args)
    targets = {}
    for stem, path in colors.items():
        img = load_image(path, False)
        img.alpha_mode = "NONE"
        targets[f"{stem}_c"] = img
    for stem, path in normals.items():
        targets[f"{stem}_n_normal"], targets[f"{stem}_n_metal_rough"] = split_packed_normal(path)
    hits = {}
    seen = set()
    for ob in meshes:
        for mat in ob.data.materials:
            for node in material_images(mat):
                stem = image_stem(node.image)
                seen.add(stem)
                if targets.get(stem) is not None:
                    node.image = targets[stem]
                    hits[stem] = hits.get(stem, 0) + 1
    missing = [stem for stem in colors if f"{stem}_c" not in hits]
    if missing and (not args.skin or len(missing) == len(colors)):
        raise SystemExit(f"no material uses {missing[0]}_c; textures in the mesh: {', '.join(sorted(seen))}")
    if missing:
        print("not on this mesh, skipped: " + ", ".join(f"{s}_c" for s in missing))
    for stem in normals:
        if args.skin and stem in missing:
            continue
        if f"{stem}_n_normal" not in hits or f"{stem}_n_metal_rough" not in hits:
            raise SystemExit(f"normal map given but the mesh has no {stem}_n_normal and {stem}_n_metal_rough textures")
    print("skin applied: " + ", ".join(f"{k} x{v}" for k, v in sorted(hits.items())))


def tint_glass(meshes):
    for ob in meshes:
        for mat in ob.data.materials:
            if not mat or "glass" not in mat.name or not mat.node_tree:
                continue
            for node in mat.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    node.inputs["Base Color"].default_value = (0.02, 0.025, 0.03, 1)
                    node.inputs["Roughness"].default_value = 0.05
                    node.inputs["Metallic"].default_value = 0.0
                    node.inputs["Alpha"].default_value = 1.0


def hide_faces(meshes, prefixes):
    prefixes = [p.strip().lower() for p in prefixes.split(",") if p.strip()]
    for ob in meshes:
        drop = set()
        for i, mat in enumerate(ob.data.materials):
            if mat is None:
                continue
            stems = [image_stem(n.image) for n in material_images(mat)]
            if "weapon_fire" in mat.name or any(s.startswith(p) for s in stems for p in prefixes):
                drop.add(i)
        if not drop:
            continue
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in drop], context="FACES")
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bm.to_mesh(ob.data)
        bm.free()


def bounds(meshes):
    pts = [ob.matrix_world @ v.co for ob in meshes for v in ob.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi, pts


def setup_world(scene):
    world = bpy.data.worlds.new("studio")
    scene.world = world
    nt = world.node_tree if world.node_tree else None
    if nt is None:
        world.use_nodes = True
        nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    light = nt.nodes.new("ShaderNodeBackground")
    light.inputs["Color"].default_value = (1, 1, 1, 1)
    light.inputs["Strength"].default_value = 0.7
    grey = nt.nodes.new("ShaderNodeBackground")
    grey.inputs["Color"].default_value = (0.214, 0.214, 0.214, 1)
    grey.inputs["Strength"].default_value = 1.0
    path = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(path.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(light.outputs["Background"], mix.inputs[1])
    nt.links.new(grey.outputs["Background"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])


def add_light(name, kind, energy, direction, size=None):
    data = bpy.data.lights.new(name, kind)
    data.energy = energy
    if size is not None:
        data.angle = size
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = Vector(direction).to_track_quat("-Z", "Y").to_euler()
    return ob


def camera_matrix(forward, up, location):
    f = Vector(forward).normalized()
    r = f.cross(Vector(up)).normalized()
    u = r.cross(f).normalized()
    m = Matrix((r, u, -f)).transposed().to_4x4()
    m.translation = location
    return m


def render_views(scene, meshes, out_dir, close=False):
    lo, hi, pts = bounds(meshes)
    center = (lo + hi) / 2
    radius = max((p - center).length for p in pts)
    aspect = scene.render.resolution_x / scene.render.resolution_y
    cam_data = bpy.data.cameras.new("cam")
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.clip_start = 0.05
    cam_data.clip_end = radius * 20
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    written = []
    for name, d, up, ortho in VIEWS:
        look = -Vector(d).normalized()
        if ortho:
            m = camera_matrix(look, up, center - look * radius * 3)
            r, u = m.col[0].xyz, m.col[1].xyz
            w = max(abs((p - center).dot(r)) for p in pts) * 2
            h = max(abs((p - center).dot(u)) for p in pts) * 2
            cam_data.type = "ORTHO"
            cam_data.ortho_scale = max(w, h * aspect) * 1.08
        else:
            cam_data.type = "PERSP"
            cam_data.lens = 50
            tx = math.tan(cam_data.angle_x / 2)
            ty = tx / aspect
            m = camera_matrix(look, up, center)
            r, u = m.col[0].xyz, m.col[1].xyz
            dist = max(max(-(p - center).dot(look) + abs((p - center).dot(r)) / tx,
                           -(p - center).dot(look) + abs((p - center).dot(u)) / ty) for p in pts)
            m = camera_matrix(look, up, center - look * dist * 1.06)
        cam.matrix_world = m
        path = out_dir / f"{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        written.append(path)
        print(f"wrote {path}")
    for name, target, d, dist in CLOSE if close else []:
        cam_data.type = "PERSP"
        cam_data.lens = 50
        look = -Vector(d).normalized()
        cam.matrix_world = camera_matrix(look, (0, 0, 1), Vector(target) - look * dist)
        path = out_dir / f"{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        written.append(path)
        print(f"wrote {path}")
    return written


def contact_sheet(paths, out_path, cols=4):
    tiles = []
    for path in paths:
        img = bpy.data.images.load(str(path), check_existing=False)
        w, h = img.size
        px = np.empty(w * h * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        bpy.data.images.remove(img)
        a = px.reshape(h, w, 4)[::-1]
        a = a[: h // 2 * 2, : w // 2 * 2].reshape(h // 2, 2, w // 2, 2, 4).mean((1, 3))
        tiles.append(a)
    th, tw = tiles[0].shape[:2]
    rows = (len(tiles) + cols - 1) // cols
    sheet = np.full((rows * th, cols * tw, 4), 0.16, dtype=np.float32)
    sheet[..., 3] = 1.0
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        sheet[r * th:(r + 1) * th, c * tw:(c + 1) * tw] = t
    out = bpy.data.images.new("contact_sheet", cols * tw, rows * th, alpha=False)
    out.pixels.foreach_set(sheet[::-1].ravel())
    out.filepath_raw = str(out_path)
    out.file_format = "PNG"
    out.save()
    print(f"wrote {out_path}")


def main():
    args = parse_args()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=str(Path(args.mesh).resolve()))
    meshes = [ob for ob in scene.objects if ob.type == "MESH"]
    if not meshes:
        raise SystemExit(f"no mesh in {args.mesh}")
    hide_faces(meshes, args.hide)
    apply_skin(args, meshes)
    tint_glass(meshes)
    setup_world(scene)
    add_light("key", "SUN", 3.0, (-0.5, 0.6, -0.8), 0.2)
    add_light("fill", "SUN", 1.2, (0.4, -0.7, -0.3), 0.5)
    add_light("under", "SUN", 0.6, (0.0, 0.2, 1.0), 0.5)
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    written = render_views(scene, meshes, out_dir, args.close)
    if args.sheet:
        contact_sheet(written, out_dir / "contact_sheet.png")
    print(f"done: {len(written)} renders in {out_dir}")


try:
    main()
except SystemExit as e:
    if e.code not in (None, 0):
        print(f"render.py: {e.code}", file=sys.stderr)
        sys.exit(1)
except Exception:
    import traceback

    traceback.print_exc()
    sys.exit(1)

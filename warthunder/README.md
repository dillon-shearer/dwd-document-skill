# War Thunder skin preview

Render a War Thunder aircraft skin to PNG without the game and without a window. An agent repaints the
skin texture, runs one command, looks at the PNGs and repeats. Proven on the MiG-21 Bison.

This folder is unrelated to the doc skill in the rest of the repo. Only the scripts and this README are
committed. `models/`, `templates/`, `out/` and `tools/` hold Gaijin assets, a downloaded tool or build
output and are in `.gitignore`.

| Path | What |
|---|---|
| `render.py` | Blender script: mesh + skin textures in, 7 PNG renders out |
| `uvgrid.py` | Writes a numbered, colored UV test grid to use as a skin texture |
| `tools/wt-unpack/bin/` | The extractor, installed by cargo (not committed) |
| `models/<model>/` | Extracted glTF with UVs and the game's own textures as PNG (not committed) |
| `templates/<skin>/` | Copy of the operator's template from `UserSkins` (not committed) |
| `out/` | Renders (not committed) |

## Needs

- War Thunder installed: `C:\Program Files (x86)\Steam\steamapps\common\War Thunder`. The tools only
  read it. Never write inside it, except under `UserSkins`.
- Blender 5.0: `C:\Program Files\Blender Foundation\Blender 5.0\blender.exe`. Always run it with `-b`.
- Rust (`cargo`) to build the extractor, and Python 3 with Pillow for `uvgrid.py`.

All commands run from the repo root in Git Bash. In PowerShell, put `& ` in front of a quoted program
path and use a backtick instead of `\` at the end of a line.

## One-time setup: build the extractor

```sh
cargo install --git https://github.com/patodois/wt-unpack --rev e2ef494 --locked --root warthunder/tools/wt-unpack wt-unpack
```

Takes about a minute and puts only `wt-unpack.exe` under `warthunder/tools/wt-unpack/bin/`. Tested at
commit `e2ef494` (v0.5.1). Do not clone the source into this repo: `check.py` scans ignored folders too
and fails on non-ASCII text in the wt-unpack sources.

## Extract the Bison mesh

```sh
warthunder/tools/wt-unpack/bin/wt-unpack.exe model "C:/Program Files (x86)/Steam/steamapps/common/War Thunder/content/base/res/aircrafts/ussr_mig_21.grp" mig_21_bison --game "C:/Program Files (x86)/Steam/steamapps/common/War Thunder" -o warthunder/models/mig_21_bison
```

About a minute. Writes `warthunder/models/mig_21_bison/mig_21_bison.gltf` (LOD 0, one UV set) and its
`.bin`, plus every texture the model uses as PNG, the stock skin included (`mig_21_bison_c.png`).

## Render a skin

```sh
"C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b --python-exit-code 1 --python warthunder/render.py -- \
  --mesh warthunder/models/mig_21_bison/mig_21_bison.gltf \
  --color warthunder/templates/mig-21_bison/mig_21_bison.tga \
  --normal warthunder/templates/mig-21_bison/mig_21_bison_n.tga \
  --out warthunder/out/proof/template
```

Writes `left`, `right`, `top`, `bottom`, `front`, `front_three_quarter` and `rear_three_quarter` PNGs
(1600x1000, Cycles on the CPU, mid-grey background, neutral light). Takes about a minute. Exits 1 on any error.
`--python-exit-code 1` must come before `--python`, or Blender exits 0 when the script fails.

Options:

| Option | Meaning |
|---|---|
| `--color` | The skin color texture, TGA or PNG. Replaces the game texture `<prefix>_c` |
| `--normal` | Optional. The skin's packed normal map (`<prefix>_n.tga`). Without it the mesh keeps the game's own |
| `--prefix` | Texture prefix, e.g. `mig_21_bison`. Default: the color file name, minus a trailing `_c` |
| `--hide` | Comma-separated texture name prefixes whose faces are removed. Default `apu_,aku_,su_apu_,gunfire,jet_flame` (missile and rocket launchers, muzzle flash, afterburner flame) |
| `--width`, `--height`, `--samples` | Render size and Cycles samples (default 1600, 1000, 32) |

If no material uses `<prefix>_c`, the script stops and lists the textures the mesh does use.

## Proof renders

```sh
python warthunder/uvgrid.py warthunder/out/uvgrid.tga
"C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b --python-exit-code 1 --python warthunder/render.py -- --mesh warthunder/models/mig_21_bison/mig_21_bison.gltf --color warthunder/out/uvgrid.tga --prefix mig_21_bison --out warthunder/out/proof/uvgrid
"C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b --python-exit-code 1 --python warthunder/render.py -- --mesh warthunder/models/mig_21_bison/mig_21_bison.gltf --color warthunder/models/mig_21_bison/mig_21_bison_c.png --out warthunder/out/proof/game_stock
```

- `out/proof/template/`: the operator's template. It is one flat grey (RGB 80,82,80) with a flat normal
  map, so these show the shape only.
- `out/proof/uvgrid/`: the 16x16 grid. Cells are square on the fuselage, fin and wings.
- `out/proof/game_stock/`: the game's own Bison texture. Roundels, fin flags and green tips sit where
  they belong. Use this set to judge where markings land.

## Which extractor won

`wt-unpack` (https://github.com/patodois/wt-unpack), the first candidate. It built cleanly, read the pack
in place, exported glTF with correct UVs and also wrote the game's textures as PNG, so the stock skin could
be rendered as a cross-check. Because it worked, the other candidates (wt-asset-explorer,
Dagor-Asset-Explorer, grp-blender-toolkit) were not tried.

## Another jet

1. Find the pack and model: the packs are `content/base/res/aircrafts/*.grp`.
   `wt-unpack grp <pack.grp>` lists the models; the model name is the one without a `_char`,
   `_skeleton`, `_anim` or `_animtree` suffix.
2. The texture prefix is in the template's `.blk`: `replace_tex{ from:t="<prefix>_c*" }`. The game makes
   templates in `UserSkins/template_<jet>/`; copy them to `warthunder/templates/<jet>/` and leave the
   original alone.
3. Export with the `model` command above, then render. If the script says no material uses `<prefix>_c`,
   pass `--prefix`, using one of the names it lists.
4. LOD 0 holds every pylon and launcher at once. Look at the PNG names in `models/<model>/` and add
   prefixes to `--hide` for stores you do not want in the shot.
5. render.py assumes the nose points to +X and the top to +Z after import. wt-unpack exports every vehicle
   that way.
6. Render `uvgrid.py`'s grid first. Labels that read backwards mark UV islands that are mirrored; on the
   Bison these are the right side of the fuselage and fin, both wing lower surfaces and one tailplane
   lower surface. Text painted on those islands must be flipped in the texture.

## Skin texture format

- Color (`<prefix>.tga`): RGBA TGA at the template's size (4096x4096 for the Bison). TGA origin
  (top or bottom) does not matter; Blender reads both.
- Normal (`<prefix>_n.tga`): Dagor's packed layout. R is smoothness, G is the normal's Y (DirectX, green
  down), B is metalness, A is the normal's X. render.py turns it into a normal map and a roughness/metal
  map. A flat one is R 0, G 128, B 0, A 128.

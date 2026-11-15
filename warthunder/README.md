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
| `livery.py` | Generates the 0OPS livery for one jet (see below) |
| `livery/style.json`, `livery/insignia.svg` | The livery's shared colors and the unit shield |
| `jets/<jet>.json` | Per-jet placement for the livery |
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
| `--skin` | A skin folder instead of `--color` and `--normal`: applies every `replace_tex` in its `.blk` |
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

## 0OPS livery

The 0OPS squadron livery, generated per jet: solid near-black (`#101113`) with the panel lines of the
game texture, a unit shield (white slashed zero) on each side of the fin, white wingtips and tailplane tips,
white nose cone, pitot boom and fin tip, a darker anti-glare panel ahead of the windscreen, "0OPS" (slashed
zero) under the canopy with kill marks above it, and the drop tanks, missiles and rockets in black with
white noses. The design went through several rounds with the operator in game; the colors live in
`livery/style.json` and the placements in `jets/<jet>.json`.

Generate the Bison skin (under a minute, exits 0):

```sh
python warthunder/livery.py mig-21_bison
```

Writes `warthunder/out/skins/0ops_mig-21_bison/`: `mig_21_bison.tga` (same size and bit depth as the
template), `mig_21_bison_n.tga` (the template's, copied byte for byte), `mig-21_bison.blk`, and one TGA per
extra part and store (see `parts` below). Needs Python 3 with numpy, scipy and Pillow.

| Option | Meaning |
|---|---|
| `--install` | Also copy the folder to `UserSkins\<name>`. Names starting with `template_` are refused, so the game's template folders are never touched |
| `--name` | Skin folder name. Default `0ops_<jet>`, or `0ops_<jet>_lead` with `--lead` |
| `--kills N` | Number of kill marks. Default: `kill_marks.count` in the jet file |
| `--lead` | Add the flight lead band across the fin |
| `--style`, `--out` | Another style file, another parent folder for the skin |

Render it (`-t 4` keeps Blender to four CPU threads so the PC stays usable; the default `--hide` leaves the
launch rails out, `--hide gunfire,jet_flame` shows them):

```sh
"C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b -t 4 --python-exit-code 1 --python warthunder/render.py -- --mesh warthunder/models/mig_21_bison/mig_21_bison.gltf --skin warthunder/out/skins/0ops_mig-21_bison --out warthunder/out/renders/0ops_mig-21_bison
```

The same `--skin` folder renders a store, e.g. `--mesh warthunder/models/su_490l_drop_tank/su_490l_drop_tank.gltf`;
textures that are not on the mesh are skipped.

### How it works

livery.py reads the glTF and draws every triangle that uses a texture into texture space, so each texel
knows its 3D point on the model. Every marking is worked out from that 3D point and written back to the
texel. That is why markings land in the same place whatever the UV layout, and do not break at UV seams.
Texels no triangle uses are filled from the nearest used texel, so edges do not bleed at a distance.

Coordinates are model space after import, in meters: X to the nose, Z up, Y across (the `right` render
looks at the +Y side). The Bison runs from X -6.8 (tail) to 8.5 (pitot); the wingtips are at Y +-3.58.
Store models have their own space, nose at +X.

- Base: `base`. Panel lines and rivets come from the game's own normal map (`panel_lines`, negative
  darkens). Weathering comes from the template color if it has any detail, else from the game color texture
  with its roundels, flags and stencils masked out (`weathering`). The Bison template is one flat grey, so
  the game textures carry all the detail.
- Splinter: 3D Voronoi cells in two shades, `splinter` vs `base`. Set to the same color it is off; that is
  the current look. The operator tried a two-tone splinter in game and dropped it.
- Fin badge: `livery/insignia.svg` (elements `shield`, `zero`, `slash`; path commands M L H V C Q Z only),
  projected along Y onto each fin side and drawn from its outline, so edges are sharp at any texture size.
  Each side is drawn as seen from that side, so the slash runs lower left to upper right on both.
- Wingtips: white where the distance from the centerline is beyond `tip - width`, inside the `x` and `z`
  ranges: a straight chordwise cut, same width both sides, top and bottom. One entry per surface (wings,
  tailplanes).
- Accents: boxes in model space painted `accent` (or the style color named by `color`, e.g. the
  anti-glare panel). With `whole`, only parts (glTF primitives) that sit fully inside the box are painted.
- Lettering: drawn with `font` (Bahnschrift SemiBold), slashed zero optional, projected along Y like the
  badge. livery.py stops if the lettering touches texture space both sides share. On the Bison the nose sides
  ahead of X 4.75 share mirrored UVs, so the lettering sits under the canopy; text there would read backwards
  on one side. The fin sides have their own UVs, so the badge is not mirrored either.
- Kill marks: `livery/kill.svg` (element `kill`), a row running aft from `start`.
- Keep: parts fully inside a `keep` box stay as the template has them (the Bison's wheels, retracted inside
  the fuselage, and the exhaust nozzle petals). Canopy glass is its own material and is never touched.
- Parts: airframe pieces and stores with their own game textures, which the game's template does not cover.
  Each is baked at the game texture's size, written as `<name>.tga` and added to the `.blk` with its own
  `replace_tex`. The operator confirmed in game that the drop tanks pick up the skin this way.

### Files

`livery/style.json` (shared): `base`, `splinter`, `white`, `accent`, `antiglare`, `badge_fill` (hex colors),
`badge_outline` (shield outline width in insignia units, drawn inside the shield edge), `panel_lines`
(0-255 levels added on the strongest line; negative darkens), `weathering` (0-1), `font`.

`jets/<jet>.json` (the only per-jet work):

| Key | Meaning |
|---|---|
| `model`, `prefix` | `models/<model>/<model>.gltf`, and the texture prefix from the template `.blk` |
| `splinter` | `cell` size in m (X, Y, Z), `seed`, `mirror` (pattern mirrored across the centerline, needed when small parts share mirrored UVs), `share` of cells in `base` |
| `fin_badge` | `center` [X, Z] of the badge on the fin, `height` in m, `max_offset` (how far from Y 0 the fin skin may be) |
| `wingtips` | List of `tip` (distance of the tip from the centerline), `width`, `x` and `z` ranges that hold the surface |
| `accents` | List of boxes (`min`, `max`), optional `whole` and `color` |
| `lettering` | `text`, `slashed_zero`, `center` [X, Z], `height` (letter height in m), `max_offset` |
| `kill_marks` | `count`, `start` [X, Z] (front of the row), `height`, `gap`, `max_offset` |
| `lead_band` | `z` and `x` ranges of the fin band, `max_offset` |
| `keep` | Boxes; parts fully inside stay as the template has them |
| `parts` | Texture names (without `_c`) on the jet mesh, or `{name, model, nose}` for a store: `model` is one extracted model or a list sharing the texture, `nose` paints the front that many meters `accent` |

### Stores

Weapons are separate models. Find what a jet carries in `aces.vromfs.bin`:
`gamedata/flightmodels/<jet>.blk` lists the weapon blks, and each weapon blk names its `mesh`. Extract each
mesh from `content/base/res/aces.grp` with the `model` command, into `warthunder/models/<mesh>/`:

```sh
warthunder/tools/wt-unpack/bin/wt-unpack.exe cat "C:/Program Files (x86)/Steam/steamapps/common/War Thunder/aces.vromfs.bin:gamedata/weapons/rocketguns/su_r_73e.blk"
warthunder/tools/wt-unpack/bin/wt-unpack.exe model "C:/Program Files (x86)/Steam/steamapps/common/War Thunder/content/base/res/aces.grp" su_r_73 --game "C:/Program Files (x86)/Steam/steamapps/common/War Thunder" -o warthunder/models/su_r_73
```

The Bison uses `su_490l_drop_tank`, `su_r_73`, `su_r_27r_missile`, `su_r_27t_missile`, `su_r_77_missile`
and `su_s_24_rocket`.

### Another jet

1. Extract the mesh and copy the template as in "Another jet" above, plus the stores.
2. Copy `jets/mig-21_bison.json` to `jets/<jet>.json`. The file name must match the template folder.
3. Find the numbers: render `uvgrid.py`'s grid and read the mesh bounds. The fin badge center is the middle
   of the fin's side area; a wingtip `tip` is the largest distance of that surface from the centerline. Put
   lettering where the uvgrid labels read correctly on both sides.
4. List the jet's other airframe textures and stores under `parts` (PNG names in `models/<model>/`).
5. Run `livery.py`, render with `--skin`, look, adjust.

# War Thunder skin preview

Render a War Thunder aircraft skin to PNG without the game and without a window. An agent repaints the
skin texture, runs one command, looks at the PNGs and repeats. Proven on the MiG-21 Bison.

Making or changing the 0OPS squadron skin (the Dragon Crew skin, `0OPS-Dragon-Crew-<jet>`) on any plane:
start with `liveries/dragon-crew/MODEL.md`, then "Dragon Crew skin (0OPS livery)" and "Apply to a new jet"
below.

This folder is unrelated to the doc skill in the rest of the repo. Only the scripts and this README are
committed. `models/`, `templates/`, `out/` and `tools/` hold Gaijin assets, a downloaded tool or build
output and are in `.gitignore`.

| Path | What |
|---|---|
| `render.py` | Blender script: mesh + skin textures in, 7 PNG renders out |
| `uvgrid.py` | Writes a numbered, colored UV test grid to use as a skin texture |
| `livery.py` | Generates the Dragon Crew skin (or another livery model) for one jet (see below) |
| `fit.py` | Prints a jet's flat spine width and wing leading edge and draws the dragon on its top view, to place it fast |
| `liveries/dragon-crew/` | The Dragon Crew skin model: `MODEL.md` (design rules, method, gotchas), `style.json`, `insignia.svg`, `dragon.svg`, `kill.svg` |
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
In this studio light any dielectric black reflects about 4% of the white dome, so near-black paint renders as
dark grey (about 50 of 255). That is the light, not the texture.
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
| `--close` | Also render five close-ups: both fin sides, nose, wing top, rear (`close_*.png`). Positions are in Bison meters |
| `--sheet` | Also write `contact_sheet.png`, every view at half size, four per row |

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
   original alone. The normal map's name can differ from the prefix when the game shares it between
   versions (F-5E FCU: color `f_5e_fcu_thailand_c*`, normal `f_5e_aidc_n*`); then set `normal` in the jet file.
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

## Dragon Crew skin (0OPS livery)

The 0OPS squadron's Dragon Crew skin, generated per jet, skin folder `0OPS-Dragon-Crew-<jet>`: one flat
black (`#0a0a0b`), satin finish, the game's own panel lines and rivets. White (`#f0f0f0`) only for: a small
unit shield on each side of the fin (slashed zero in a DIN-style stadium, black field, thin outline), "0OPS"
and kill marks under the canopy on both sides, thin wingtips on both wings, and a top-view dragon on the top
surfaces only (body on the spine, wings spread out over both wings). No numbers, stencils or other color.
Stores and pylons get the same black. The design rules, the method and the gotchas are in
`liveries/dragon-crew/MODEL.md`; read it before applying the skin to another jet. The shared art and style
live in `liveries/dragon-crew/` and the placements in `jets/<jet>.json`. The Bison was finished by render
rounds; `out/rounds/<n>/note.txt` says what each round changed.

Generate the Bison skin (under a minute, exits 0):

```sh
python warthunder/livery.py mig-21_bison
```

Writes `warthunder/out/skins/0OPS-Dragon-Crew-mig-21_bison/`: `mig_21_bison.tga` (same size and bit depth as the
template), `mig_21_bison_n.tga`, `mig-21_bison.blk`, and one TGA per extra part and store (see `parts`
below). The output is deterministic: the same inputs give the same file hash. Needs Python 3 with numpy, scipy
and Pillow.

The normal TGA is the game's own normal map (from `models/<model>/<prefix>_n_normal.png` and
`_n_metal_rough.png`, put back into Dagor's packed layout at the template size), with smoothness and
metalness from the style. The template's own normal map is flat, and shipping it would erase the panel lines
in game.

| Option | Meaning |
|---|---|
| `--install` | Also copy the folder to `UserSkins\<name>`. Names starting with `template_` are refused, so the game's template folders are never touched. A folder with the same name in another case is renamed to `<name>`; old `.tga`, `.blk` and `.dds` files the new skin does not have are removed from it |
| `--livery` | Livery model, a folder under `liveries/`. Default `dragon-crew` |
| `--name` | Skin folder name. Default the style's `skin_name` with `{jet}` filled in (`0OPS-Dragon-Crew-<jet>`), plus `_lead` with `--lead` |
| `--kills N` | Number of kill marks. Default: `kill_marks.count` in the jet file |
| `--lead` | Add the flight lead band across the fin |
| `--style`, `--out` | Another style file (default `liveries/<livery>/style.json`), another parent folder for the skin |

Render it (`-t 4` keeps Blender to four CPU threads so the PC stays usable; the default `--hide` leaves the
launch rails out, `--hide gunfire,jet_flame` shows them):

```sh
"C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b -t 4 --python-exit-code 1 --python warthunder/render.py -- --mesh warthunder/models/mig_21_bison/mig_21_bison.gltf --skin warthunder/out/skins/0OPS-Dragon-Crew-mig-21_bison --out warthunder/out/final --close --sheet
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
- Splinter: 3D Voronoi cells in two shades, `splinter` vs `base`. Cell walls are planes, so edges are
  straight and hard, and with `mirror` the pattern matches across the centerline. When both are the same
  color (the Dragon Crew skin) the step is skipped and the skin is one flat color.
- Fin badge: `insignia.svg` in the livery folder (elements `shield`, `zero`, `slash`; path commands M L H V C Q Z only),
  projected along Y onto each fin side and drawn from its outline, so edges are sharp at any texture size.
  Each side is drawn as seen from that side, so the slash runs lower left to upper right on both.
- Wingtips: white where the distance from the centerline is beyond `tip - width`, inside the `x` and `z`
  ranges: a straight chordwise cut, same width both sides, top and bottom. One entry per surface (wings,
  tailplanes).
- Emblems: a shape from `<svg>.svg` in the livery folder (element `emblem`, path commands as for the badge),
  seen from above with the nose up, projected along Z onto the top and/or bottom. Only faces whose geometric
  normal points up (or down) by more than `min_facing` take it, so nothing runs down the fuselage sides, and
  only the topmost surface in each `cell` (m, default 0.02) within `depth_tol` (m, default 0.03) of the top,
  so nothing underneath (a lower wing surface, a pylon) catches it. `bands` limits it to distances from the
  centerline: on the Bison the flat spine (0 to 0.14 m) and the wings (beyond 0.58 m), with a clean break
  over the round fuselage shoulders, where any paint shows in the side view. Keep emblems mirror-symmetric:
  parts of the Bison share mirrored UVs. Emblems are drawn on the main texture only, not on parts.
- Accents: boxes in model space painted `accent` (or the style color named by `color`, e.g. the
  anti-glare panel). With `whole`, only parts (glTF primitives) that sit fully inside the box are painted.
- Lettering: drawn with `font` (Bahnschrift SemiBold), slashed zero optional, projected along Y like the
  badge. livery.py stops if the lettering touches texture space both sides share. On the Bison the nose sides
  ahead of X 4.75 share mirrored UVs, so the lettering sits under the canopy; text there would read backwards
  on one side. The fin sides have their own UVs, so the badge is not mirrored either.
- Kill marks: `kill.svg` in the livery folder (element `kill`), a row running aft from `start`.
- Keep: parts fully inside a `keep` box stay as the template has them (the Bison's wheels, retracted inside
  the fuselage, and the exhaust nozzle petals). Canopy glass is its own material and is never touched.
- Parts: airframe pieces and stores with their own game textures, which the game's template does not cover.
  Each is baked at the game texture's size, written as `<name>.tga` and added to the `.blk` with its own
  `replace_tex`. The operator confirmed in game that the drop tanks pick up the skin this way.

### Files

`liveries/<livery>/style.json` (shared): `name` (the model's name), `skin_name` (default skin folder, `{jet}` is
filled in), `base`, `splinter`, `white`, `accent`, `antiglare`, `badge_fill` (hex colors),
`badge_outline` (shield outline width in insignia units, drawn inside the shield edge), `panel_lines`
(0-255 levels added on the strongest line; negative darkens, positive lightens the seams so they read on
black), `weathering` (0-1), `font`, and the finish written to the normal TGA: `smoothness` or
`smoothness_scale` (a fixed 0-1 value, or a factor on the game's own smoothness map, which keeps its
variation), `metalness` or `metalness_scale` (same). Without them the game's values are used.

`liveries/<livery>/insignia.svg`: `zero` may be an `ellipse` or a closed `path` (the stadium zero is a path).

`jets/<jet>.json` (the only per-jet work):

| Key | Meaning |
|---|---|
| `model`, `prefix` | `models/<model>/<model>.gltf`, and the texture prefix from the template `.blk` |
| `normal` | Optional. The normal map's texture name from the template `.blk` (without `*`), when it is not `<prefix>_n`, e.g. `f_5e_aidc_n` on the F-5E FCU |
| `splinter` | `cell` size in m (X, Y, Z), `seed`, `mirror` (pattern mirrored across the centerline, needed when small parts share mirrored UVs), `share` of cells in `base` |
| `fin_badge` | `center` [X, Z] of the badge on the fin, `height` in m, `max_offset` (how far from Y 0 the fin skin may be) |
| `emblems` | List of `svg` (file name in the livery folder), `center` [X, Y] of the shape's box, `length` (nose to tail, m), `surfaces` (`top`, `bottom`), `min_facing` (default 0.2), optional `bands`, `cell`, `depth_tol` and `color` |
| `wingtips` | List of `tip` (distance of the tip from the centerline), `width`, `x` and `z` ranges that hold the surface |
| `accents` | List of boxes (`min`, `max`), optional `whole` and `color` |
| `lettering` | `text`, `slashed_zero`, `center` [X, Z], `height` (letter height in m), `max_offset` |
| `kill_marks` | `count`, `start` [X, Z] (front of the row), `height`, `gap`, `max_offset` |
| `lead_band` | `z` and `x` ranges of the fin band, `max_offset` |
| `keep` | Boxes; parts fully inside stay as the template has them |
| `parts` | Texture names (without `_c`) on the jet mesh, or `{name, model, nose, tex}` for a store: `model` is one extracted model or a list sharing the texture, `nose` (optional) paints the front that many meters `accent`, `tex` (optional) is the game texture name when it does not end in `_c` (e.g. `us_750lb_m117_cone_a`; `model` may then be the jet's own model). The Bison's stores have no `nose`: plain black |

### Stores

Weapons are separate models. Find what a jet carries in `aces.vromfs.bin`:
`gamedata/flightmodels/<jet>.blk` lists the weapon blks, and each weapon blk names its `mesh`. Extract each
mesh from `content/base/res/aces.grp` with the `model` command, into `warthunder/models/<mesh>/`:

```sh
warthunder/tools/wt-unpack/bin/wt-unpack.exe cat "C:/Program Files (x86)/Steam/steamapps/common/War Thunder/aces.vromfs.bin:gamedata/weapons/rocketguns/su_r_73e.blk"
warthunder/tools/wt-unpack/bin/wt-unpack.exe model "C:/Program Files (x86)/Steam/steamapps/common/War Thunder/content/base/res/aces.grp" su_r_73 --game "C:/Program Files (x86)/Steam/steamapps/common/War Thunder" -o warthunder/models/su_r_73
```

The Bison uses `su_490l_drop_tank`, `su_r_73`, `su_r_27r_missile`, `su_r_27t_missile`, `su_r_77_missile`
and `su_s_24_rocket`. Some stores are not in `aces.grp`: if `model` says not found, look in
`content/base/res/aircrafts/air.grp` (the F-5E's `aero_7a` and `lau_10a` rocket pods are there).

### F-5E FCU (Thailand)

The second build, `jets/f-5e_fcu_thailand.json` (template `template_f-5e_fcu_thailand`, model
`f_5e_fcu_thailand` in `usa_f_5.grp`). Final renders in `out/final_f-5e_fcu_thailand/` (with
`compare_top.png` next to the Bison), rounds in `out/rounds_f-5e_fcu_thailand/<n>/note.txt`.

```sh
mkdir -p warthunder/templates/f-5e_fcu_thailand
cp "C:/Program Files (x86)/Steam/steamapps/common/War Thunder/UserSkins/template_f-5e_fcu_thailand/"* warthunder/templates/f-5e_fcu_thailand/
WT="C:/Program Files (x86)/Steam/steamapps/common/War Thunder"
warthunder/tools/wt-unpack/bin/wt-unpack.exe model "$WT/content/base/res/aircrafts/usa_f_5.grp" f_5e_fcu_thailand --game "$WT" -o warthunder/models/f_5e_fcu_thailand
for m in us_aim_9p4_sidewinder python_3 us_agm_65b us_150gal_early_drop_tank us_150gal_fuse_drop_tank us_500lb_mk_82_ldgp us_500lb_mk_82_snakeye_na us_750lb_m117_cone_45 750_lb_blu_27_unfinned us_1000lb_mk_83_ldgp us_2000lb_mk_84_ldgp; do warthunder/tools/wt-unpack/bin/wt-unpack.exe model "$WT/content/base/res/aces.grp" $m --game "$WT" -o warthunder/models/$m; done
for m in aero_7a lau_10a; do warthunder/tools/wt-unpack/bin/wt-unpack.exe model "$WT/content/base/res/aircrafts/air.grp" $m --game "$WT" -o warthunder/models/$m; done
python warthunder/livery.py f-5e_fcu_thailand
"C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b -t 4 --python-exit-code 1 --python warthunder/render.py -- --mesh warthunder/models/f_5e_fcu_thailand/f_5e_fcu_thailand.gltf --skin warthunder/out/skins/0OPS-Dragon-Crew-f-5e_fcu_thailand --out warthunder/out/final_f-5e_fcu_thailand --sheet
python warthunder/livery.py f-5e_fcu_thailand --install
```

Generating takes about two and a half minutes. Do not use `--close` here (its close-ups are placed for
the Bison).

### Another jet

1. Extract the mesh and copy the template as in "Another jet" above, plus the stores.
2. Copy `jets/mig-21_bison.json` to `jets/<jet>.json`. The file name must match the template folder.
3. Find the numbers: render `uvgrid.py`'s grid and read the mesh bounds. The fin badge center is the middle
   of the fin's side area; a wingtip `tip` is the largest distance of that surface from the centerline. Put
   lettering where the uvgrid labels read correctly on both sides.
4. List the jet's other airframe textures and stores under `parts` (PNG names in `models/<model>/`).
5. Run `livery.py`, render with `--skin`, look, adjust.

## Apply to a new jet

The Dragon Crew skin is shared; a new jet needs only its placement file. Read
`liveries/dragon-crew/MODEL.md` first: the design rules, how to fit the dragon, the gotchas and the review
checklist. Commands run from the repo root in Git Bash; `<jet>` is the template name (e.g. `f-5e`),
`<model>` the mesh name.

1. Get the template in game: open the jet in War Thunder, Customization, and make a user skin template.
   The game writes `UserSkins/template_<jet>/`. Copy it and leave the original alone:
   ```sh
   mkdir -p warthunder/templates/<jet>
   cp "C:/Program Files (x86)/Steam/steamapps/common/War Thunder/UserSkins/template_<jet>/"* warthunder/templates/<jet>/
   ```
2. Extract the mesh (pack and model name as in "Another jet" above), plus any stores it carries:
   ```sh
   warthunder/tools/wt-unpack/bin/wt-unpack.exe model "C:/Program Files (x86)/Steam/steamapps/common/War Thunder/content/base/res/aircrafts/<pack>.grp" <model> --game "C:/Program Files (x86)/Steam/steamapps/common/War Thunder" -o warthunder/models/<model>
   ```
3. Write the placement file `warthunder/jets/<jet>.json`, starting from `jets/mig-21_bison.json`: set
   `model` and `prefix`, the fin badge `center` and `height`, the wingtip `tip` and `x`/`z` ranges, the
   dragon `center`, `length` and `bands` (spine half-width, wing root distance; see "Fitting the dragon"
   in MODEL.md), the `lettering` and `kill_marks` under the canopy, `keep` boxes for wheels and nozzle, and
   `parts` (other airframe textures and stores). Render the UV grid first to find the numbers (see "Proof
   renders"). For the dragon, `fit.py` prints the flat spine width and the wing leading edge and writes
   `warthunder/out/fit/<jet>_top.png` with the dragon drawn as it will be painted, in seconds:
   ```sh
   python warthunder/fit.py <jet>
   python warthunder/fit.py <jet> --center -0.4 0 --length 2.5
   ```
4. Run the command, render, look (MODEL.md review checklist), adjust the placement, repeat; then install:
   ```sh
   python warthunder/livery.py <jet>
   "C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b --python-exit-code 1 --python warthunder/render.py -- --mesh warthunder/models/<model>/<model>.gltf --skin warthunder/out/skins/0OPS-Dragon-Crew-<jet> --out warthunder/out/renders/<jet> --close --sheet
   python warthunder/livery.py <jet> --install
   ```
   In game: open the jet, Customization, pick the user skin `0OPS-Dragon-Crew-<jet>`.

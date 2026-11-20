# Dragon Crew skin

The 0OPS squadron's standard War Thunder skin, for every plane. Call it the Dragon Crew skin. The skin
folder, which is also its name in the game's skin list, is `0OPS-Dragon-Crew-<jet>`, e.g.
`0OPS-Dragon-Crew-mig-21_bison` (`<jet>` is the template name the game uses, from
`UserSkins/template_<jet>`).

This folder is the model. It holds everything that is the same on every plane:

| File | What |
|---|---|
| `MODEL.md` | This spec: the design rules, the method, how to fit it to a plane, the gotchas, the review checklist |
| `style.json` | Name, default skin folder, colors and finish |
| `insignia.svg` | The unit shield with the slashed zero (fin badge) |
| `dragon.svg` | The top-view dragon (opens in a browser as a preview) |
| `kill.svg` | One kill mark |

A plane adds one placement file, `warthunder/jets/<jet>.json`, and nothing else. `warthunder/livery.py`
builds the skin from the model plus the placement; nothing is painted by hand. The finished reference
build is the MiG-21 Bison (`jets/mig-21_bison.json`, renders in `warthunder/out/final/`). The README
(`warthunder/README.md`) has every command and every key; this file says what to build and why.

## Settings at a glance

Every plane gets exactly what the finished MiG-21 Bison has. The operator signed it off on 2026-11-20
("the mig is good") so that no ticket has to ask again. Build exactly this list; do not add, drop or
change an item without the operator saying so.

| Item | Setting |
|---|---|
| Skin name | `0OPS-Dragon-Crew-<jet>` (zero, not the letter O) |
| Base | One flat black `#0a0a0b` everywhere, stores and pylons too. No second shade, no camo |
| Colors | Black and white `#f0f0f0` only |
| Finish | Satin; game panel lines and rivets visible |
| Fin | One white-outlined black shield with a white slashed zero, centered on each side. Nothing else on the fin (no white fin tip) |
| By the pilot | "0OPS" (Bahnschrift, slashed zero) and 5 white kill marks, under the canopy, both sides |
| Wingtips | White, both wings, top and bottom |
| Tailplane tips | White, both tailplanes, top and bottom |
| Nose cone | White: the cone only (radome or intake shock cone), not the rest of the nose |
| Pitot | White: the probe or antenna boom sticking out of the nose |
| Dragon | White top-view dragon (`dragon.svg`) on the top surfaces only, wings straight out to the sides |
| Stores | Plain black, no white noses |
| Not painted | Canopy glass, tyres and wheels, exhaust nozzle petals |
| Nothing else | No numbers, stencils, cheat line, anti-glare panel or other markings |

## Design rules

The operator chose all of these over several review rounds (2026-11-14 to 2026-11-20). They are fixed.
Ask the operator before changing any of them, and do not add anything that is not here.

1. Base: one flat black `#0a0a0b` on every painted surface, pylons, launchers, gun pods, drop tanks and
   missiles included. No second shade, no splinter camo, no gradient. (`splinter` = `base` in
   `style.json`; livery.py then skips the splinter step.)
2. Colors: black and white `#f0f0f0` only. No red, no gold, no other accent.
3. Finish: satin, not gloss and not matte. `smoothness_scale` 0.6 (keeps the game's own smoothness
   variation, so rivets and wear still read), `metalness` 0. The game's own panel lines and rivets stay,
   lightened a little (`panel_lines` +5) so they read on black. Weathering 0.12.
4. Fin badge: one small unit shield, centered on each side of the fin, same height on both sides,
   about 0.5 m tall on a fighter. Black shield (`badge_fill`), thin white outline (`badge_outline` 3.5),
   white slashed zero shaped like the Bahnschrift zero (a stadium), slash running lower left to upper
   right as seen from each side. Nothing else on the fin.
5. Pilot marking, on both sides, on the fuselage just under the canopy by the pilot: "0OPS" in
   Bahnschrift with a slashed zero (letter height 0.14 m on the Bison), and a row of 5 white kill marks
   (0.09 m tall) just above it, starting a little ahead of the text and running aft. Both must read the
   right way round on both sides (see the mirrored-UV gotcha).
6. Wingtips: a thin white chordwise band at the tip of each main wing (0.3 m on the Bison) and of each
   tailplane (0.2 m on the Bison), equal on both sides, top and bottom. Cut straight, parallel to the
   centerline.
7. Nose: the nose cone white, the cone part only (the radome, or the intake shock cone on a jet like the
   MiG-21), not the rest of the nose. The pitot or probe boom sticking out of the nose white. Both are
   whole parts, set as `accents` in the jet file (`whole` true for the cone, so only the part that sits
   fully inside the box is painted).
8. Dragon: one solid white top-view dragon on the TOP surfaces only. Never on the underside, never on
   the fuselage sides. See "The dragon".
9. Nothing else: no numbers, no stencils, no cheat line, no anti-glare panel in another shade.
10. Not painted: canopy glass (its own material, never touched), tyres and wheels, the exhaust nozzle
   petals (kept as the template has them with `keep` boxes).

Rejected on the way, so do not bring them back: a ghost splinter in a second black; a dragon on the
underside; long thin swept "lightning bolt" wings with sawtooth spikes; a long arrow-like body; wings
swept back along the wing leading edge; heavy fan or feather wings. An earlier session also dropped the
"0OPS" lettering and kill marks, the tailplane tips, the white nose cone and the white pitot on its own;
the operator wanted all of them back. Never drop a marking the operator has not removed. A white fin tip
and white store noses were in the first build only; the operator chose to leave both out (2026-11-20).

## The dragon

Drawn once, in `dragon.svg`: element `emblem`, one closed path (commands M L Q Z), top view, nose up,
mirror-symmetric about x = 0. On the Bison 1 SVG unit = 1 cm at the jet's size, but livery.py rescales
it to the jet file's `length`, so the units only matter for reading the numbers below.

Look (from the operator's reference picture, a classic top-view dragon in flight):

- Small head toward the jet's nose: a short wedge snout, cheeks, and two horns sweeping back and out.
- Thin neck, then a chest as wide as the spine allows, a narrow waist, hips with short leg nubs.
- Wings spread almost straight out to the sides (not swept back with the wing leading edge). Each wing:
  the leading edge rises from the shoulder to a raised wrist with a small claw, then runs out with a
  slight droop to a pointed tip. The trailing edge is scalloped: from the tip, 5 finger points (the tip
  plus 4 more) with concave curves between them, the deepest at mid-span, ending at the hip.
- Long thin tail, tapering, ending in a diamond spade.
- Solid white, no internal lines.

Proportions in `dragon.svg` (fractions of the nose-to-spade length L, measured from the head tip):
shoulders and wing leading edge root at 0.31 L; wrist 0.22 L behind the head tip; wing tip 0.37 L,
deepest trailing-edge point 0.77 L; hips 0.55 L; spade from 0.84 L to 1.0 L. Half-span (centerline to
wing tip) 0.94 L. Body half-width: head 0.035 L, horns 0.055 L, neck 0.012 L, chest and hips 0.053 L,
tail 0.016 to 0.008 L, spade 0.045 L.

The wing joins the body through a thin bridge across the fuselage shoulder. That bridge is masked out by
`bands` (it would show in the side view), so the painted wing starts at the wing root and the torso keeps
its own outline. Keep that structure if you redraw it: torso outline, out to the wing through a bridge a
few cm wide at the shoulder, around the wing, back to the hip at the wing root, back to the torso through
the bridge, then the tail.

## Method

livery.py maps every texel of the skin to its 3D point on the model, then picks its color from that
point. So every marking is placed in model meters (X to the nose, Y across, Z up; `right` render looks at
+Y), not in texture space. Markings do not break at UV seams and the same placement works whatever the
UV layout. Each marking is projected:

- fin badge, "0OPS", kill marks: along Y onto each side, drawn as seen from that side;
- dragon: straight down along Z, only onto surfaces that face up by more than `min_facing` and are the
  topmost surface at that spot (a 2 cm height map), and only inside the `bands`;
- wingtips: by distance from the centerline, inside an X and Z box per surface.

Then the game's own panel lines and the finish are added, texels no triangle uses are filled from the
nearest used texel, and a normal TGA is rebuilt from the game's normal map. Parts with their own
textures (pylons, stores) are baked the same way into their own TGAs and added to the `.blk`.

## Apply to a new plane

Commands run from the repo root in Git Bash. Follow `warthunder/README.md` "Apply to a new jet" for the
exact commands; in short:

1. Copy the game's template `UserSkins/template_<jet>/` to `warthunder/templates/<jet>/` (the operator
   makes the template in game: open the jet, Customization, create a user skin template). Never edit the
   template folder in `UserSkins`.
2. Extract the mesh and its stores with wt-unpack into `warthunder/models/`.
3. Copy `jets/mig-21_bison.json` to `jets/<jet>.json` and set `model`, `prefix`, `parts` and `keep`.
4. Place the markings with numbers from the mesh (see below), then generate, render, look, adjust:
   ```sh
   python warthunder/fit.py <jet>
   python warthunder/livery.py <jet>
   "C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b -t 4 --python-exit-code 1 --python warthunder/render.py -- --mesh warthunder/models/<model>/<model>.gltf --skin warthunder/out/skins/0OPS-Dragon-Crew-<jet> --out warthunder/out/renders/<jet> --close --sheet
   ```
   `--close` close-ups are placed for the Bison; on another plane judge the full views.
5. Go through the review checklist below. Keep each round's renders in a numbered folder with a short
   note of what changed.
6. Install: `python warthunder/livery.py <jet> --install` (writes `UserSkins/0OPS-Dragon-Crew-<jet>`).
   The operator checks it in game: open the jet, Customization, pick the user skin
   `0OPS-Dragon-Crew-<jet>`.

### Placing each marking

| Marking | Jet file key | How to find the numbers |
|---|---|---|
| Fin badge | `fin_badge.center` [X, Z], `height`, `max_offset` | Middle of the fin's flat side area, clear of fairings, antennas and the rudder hinge. `max_offset` just more than the fin's half-thickness so nothing else catches it |
| "0OPS" | `lettering.center` [X, Z], `height` | On the fuselage side under the canopy rear, where the side is flat and the UVs are not mirrored. livery.py stops with an error if the text lands on mirrored texels: move it aft |
| Kill marks | `kill_marks.start` [X, Z], `height`, `gap`, `count` 5 | Just above "0OPS", the row starting slightly ahead of the text |
| Nose cone, pitot | `accents[]`: `min`, `max` boxes, `whole` | Nose cone: a box around the whole radome or shock cone part with `whole` true, so only parts fully inside are painted. Pitot: a tight box around the boom |
| Wingtips | `wingtips[]`: `tip`, `width`, `x`, `z` | `tip` is the surface's largest distance from the centerline (`fit.py` prints the mesh Y range). One entry for the wings, one for the tailplanes; the `x` and `z` box must hold only that surface |
| Dragon | `emblems[0]`: `center` [X, 0], `length`, `bands`, `min_facing` 0.93, `surfaces` ["top"] | See "Fitting the dragon" |
| Stores and pylons | `parts` | Every texture name in `models/<model>/` that is not the main skin, plus every store model. Missing ones keep the stock colors |
| Wheels, nozzle | `keep` | Boxes around those parts |

### Fitting the dragon

`python warthunder/fit.py <jet>` prints the flat spine half-width at each X station, the foremost and
rearmost flat top surface at each Y station (on the wings that is the leading and trailing edge), and
writes `warthunder/out/fit/<jet>_top.png`: the top view with the dragon drawn as livery.py will paint it.
`--center X Y` and `--length L` try other values without editing the jet file. It takes seconds; use it
to get close, then confirm with a Blender render.

1. `bands`: [[0, spine half-width], [wing root distance, 9]]. The spine half-width is the flat width on
   top of the fuselage (0.14 m on the Bison). The wing root distance is where the wing top starts
   (0.58 m on the Bison). Between them is the round fuselage shoulder; anything painted there shows in the
   side views as white on the fuselage side.
2. Size and position: the wing tips must sit at least 0.15 m behind the wing leading edge at their span
   (read it from the Y table), ahead of the trailing edge, and inside the white wingtip band. On a swept
   or delta wing that is what limits the size: wings that go straight out must sit far enough aft for
   their tips to clear the swept leading edge. The tail spade must end ahead of the fin root, and the head
   must stay behind the canopy.
3. `center` Y is 0 (symmetric). `center` X is the middle of the dragon's nose-to-spade box.
4. If the shared shape cannot fit a plane (a very different spine width or wing shape), add a variant in
   this folder, e.g. `dragon-<jet>.svg`, with the same look and the same structure, and set the jet's
   emblem `svg` to `dragon-<jet>`. Keep `dragon.svg` as it is.

Bison values: center [-0.43, 0], length 2.46 m (head tip X 0.80, spade X -1.66, wing tips at Y +-2.31,
0.15 m inside the delta's leading edge), bands [[0, 0.14], [0.58, 9]], min_facing 0.93.

## Gotchas

- Mirrored UVs: parts of a jet share mirrored texture space, so one texel shows on both sides. On the
  Bison that is the nose sides ahead of X 4.75 and pieces of the spine. Text there reads backwards on one
  side, which is why livery.py refuses lettering on shared texels and why "0OPS" sits under the canopy and
  not on the nose. Emblems must be mirror-symmetric for the same reason.
- Pure side view: the near wing top is seen edge-on (the Bison has 3 degrees of anhedral), so the
  wingtips and the dragon wings show as a thin white streak at wing level. Expected; not a fault.
- The fuselage shoulder: paint on the curved area between the spine and the wing root shows as white on
  the fuselage sides. The `bands` gap and `min_facing` 0.93 keep it off. A lower `min_facing` or a wider
  spine band brings slivers back.
- Topmost surface only: without the height map test, top-view paint also lands on surfaces underneath
  (the lower wing skin, pylons). Leave `cell` and `depth_tol` at their defaults.
- Template textures: the game's template color is one flat grey and its normal map is flat. livery.py
  rebuilds the normal TGA from the game's own normal map; shipping the template's flat one erases the
  panel lines in game. The weathering comes from the game's own color texture with its markings masked.
- Parts: pylons, launchers, gun pods and stores have their own game textures, which the template does
  not cover. Each must be listed in `parts`, or it keeps the stock camo next to the black skin. The
  operator confirmed in game that stores pick up the skin this way.
- Render light: in the studio render the black reads as dark grey (about 50 of 255) because it reflects
  the white dome, and the canopy glass shows a white reflection along its frame. Neither is paint.
- Determinism: the same inputs give the same file hash. Re-running the generate command must reproduce
  the installed color TGA exactly; that is the proof that nothing was edited by hand.
- Safety: never write inside the War Thunder folder except `UserSkins`; never touch
  `UserSkins/template_*` (livery.py refuses those names); never launch the game; run Blender with `-b`
  only.
- Repo: `models/`, `templates/`, `out/` and `tools/` are git-ignored (game assets and build output).
  Commit only the scripts, this model and the jet files. Text files are ASCII only (`python check.py`).

## Review checklist

Render with `--sheet` (and `--close` on the Bison) and check every view before installing:

- top: the dragon is complete and symmetric (horned head, neck, chest, waist, hips, wings straight out to
  the sides with wrist claw and 5 scalloped finger points, long tail, diamond spade); the wings are on the
  wings and the body on the spine; both wingtips and both tailplane tips white and equal; nose cone and
  pitot white;
- left and right: no white on the fuselage sides except "0OPS" and the kill marks, both crisp and reading
  the right way; a thin streak at wing level is the wing top seen edge-on;
- fin: the shield centered, crisp, same height on both sides;
- bottom: only the wingtips, tailplane tips, nose cone and pitot are white; no dragon;
- everywhere: one black with no second shade, no stock colors on parts or stores, panel lines visible,
  canopy glass and tyres unpainted, no color other than black and white.

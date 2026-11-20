---
name: dragon-crew-skin
description: Make, change or check the 0OPS Dragon Crew War Thunder skin (flat black, white fin shield, 0OPS lettering and kill marks, white tips, top-view white dragon) for any plane, e.g. "apply the Dragon Crew skin to the Su-30MKK" or "OOPS-Dragon-Crew-<plane>". Use for any War Thunder skin or livery work in this repo.
---

# Dragon Crew skin

The 0OPS squadron's standard War Thunder skin. Skin folder and in-game name: `0OPS-Dragon-Crew-<jet>`.

1. Read `warthunder/liveries/dragon-crew/MODEL.md` in full before changing anything. Its "Settings at a
   glance" table is the exact list every plane gets (signed off by the operator on the finished MiG-21
   Bison): build exactly that, nothing added or dropped, and do not ask the operator to choose again. It
   also holds the design rules, how to fit the skin to a plane, the gotchas and the review checklist.
2. Commands and every option and key: `warthunder/README.md`, sections "Dragon Crew skin (0OPS livery)"
   and "Apply to a new jet".
3. The reference build is the MiG-21 Bison: `warthunder/jets/mig-21_bison.json`, renders in
   `warthunder/out/final/` (git-ignored, present in the main checkout once built).

Core loop for a plane `<jet>` (repo root, Git Bash):

```sh
python warthunder/fit.py <jet>
python warthunder/livery.py <jet>
"C:/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b -t 4 --python-exit-code 1 --python warthunder/render.py -- --mesh warthunder/models/<model>/<model>.gltf --skin warthunder/out/skins/0OPS-Dragon-Crew-<jet> --out warthunder/out/renders/<jet> --sheet
python warthunder/livery.py <jet> --install
```

Rules that always apply: all per-plane work goes in `warthunder/jets/<jet>.json` only; shared art and
style changes go in `warthunder/liveries/dragon-crew/`; never hand-paint a texture; Blender with `-b`
only; never launch the game; never write in the War Thunder folder except `UserSkins`, and never touch
`UserSkins/template_*`.

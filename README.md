# Arcade Conversation Pit

A classic sunken-lounge "conversation pit" adapted for an arcade: ten identical storage benches enclose the
Noisebridge two-player arcade coffee table. Each bench has a hinged plywood seat lid, storage inside, and lit
acrylic display windows on the outside that show off a retro game collection (cartridges, discs, consoles and
toys).

The whole design is parametric [build123d](https://github.com/gumyr/build123d) Python. One script derives the
layout from the real table model, builds the bench, checks that the lid swings clear, and exports STEP files plus
a mesh bundle for the browser viewers.

![Arcade Conversation Pit print render](out/print/arcade_pit_print.png)

## At a glance

| | Metric | Imperial |
|---|---|---|
| Pit footprint (outside) | 3715 × 2676 mm | 12′2″ × 8′9″ |
| Clear space inside | 2699 × 1660 mm | 8′10″ × 5′5″ |
| Bench (all 10 identical) | 892 L × 508 D × 457 H mm | 35.1″ × 20″ × 18″ |
| Walk-in gaps | 2, centred on the long sides, 915 mm | 36″ |
| Knee room to table | 496 mm at player ends, 465 mm on long sides | 19.5″ / 18.3″ |
| Bench weight (estimate) | ~29 kg | ~64 lb, a two-person carry |
| Storage per bench | ~143 L | ~5 ft³ |
| Lid hinge | Steel piano hinge, 865 mm, wrapped on the outer top corner | 34″ |
| Lid hold / stop | Soft-down stays hold at 105°, rope limiter stops at 108° | |
| Display lighting | Down-facing LED strip in a routed header behind the front acrylic, opal diffuser | |

## Layout

```
     ┌───┐┌─────────┐         ┌─────────┐┌───┐
     │   ││         │   gap   │         ││   │
     │   │└─────────┘         └─────────┘│   │
     ├───┤                               ├───┤
     │   │        [ arcade table ]       │   │   player ends: 3 benches run
     ├───┤                               ├───┤   the full width, closing
     │   │┌─────────┐         ┌─────────┐│   │   the corners
     │   ││         │   gap   │         ││   │
     └───┘└─────────┘         └─────────┘└───┘
```

Players sit at the two short ends, facing the screen. Each end has 3 benches across the full outside width, so the
corners are closed. Each long side has 2 benches with a 36″ walk-in gap between them.

## Repository layout

```
cad/
  arcade_pit.py      Main model: layout, bench, table import, swing check, exports
  collection.py      Display props (cartridges, discs, consoles, toys), 5 themed sets
  hinge_calc.py      Hinge/stay/rope calculator; writes the section SVG and build sheet
web/
  benches.html       Bench module viewer (lid slider, spec sheet, lighting notes)
  pit.html           Whole-pit viewer
  poster.html        Print layout used to render out/print/arcade_pit_print.png
  viewer.js          Shared three.js loader/materials/lid animation
out/                 Generated: STEP files, mesh bundle, hinge drawing, build sheet, print
raw/                 Inputs: concept images, table STEP and photo, table PDF, hinge spec
docs/                Design documentation (start at docs/README.md)
```

## Quick start

Requires [`uv`](https://docs.astral.sh/uv/). It fetches Python 3.12 and build123d on first run.

```sh
# Rebuild the model: runs the swing check, writes out/*.step and out/pit_meshes.json
uv run --python 3.12 --with build123d python cad/arcade_pit.py

# Hinge numbers, section drawing and build sheet (standard library only)
python3 cad/hinge_calc.py --leaf 0.065 --lid-weight-lb 13.4 --wall 300

# View locally
cd web && cp ../out/pit_meshes.json . && python3 -m http.server 8765
# open http://localhost:8765/benches.html, /pit.html or /poster.html
```

See [docs/workflow.md](docs/workflow.md) for the full regeneration pipeline, including the print render.

## Published viewers

- Bench Modules: https://claude.ai/artifact/KXkdK499rf3dtLTWk31Rkt
- Arcade Conversation Pit: https://claude.ai/artifact/W5c6TJvCWzA3y9YrNHYd47

## Documentation

| Doc | Covers |
|---|---|
| [docs/README.md](docs/README.md) | Index and design history |
| [docs/layout.md](docs/layout.md) | Pit layout, how it is derived from the table, clearances |
| [docs/bench.md](docs/bench.md) | Bench module construction, materials, cut dimensions |
| [docs/hinge.md](docs/hinge.md) | Lid hinge, stays, rope limiter, wall clearance |
| [docs/lighting.md](docs/lighting.md) | LED header, routed channel and diffuser |
| [docs/display-contents.md](docs/display-contents.md) | Display prop themes |
| [docs/workflow.md](docs/workflow.md) | Scripts, outputs, viewers, print render, checks |
| [docs/open-items.md](docs/open-items.md) | Decisions pending and things still to measure |

## Status

Design model complete, not yet built. Before cutting, measure the real hinge leaf, lid weight and site
clearances (see [docs/open-items.md](docs/open-items.md)).

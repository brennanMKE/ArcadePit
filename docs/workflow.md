# Workflow

## Requirements

- [`uv`](https://docs.astral.sh/uv/). It provides Python 3.12 and build123d without a separate install.
- Python 3 for `hinge_calc.py` and the local web server.
- Chromium (`/Applications/Chromium.app`), only for rendering the print image headlessly.

The model was developed with the build123d-mcp server (see `../Build123D/README.md`), but the scripts run
standalone.

## Regenerate the model

```sh
uv run --python 3.12 --with build123d python cad/arcade_pit.py
```

In order, this:

1. Measures the table from `raw/Arcade Table.step` and derives the layout ([layout.md](layout.md)).
2. Builds the bench and runs the lid **swing check** from 0 to 108°. It fails if the lid collides with anything.
3. Asserts that the hinge leaf fits within the lid thickness, that the base, bench bottom and display floor stack
   up to the window, and that the pins engage before the connector.
4. Checks that every part is a valid, non-empty solid, and prints part counts, volumes and bounding boxes.
5. Builds the three base section types and the joints between them. Checks that the pins clear the frame and
   conduit, and that nothing in the base pokes up into a bench.
6. Builds the 5 display themes, and checks that each one fits inside the bench.
7. Places 10 benches on the shared base (power sections under the middle bench at each end, corner sections at
   the outer ends) and the table, and checks that no benches overlap.
8. Writes the outputs below, and prints the bench spec and layout parameters.

### Outputs

| File | Contents |
|---|---|
| `out/pit_bench.step` | One bench, every part labelled |
| `out/pit_base.step` | Standard base section |
| `out/pit_base_corner.step` | Corner section: adds the pull box where a side run joins |
| `out/pit_base_power.step` | Power section: adds the fuse block and feeder inlet |
| `out/arcade_pit_assembly.step` | The full pit: 10 benches, 10 base sections, the joints (couplings, spacers, bolts) and the table (props not included) |
| `out/pit_meshes.json` | Tessellated meshes, placements, pivots, lights and specs for the web viewers |

## Hinge calculator

```sh
python3 cad/hinge_calc.py [--leaf IN] [--lid-weight-lb LB] [--wall MM] [...]
```

Writes `out/hinge/hinge_section.svg` (dimensioned side section, closed and open) and `out/hinge/build_sheet.md`.
See [hinge.md](hinge.md).

## Power calculator

```sh
python3 cad/power_calc.py [--strip-w-per-m W] [--feeder-m M] [...]
```

Reads `out/pit_meshes.json`, so run `arcade_pit.py` first. Writes `out/power/power_sheet.md` and
`out/power/wiring_plan.svg`. See [power.md](power.md).

## Web viewers

`web/` is a static three.js (0.160, from jsDelivr) site. All three pages load `pit_meshes.json` from their own
directory through `viewer.js`.

| Page | Shows |
|---|---|
| `benches.html` | One bench module: lid slider to 108°, theme picker, spec sheet, lighting and power sections. The **Base** view shows a corner lifted off the shared base, with the top plates see-through |
| `pit.html` | The whole pit around the table |
| `poster.html` | The print layout |

To view locally:

```sh
cd web
cp ../out/pit_meshes.json .
python3 -m http.server 8765
# http://localhost:8765/benches.html
```

`web/pit_meshes.json` is a copy and is git-ignored. The source is always `out/pit_meshes.json`.

The published Artifacts are built from these pages, with `pit_meshes.json` uploaded alongside:

- Bench Modules: https://claude.ai/artifact/KXkdK499rf3dtLTWk31Rkt
- Arcade Conversation Pit: https://claude.ai/artifact/W5c6TJvCWzA3y9YrNHYd47

## Print render

`out/print/arcade_pit_print.png` is a 3600 × 2400 px screenshot of `poster.html`, set to 200 dpi:

```sh
cd web && cp ../out/pit_meshes.json . && (python3 -m http.server 8765 >/dev/null 2>&1 &) ; sleep 1
/Applications/Chromium.app/Contents/MacOS/Chromium --headless=new --use-angle=swiftshader \
  --enable-unsafe-swiftshader --hide-scrollbars --window-size=1800,1200 --force-device-scale-factor=2 \
  --virtual-time-budget=25000 --screenshot=../out/print/arcade_pit_print.png http://localhost:8765/poster.html
rm pit_meshes.json; pkill -f "http.server 8765"
sips -s dpiWidth 200 -s dpiHeight 200 ../out/print/arcade_pit_print.png
```

Re-render it after any change you want to show in the print.

## Key parameters

They're all at the top of `cad/arcade_pit.py`:

| Group | Parameters |
|---|---|
| Layout | `CLEAR_END`, `CLEAR_SIDE`, `END_BENCHES`, `GAP_MIN`, `D` |
| Bench | `H`, `T_TOP`, `T`, `T_ACR`, `T_LINER`, `T_FLOOR`, `SEAM`, `BORDER_*`, `LINER_NOTCH_*` |
| Lighting | `HEADER_D`, `LED_CH_W`, `LED_CH_D`, `DIFF_W`, `DIFF_T` |
| Base and power | `BASE_*`, `PIN_*`, `C_*`, `COUPLER_*`, `OUTLET_X`, `GLAND_XY`, `GROMMET_R`, `JUNCTION_X`, `BCHASE`, `CTRL`, `LED_RACE_Z` |
| Hinge | from `hinge_calc.Inputs()` defaults |

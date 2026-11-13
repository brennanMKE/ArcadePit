# Lid Hinge

Source spec: [`raw/storage-bench-hinge-spec.md`](../raw/storage-bench-hinge-spec.md). Calculator:
`cad/hinge_calc.py`. Generated outputs: [`out/hinge/build_sheet.md`](../out/hinge/build_sheet.md) and
`out/hinge/hinge_section.svg`.

## Goals

- Nothing proud on the seat.
- Durable under shared, heavy use.
- Affordable.
- No screws into plywood edges.

## Design

A steel piano hinge wraps around the **outer top corner of the display face**. In this pit, the spec's "back" is
the display (window) side, because the lid swings outward, away from the table.

- **Case leaf:** vertical, screwed to the 45 mm frame rail above the window. It must stay inside the rail and never
  cross the window.
- **Lid leaf:** horizontal, in a rabbet under the lid's back edge, so the lid closes flat.
- **Knuckle:** on the corner, at the joint between the lid and the case.
- **Lid:** full depth (508 mm), back edge flush with the display face.

## Hardware (per bench)

| Item | Spec |
|---|---|
| Piano hinge | Steel, 1-1/2″ open width, 0.66″ leaf, cut to **865 mm (34.04″)** (lid length minus 1/2″ each end). Example: Rockford Process Control CP2-2203S-48, 48″, 2″ hole spacing |
| Rabbet | **17.5 mm wide × leaf thickness deep** (11/16″ × 0.060″ nominal). Cut it to the measured leaf |
| Screws | Lid leaf #4 FH × 1/2″ (doesn't break through the lid); case leaf #4 FH × 5/8″; every hole |
| Soft-down stays | **2 × Sugatsune SDS-210**, one per end, holding at 105° |
| Rope limiter | Braided polyester or nylon cord, one per end, with 2 screw eyes per rope |

For 10 benches, buy 10 hinges, 20 stays and 20 ropes.

## Stays

The estimated lid weight is 12.9 lb (890 × 508 × 19 mm birch ply), which is **6.5 lb per stay** with two stays.
That's near the low end of the SDS-210's 6–10 lb range, so confirm on Sugatsune's selection chart with the
measured lid weight. The stays mount on the solid first 115 mm of each end panel. The end windows start behind
that zone.

## Rope limiter

The rope is a hard stop that protects the hinge and stays if someone yanks or leans on the open lid. The stay must
latch first.

Anchors, measured from the knuckle (x forward into the bench, y up):

| Anchor | Position |
|---|---|
| Case (end panel face, above the end window) | a = 150 mm forward, b = 20 mm below |
| Lid (underside) | c = 150 mm forward |

```
L = sqrt( (a - c·cos θ)² + (c·sin θ + b)² )
```

At a stop angle θ = 108°, **L = 255 mm (10.04″)** knot to knot. Cut about 375 mm and set it on the bench with an
adjustable knot (taut-line hitch). At 105° the span is 251 mm, so the rope is 4.3 mm short of taut when the stay
latches ✓. When the lid is closed, 235 mm of slack hangs inside.

The anchor geometry (long a and c, short b) is chosen so the span changes fastest near 105–108°. That gives a clear
gap between the stay latching and the rope going taut.

## Wall clearance

At an open angle θ > 90°, the lid's top front edge ends up behind the display face by about
`d·sin(θ − 90°) + t·cos(θ − 90°)`:

| Angle | Clearance |
|---|---|
| 105° (stay hold) | 150 mm (5.9″) |
| 108° (rope stop) | **175 mm (6.9″)** |

If a wall or obstruction stops the lid before 105°, the stay won't latch and the lid will slowly close itself.

## Build steps

1. Measure the hinge leaf thickness, and set the rabbet depth to match.
2. Cut the rabbet under the lid's back edge, 17.5 mm wide.
3. Cut the hinge to 865 mm, and file the ends.
4. Screw the lid leaf into the rabbet, knuckle centre on the lid's back edge.
5. Close the lid on the case, back edge flush with the display face, and clamp it.
6. Screw the case leaf to the frame rail above the window.
7. Fit the 2 stays on the solid zone of each end panel, following Sugatsune's drawing (measured from the hinge
   centre).
8. Fit the rope eyes inboard of each stay, at a, b and c.
9. Open and close the lid 20 times. The stay must latch at 105° before the rope goes taut at 108°.

## Recalculating

```sh
python3 cad/hinge_calc.py --leaf 0.065 --lid-weight-lb 13.4 --wall 300
```

Every field of `Inputs` in `hinge_calc.py` is also a flag (for example `--rope-a`, `--rope-stop-deg`,
`--lid-depth`). The run prints a summary and regenerates `out/hinge/hinge_section.svg` and
`out/hinge/build_sheet.md`.

**Note:** `arcade_pit.py` reads the **defaults** in `hinge_calc.Inputs()`, not command-line flags. To carry a
measured value (leaf thickness, rope anchors, stop angle) into the 3D model, change the default in `Inputs` and
re-run both scripts.

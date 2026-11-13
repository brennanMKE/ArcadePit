# Pit Layout

## The table

The arcade table is the Noisebridge two-player coffee table: a black top frame with a 43″ TV under acrylic in the
middle, a joystick-and-buttons control box at each end, on a pine base. The model is the Onshape Super Assembly,
exported to `raw/Arcade Table.step` (source:
[Onshape document](https://cad.onshape.com/documents/78f475104c9923610f5e185a/w/902a4c2327f0fcad61617b25/e/bef8f43fe906f254708df8c8)).
`raw/Arcade Table.jpg` is a photo and `raw/Coffee Table - Noisebridge.pdf` is the original plan.

`arcade_pit.py` measures the table from the STEP file on every run:

| | Value |
|---|---|
| Top length | 1708 mm (67.3″) |
| Top width | 730 mm (28.75″) |
| Height to top | 514 mm (20.25″) |

If the STEP file is missing, it falls back to these numbers and a simple stand-in model, and sets
`table_estimated: true` in the mesh bundle.

## How the layout is derived

Everything follows from the table size and a few clearance parameters at the top of `cad/arcade_pit.py`:

| Parameter | Value | Meaning |
|---|---|---|
| `CLEAR_SIDE` | 465 mm | Knee room from a long-side bench front to the table edge |
| `CLEAR_END` | 480 mm minimum | Knee room at the player ends (players must reach the controls) |
| `END_BENCHES` | 3 | Benches across each player end |
| `GAP_MIN` | 915 mm (36″) | Minimum walk-in gap |
| `D` | 508 mm (20″) | Bench depth |

Derivation:

1. Clear inside width = table width + 2 × `CLEAR_SIDE` = **1660 mm**.
2. The end benches span the inside width plus both side-bench depths, so the bench length is
   `L = (1660 + 2 × 508) / 3` = **892 mm**.
3. Clear inside length = the larger of (table length + 2 × `CLEAR_END`) and (2 × `L` + `GAP_MIN`) =
   **2699 mm**. The gap requirement wins, so the player-end knee room grows to **496 mm**.
4. The walk-in gap on each long side is the inside length minus 2 × `L` = **915 mm**.

Changing the table, a clearance or the bench depth re-derives every placement.

## Result

| | mm | Imperial |
|---|---|---|
| Outside footprint | 3715 × 2676 | 12′2″ × 8′9″ |
| Clear inside | 2699 × 1660 | 8′10″ × 5′5″ |
| Bench | 892 × 508 × 457 | 35.1″ × 20″ × 18″ |
| Benches | 10 (3 per end, 2 per long side) | |
| Walk-in gaps | 2 × 915, centred on the long sides | 2 × 36″ |

## Placement

`ring_locations()` returns each bench's position, rotation and side. A bench's display face (local Y = 0) always
points away from the table, so the windows face outward and the seat front faces in.

- **West and east ends:** 3 benches each, rotated ±90°, running the full outside width. They close the corners.
- **South and north sides:** 2 benches each, one on either side of the centred gap.

The script checks that no two benches overlap by more than 2.5 mm in plan.

## Space around the pit

The lids swing outward, over the display side. Leave at least **175 mm (6.9″)** clear behind every bench so the lid
can reach the rope stop. The stay won't latch if a wall stops the lid before 105°. See [hinge.md](hinge.md).

# Display Contents

`cad/collection.py` builds the props shown inside the benches in the renders and viewers. They're simple,
unbranded low-poly shapes that read as a retro game collection at display scale:

- Cartridges: 8-bit, 16-bit, 64-bit and handheld formats
- Disc cases and loose discs
- Consoles with controllers
- Toys: a block, a mushroom, pixel critters, ghosts, coins and a mini arcade cabinet
- Risers, to stage items at different heights

## Themes

There are five themed sets. The pit cycles through them across the 10 benches (`contents = index % 5`):

| # | Theme |
|---|---|
| 0 | 8-bit |
| 1 | 16-bit & handheld |
| 2 | 64-bit |
| 3 | 32-bit discs |
| 4 | disc tower |

Each builder works in bench-local coordinates. Items sit on the display floor (Z = 75 mm), inside the acrylic,
liner and end panels. `arcade_pit.py` checks that every set fits inside the bench and stays at least 15 mm below
the lid.

The props are only for visualisation. They aren't part of the build and aren't in `pit_bench.step`.

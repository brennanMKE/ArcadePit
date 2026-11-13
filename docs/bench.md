# Bench Module

All 10 benches are the same module (`pit_bench()` → `bench()` in `cad/arcade_pit.py`). Each bench has a window on
its outer face and on both ends, so it works in any position: at a corner, the end windows are exposed; elsewhere
they face a neighbour.

## Overall

| | Value |
|---|---|
| Length × depth × height | 892 × 508 × 457 mm (35.1″ × 20″ × 18″ seat height) |
| Carcass height (below lid) | 438 mm |
| Front window | 802 × 318 mm, 1 bay |
| End windows | 325 mm wide × 318 mm, both ends |
| Clear display height | 363 mm (display floor to lid) |
| Storage volume | ~143 L |
| Estimated weight | ~29 kg (64 lb): ply 680 kg/m³, acrylic 1190 kg/m³, steel 8000 kg/m³ |

## Materials

| Part | Material | Thickness |
|---|---|---|
| Lid | Birch plywood, 3/4″ | 19 mm |
| Carcass panels (display face, seat front, ends, bottom) | Black-finished plywood | 18 mm |
| Windows | Clear acrylic | 6 mm |
| Interior liner (back) | Plywood | 6 mm |
| Display floor | Plywood | 12 mm |
| LED header | Black plywood | 38 mm deep (see [lighting.md](lighting.md)) |
| LED diffuser | Opal acrylic | 3 mm (1/8″) |
| Hinge | Steel piano hinge | see [hinge.md](hinge.md) |

## Parts

- **Display face (outer):** 18 mm panel with one window cut-out. Borders: 45 mm at the sides and top, 75 mm black base
  rail at the bottom. The top border is the frame rail that carries the hinge's case leaf.
- **Front acrylic:** 6 mm, behind the display face. It overlaps the cut-out by 15 mm at the sides and bottom, and
  its top edge slides up under the LED header, which holds it in place.
- **Seat-front panel (inner, faces the table):** 18 mm, with a 140 × 22 mm finger-pull scoop centred in its top edge
  for lifting the lid.
- **Ends:** 18 mm panels, each with a window starting 125 mm in from the display face. The first 115 mm is kept
  solid (`STAY_ZONE`) for the lid stay and rope anchor. The end acrylic is 6 mm, inside the panel.
- **Bottom:** 18 mm, between the ends.
- **Display floor:** 12 mm ply, top surface level with the bottom of the window (75 mm above the floor).
- **Back liner:** 6 mm ply against the inside of the seat-front panel, above the display floor.
- **Lid:** one full-depth 3/4″ lid, 890 mm long (1 mm seam each side), flush with the display face at the back. No
  rear overhang. The underside has a rabbet for the hinge leaf and a relief for the knuckle.

The bench stops 1 mm short of its neighbours at each end (`SEAM`), so lids never rub.

## Construction notes

- Every hinge screw goes into plywood face grain. None go into panel edges (from the hinge spec).
- The top edges of the carcass only carry the lid's weight in compression.
- The case-leaf screws go through the frame rail into the LED header behind it, so they have more to grip.
- The LED header and diffuser are part of the display frame. Fit them before the front acrylic.

## Lid swing

The lid lifts at the seat front and swings back over the display side, pivoting on the hinge at the outer top corner.
`swing_check()` rotates every lid-group part (lid, lid leaf, stay arms, lid rope eyes) about the hinge axis in steps
up to 108°, and fails the build if any of them cuts into a fixed part by more than 500 mm³. The knuckle and stay
bodies are excluded, because they are meant to touch.

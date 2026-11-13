# Bench Module

All 10 benches are the same module (`pit_bench()` → `bench()` in `cad/arcade_pit.py`), so any bench fits any spot.
Each bench has one window, on its outer face. The ends are solid wood for structural strength.

## Overall

| | Value |
|---|---|
| Length × depth × height | 892 × 508 × 457 mm (35.1″ × 20″ × 18″ seat height) |
| Carcass height (below lid) | 438 mm |
| Front window | 802 × 318 mm, 1 bay |
| Ends | Solid 18 mm ply, no windows |
| Clear display height | 363 mm (display floor to lid) |
| Storage volume | ~141 L |
| Estimated weight | ~30 kg (66 lb): ply 680 kg/m³, acrylic 1190 kg/m³, steel 8000 kg/m³ |
| Sits on | The shared 45 mm base (see [power.md](power.md)); the carcass starts 45 mm above the floor |

## Materials

| Part | Material | Thickness |
|---|---|---|
| Lid | Birch plywood, 3/4″ | 19 mm |
| Carcass panels (display face, seat front, ends, bottom) | Black-finished plywood | 18 mm |
| Window (outer face only) | Clear acrylic | 6 mm |
| Interior liners (back and ends) | Birch plywood | 6 mm |
| Display floor | Plywood | 12 mm |
| LED header | Black plywood | 38 mm deep (see [lighting.md](lighting.md)) |
| LED diffuser | Opal acrylic | 3 mm (1/8″) |
| Hinge | Steel piano hinge | see [hinge.md](hinge.md) |

## Parts

- **Display face (outer):** 18 mm panel with one window cut-out. Borders: 45 mm at the sides and top. The bottom rail is
  30 mm, sitting on the base, so the window still starts 75 mm above the floor. The top border is the frame rail that carries the hinge's case leaf.
- **Front acrylic:** 6 mm, behind the display face. It overlaps the cut-out by 15 mm at the sides and bottom, and
  its top edge slides up under the LED header, which holds it in place.
- **Seat-front panel (inner, faces the table):** 18 mm, with a 140 × 22 mm finger-pull scoop centred in its top edge
  for lifting the lid.
- **Ends:** solid 18 mm panels with no window, for structural strength. They're lined with 6 mm birch inside.
  The liner is notched at the top front (200 mm deep × 125 mm tall), so the lid stay and rope eye screw into the
  solid 18 mm panel, not the thin liner.
- **Bottom:** 18 mm, between the ends, resting on the base top plate at 45 mm. It carries the 2 locating pins and
  a 35 mm grommet for the power cable, under the back-left corner ([power.md](power.md)).
- **Cable chase:** a 30 × 38 mm birch box in the back-left corner, from the display floor up to the control box.
- **Control box:** about 140 × 34 × 80 mm, high on the back liner at the left end, under the lid. It holds the fuse,
  ESP32 and level shifter, with a GX16 inlet underneath.
- **LED feed:** a black raceway along the left end liner, below the stays, then a short chase behind the left side
  border up into the LED header.
- **Display floor:** 12 mm ply, directly on the bottom, top surface level with the bottom of the window (75 mm
  above the floor). Notched around the cable chase.
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

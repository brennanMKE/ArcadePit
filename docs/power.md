# Shared Base, Conduit and 5 V Power

Model: `base_parts()`, `ring_hardware()` and `power_parts_bench()` in `cad/arcade_pit.py`. Calculator:
`cad/power_calc.py`. Generated outputs: [`out/power/power_sheet.md`](../out/power/power_sheet.md) and
`out/power/wiring_plan.svg`.

## Goals

- One base that holds every bench in the pit shape and carries the conduit for the power cables.
- No single huge part: the base comes apart into sections that interlock when assembled.
- 5 V to every bench on its own cable, so every LED gets enough power.
- Durable: no splices in the runs, strain relief at every point where a cable could be pulled, and locking
  connectors.

## Shared base

The walk-in gaps split the ring into a **west** half and an **east** half. Each half has its own shared base, shaped
like a U: 3 sections across the player end and 1 down each side. So no part of the base crosses a walkway.

| | Value |
|---|---|
| Height | 45 mm |
| Sections | One per bench position, 890 mm long, about 4.3 kg each: 4 standard, 4 corner, 2 power |
| Construction | Open-bottom frame of 18 mm ply rails (front, back, two ends and two intermediate) under a 12 mm ply top plate |
| Footprint | Set back 20 mm from the display face and the seat front, like a toe kick |
| Locating | 2 steel bushings in the top plate per bench. The bench's chamfered 12 mm pins drop into them |

**Height is unchanged.** The base fills the empty space that used to sit under the display floor. The bench bottom
(18 mm) and display floor (12 mm) sit on it, so the display floor is still 75 mm up, level with the bottom of the
window. `arcade_pit.py` asserts this, and checks that nothing in the base pokes up into the bench above.

### How the sections interlock

- **Straight seams** (between the 3 sections across each player end): the end rails of neighbouring sections bolt
  together with 2 M8 connector bolts and barrel nuts. A slip coupling joins the conduit across the seam.
- **Corners** (side section to end section): the side section's end sits 21 mm from the end section's back rail
  (20 mm toe kick plus the 1 mm seam). Two hardwood spacers fill that gap, and an M8 bolt through each one locks
  the side section's end rail to the end section's back rail. A short conduit nipple goes through the back rail
  into a pull box in the end section, with a slip coupling at the side section.
- The benches sit on top, each held by its pins. Bolting the sections makes each half one rigid U.
- The CAD script checks that the corner nipples enter their pull boxes, and that the spacers touch both rails.

### Section types

| Type | Where | Extra parts |
|---|---|---|
| Standard (`pit_base.step`) | Both side positions on each long side | none |
| Corner (`pit_base_corner.step`) | Outer two end positions at each player end | Pull box where the side run joins |
| Power (`pit_base_power.step`) | Middle end position | Fuse block, Powerpole feeder inlet in the outer rail |

All three have the same frame, conduit, holes and outlet box, so the benches are identical and fit any position.

## Conduit

- 3/4″ schedule 40 PVC (26.7 mm OD) runs along the back of each section, 440 mm from the display face and 16 mm up
  its centreline. It passes through holes in the rails and fits under the top plate.
- Every back rail has an entry hole for a corner run, in the same place on every section.
- **Cables are pulled once**, after the base is assembled. Each bench gets one unbroken cable from the fuse block. The
  seams have conduit couplings, but no electrical joints.

## From the base into the bench

1. **Outlet box** on the conduit under the left end of each bench position.
2. **Cord grip** (PG9 or M16 gland) in the base top, above the outlet box. This is the strain relief where the cable
   leaves the base. Leave about 300 mm of slack.
3. **Grommet**, 35 mm, in the bench bottom directly above. It's big enough for the GX16 plug to pass through.
4. **Cable chase:** a birch box in the back-left corner of the bench, from the display floor up to the control box.
5. **GX16 4-pin aviation plug**, screw-locking, into the control box's panel socket. Two pins carry +5 V and two
   carry GND (2.9 A load). A P-clip holds the cable just before the plug, so a pull on the cable doesn't load the
   connector.

**To move a bench:** open the lid, unscrew the GX16, pass the plug down through the grommet and lift the bench off
its pins. The cable stays in the base.

## Control box (one per bench)

About 140 × 34 × 80 mm. It's mounted high on the back liner at the left end, under the lid, above the tallest
display items. Lifting the lid gives direct access to it.

- The bench fuse (5 A) and a terminal block. Use ferrules on every wire.
- A 1000 µF 10 V capacitor across the strip input.
- An ESP32 dev board (5 V in, with its own 3.3 V regulator).
- A 74AHCT125 level shifter, taking the ESP32's 3.3 V data up to 5 V for the LED strip.
- Two cable glands for the LED feeds.

The LED feed runs from the box along a black raceway on the left end liner, below the stays. It turns up a short chase
behind the left side border into the LED header, feeding the left end of the strip. A second pair runs back along
the LED channel to feed the right end.

**Fuses at both ends:** the fuse block in the power base protects each cable in the conduit. The fuse in the control
box protects the bench.

## Supplies

Each supply sits outside the pit, behind its player end, and plugs into the wall. A short 10 AWG feeder runs into the
Powerpole inlet on the power base. There's no mains wiring in the furniture.

## Numbers (defaults: 18 W/m strip, 2 m feeder)

| | Value |
|---|---|
| Load per bench | 802 mm strip at 18 W/m (5 V WS2812B-class, 60/m, full white) = **2.9 A** |
| Fuse per run | 5 A at the fuse block, and 5 A in the control box |
| Load per half | 14.4 A |
| Supply per half | Mean Well LRS-150F-5 (22 A), trimmed to about 5.3 V |
| Runs | 1.0–2.5 m along the conduit. 16 AWG covers every run; 14 AWG gives more margin |
| Voltage at each bench, full white | 4.92–4.99 V |

Re-run once the strip is chosen or the supply location is known:

```sh
python3 cad/power_calc.py --strip-w-per-m 14.4 --feeder-m 3
```

Options: `--strip-w-per-m`, `--feeder-m`, `--slack-m` (default 0.6 m per run), `--run-budget-v` (0.20 V) and
`--feeder-budget-v` (0.15 V). Runs follow the conduit along the end, round the corner pull box and along the side.

## Parameters

At the top of `cad/arcade_pit.py`: `BASE_H`, `BASE_TOP`, `BASE_RAIL`, `BASE_SET`, `BASE_MID_RAILS`, `PIN_*`,
`C_Y`, `C_Z`, `C_R`, `COUPLER_*`, `OUTLET_X`, `GLAND_XY`, `GROMMET_R`, `JUNCTION_X`, `BCHASE`, `CTRL` and
`LED_RACE_Z`.

# Base, Locating and 5 V Power

Model: `base_parts()` and `power_parts_bench()` in `cad/arcade_pit.py`. Calculator: `cad/power_calc.py`.
Generated outputs: [`out/power/power_sheet.md`](../out/power/power_sheet.md) and `out/power/wiring_plan.svg`.

## Goals

- Get 5 V to every bench, with a separate feed to each one so every LED gets enough power.
- Stop the benches from wandering.
- Keep each bench a two-person carry: set it down and it's connected; lift it and it's free.

## Base

Each bench drops onto its own low base. There's no deck.

| | Value |
|---|---|
| Height | 45 mm |
| Construction | Open-bottom frame of 18 mm black ply rails under a 12 mm black ply top plate |
| Footprint | Full bench length (1 mm seams), set back 20 mm from the display face and the seat front, like a toe kick |
| Rails | Front, back, both ends, and one centre rail |
| Cable slots | 22 mm tall: through both end rails and the centre rail, and at both ends of the back rail, so a run can pass under neighbouring benches, including around the corners |
| Weight | About 4.3 kg each |

**Height is unchanged.** The 45 mm base fills the empty space that used to sit under the display floor. The carcass
now starts at 45 mm. The bench bottom (18 mm) and display floor (12 mm) sit directly on it, so the display floor
is still 75 mm up, level with the bottom of the window. Seat height, window size and display height are all
unchanged. `arcade_pit.py` asserts `BASE_H + T + T_FLOOR == FLOOR_Z`.

## Locating pins

- 2 hardened steel dowel pins per bench: 12 mm diameter, 43 mm long, chamfered tip. They're fixed through the
  bench bottom on the depth centreline, 90 mm from each end.
- They stick out 25 mm below the bench and drop into steel bushings (12 mm bore) in the base top plate.
- The pins hold the bench in place sideways, and the bench's weight (about 28 kg) keeps it seated. If you want the
  ring more rigid, add barrel bolts or connector bolts between neighbouring bases.

## Blind-mate connector

- An **Anderson Powerpole** pair: red for +5 V, black for GND, rated 45 A and genderless.
- **Bench half:** fixed in the bench bottom under the left end (bench-local X = 40, Y = 48 mm), sticking out 12 mm
  below.
- **Base half:** in a floating ply bracket screwed to the base's front rail, under a pocket in the top plate. The
  bracket gives it about 0.6 mm of float, so the pins do the aligning.
- **Sequence:** the pins enter their bushings **13 mm** before the connector halves touch. The CAD script asserts
  that the pins stick out at least 8 mm further than the connector.
- Use the same red/black orientation on every bench and base, so any bench fits any base.
- The base half is always live, so it's the shrouded side. The contacts sit back inside the housing, and each run
  has its own fuse in case a coin or screw shorts the pocket.

## Inside the bench

A black wire chase, 9.5 × 30 mm, runs up the inside of the display face at the left end. It's hidden behind the
45 mm side border, and the display floor is notched around it. It goes from the connector to the end of the LED
header, where the pair feeds the left end of the strip. A second pair runs back along the LED channel, behind the
strip, and feeds the right end, so the strip is powered from both ends. The display props stay clear of the chase.

## Distribution

The two walk-in gaps split the ring into a **west** half and an **east** half of 5 benches each. Each half gets its
own supply, so no wire crosses a walkway.

```
 wall outlet → 5 V supply (outside the pit, behind the player end)
            → feeder, 10 AWG → Powerpole inlet on the outer rail of the power base
            → fused distribution block in the power base (middle bench at that end)
            → one fused run per bench, through the base cable slots → base connector
```

- **Power base:** the base under the middle bench at each player end. It's a standard base plus a 6-way blade fuse
  block and a Powerpole feeder inlet in the outer rail. Benches are still all identical; only the two power bases
  differ (`pit_base_power.step`).
- **Supply:** outside the pit, so there's no mains wiring inside the furniture. It plugs into the wall.

## Numbers (defaults: 18 W/m strip, 2 m feeder)

| | Value |
|---|---|
| Load per bench | 802 mm strip at 18 W/m (5 V WS2812B-class, 60/m, full white) = **2.9 A** |
| Fuse per run | 5 A blade |
| Load per half | 14.4 A |
| Supply per half | Mean Well LRS-150F-5 (22 A), trimmed to about 5.25 V |
| Feeder | 2 m, 10 AWG |
| Runs | 1.2–3.1 m. 18 AWG for the shortest, 14 AWG for the longest. Buy 14 AWG for all of them to keep it simple |
| Voltage at each bench, full white | 4.89–4.92 V |

Re-run when the strip is chosen, or the supply location is known:

```sh
python3 cad/power_calc.py --strip-w-per-m 14.4 --feeder-m 3
```

Options: `--strip-w-per-m`, `--feeder-m`, `--slack-m` (default 0.6 m per run), `--run-budget-v` (0.20 V) and
`--feeder-budget-v` (0.15 V). Runs follow the ring through the bases and never cross the open floor of the pit.

## Parameters

At the top of `cad/arcade_pit.py`: `BASE_H`, `BASE_TOP`, `BASE_RAIL`, `BASE_SET`, `PIN_R`, `PIN_L`, `PIN_X`, `PP`,
`PP_L`, `CONN_X`, `CONN_Y`, `CONN_DROP` and `CHASE_X`/`CHASE_Y`.

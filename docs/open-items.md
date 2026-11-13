# Open Items

## Decisions pending

- **LED channel location.** It's currently in a separate black header behind the frame rail
  ([lighting.md](lighting.md)). The other option is to route it directly into the frame rail. That's simpler, but
  it puts the strip in front of the acrylic.
- **LED strip.** The power plan assumes 18 W/m (5 V WS2812B-class, 60/m, full white). Choose the strip, then
  re-run `python3 cad/power_calc.py --strip-w-per-m <W/m>`.
- **Supply location.** Assumed to be outside the pit, 2 m from each power base. Set `--feeder-m` once the outlets
  are known.
- **Joining the bases.** The pins hold each bench to its base. Decide whether the bases should also be bolted to
  each other or fixed to the floor.

## To measure before cutting

| Item | Why | How to apply |
|---|---|---|
| Hinge leaf thickness | Sets the rabbet depth (nominal 0.060″) | `--leaf` and the `Inputs.leaf_thickness_in` default |
| Actual lid weight | Stay count and rating: 6.5 lb per stay is borderline for the SDS-210 | `--lid-weight-lb`, then check Sugatsune's chart |
| Clearance behind each bench on site | The lid needs 175 mm (6.9″) to reach the rope stop | `--wall` |
| Powerpole housing positions | Check the mated length against the datasheet, and set `CONN_DROP` | `cad/arcade_pit.py` |
| Stay envelope against the 363 mm interior height | Check with Sugatsune's installation drawing | Adjust `LINER_NOTCH_Y` / `LINER_NOTCH_H` if needed |

After changing `hinge_calc.Inputs` defaults, re-run both `cad/hinge_calc.py` and `cad/arcade_pit.py`, then
republish the viewers and re-render the print ([workflow.md](workflow.md)).

## Known simplifications in the model

- Weight is estimated from volumes and nominal densities. It doesn't include the stays, the rope or the
  display contents.
- Display props are visual stand-ins only.
- The stay bodies are blocks sized to the SDS-210 envelope, not the real part geometry.

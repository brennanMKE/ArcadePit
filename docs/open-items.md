# Open Items

## Decisions pending

- **LED channel location.** It's currently in a separate black header behind the frame rail
  ([lighting.md](lighting.md)). The other option is to route it directly into the frame rail. That's simpler, but
  it puts the strip in front of the acrylic.
- **End-window lighting.** There are no strips at the ends for now. Add short end headers if the end views are too
  dark once it's built.

## To measure before cutting

| Item | Why | How to apply |
|---|---|---|
| Hinge leaf thickness | Sets the rabbet depth (nominal 0.060″) | `--leaf` and the `Inputs.leaf_thickness_in` default |
| Actual lid weight | Stay count and rating: 6.5 lb per stay is borderline for the SDS-210 | `--lid-weight-lb`, then check Sugatsune's chart |
| Clearance behind each bench on site | The lid needs 175 mm (6.9″) to reach the rope stop | `--wall` |
| Stay envelope against the 363 mm interior height | Check with Sugatsune's installation drawing | Adjust `STAY_ZONE` if needed |

After changing `hinge_calc.Inputs` defaults, re-run both `cad/hinge_calc.py` and `cad/arcade_pit.py`, then
republish the viewers and re-render the print ([workflow.md](workflow.md)).

## Known simplifications in the model

- Weight is estimated from volumes and nominal densities. It doesn't include the stays, the rope or the
  display contents.
- Display props are visual stand-ins only.
- The stay bodies are blocks sized to the SDS-210 envelope, not the real part geometry.

# Storage Bench Lid Hinge: Design Spec

Handoff spec for a storage bench with a hinged lid. The goal is a lid hinge that is not proud on top, is durable under shared heavy use, and is affordable. All screws must go into plywood face grain, never into plywood edges.

## Chosen design

A steel piano hinge wrapped around the outside back corner of the bench, plus a soft-down lid stay and a rope limiter on each end.

- **Case leaf:** vertical, screwed into the back face of the back panel (face grain).
- **Lid leaf:** horizontal, screwed up into the underside of the lid (face grain). It sits in a shallow rabbet along the lid's back edge so the lid closes flat.
- **Knuckle:** at the outside back corner, on the joint line between the lid and the case.
- **Closed:** the hinge leaves are at 90°. **Open:** about 195° (lid at about 105°). A piano hinge swings well past this.
- **Visibility:** nothing is visible on top. The knuckle and case leaf are visible only from behind.

## Constraints

- Lid: 3/4" plywood.
- The lid's back edge must be flush with the case's back face. No rear overhang.
- Front and side overhang are fine.
- No screws into plywood edges anywhere. The top edge of the back panel only carries the lid's weight in compression.
- The lid swings behind the case when opened, so wall clearance is required (see Geometry).

## Parts

| Part | Spec | Example | Approx. cost |
|---|---|---|---|
| Piano hinge | Steel, 1-1/2" open width, 0.66" leaf, cut to lid length | Rockford Process Control CP2-2203S-48 (nickel) or CP2-3303S (brass plated), 48", 2" hole spacing, countersunk, screws not included | ~$16 |
| Lid leaf screws | #4 flat head x 1/2" (must not break through the 3/4" lid) | | |
| Case leaf screws | #4 flat head x 5/8" | | |
| Soft-down stay | Sugatsune SDS-210: 105° hold, rated for piano/butt hinges, 30,000-cycle test, about 6 to 10 lb lid per stay | Rockler, $17.99 to $19.99 each | $18 to $40 |
| Rope limiter | Small-diameter braided cord (polyester or nylon), one per end, with 2 screw eyes or anchor screws per side | | a few dollars |

Use 1 stay for a lid of about 10 lb or less, or 2 stays (one per end) for a heavier lid. Confirm against Sugatsune's selection chart using the measured lid weight.

## Build steps

1. **Measure the leaf thickness** of the actual hinge (typically 0.06" to 0.075").
2. **Cut the rabbet** on the lid underside along the back edge. Make it about 11/16" wide and exactly the leaf thickness deep. Use a table saw or router table.
3. **Cut the hinge** to the lid length minus about 1/2" at each end. File the cut ends smooth.
4. **Mount the lid leaf** in the rabbet, with the knuckle center at the lid's back edge. Drill pilot holes and use #4 x 1/2" screws.
5. **Position the lid** on the case closed, with its back edge flush to the case back face. Clamp it.
6. **Mount the case leaf** to the back face of the back panel. Drill pilot holes and use #4 x 5/8" screws.
7. **Install the stay(s)** following Sugatsune's SDS-210 installation drawing (mounting dimensions are measured from the hinge center).
8. **Install the rope limiters**, one per end (see the rope limiter section).
9. **Test:** open and close the lid fully at least 20 times. Check that the stay latches at its hold position and the rope goes taut just after it.

## Rope limiter

The rope is a hard stop that protects the hinge and stay when someone yanks the lid or leans on it while it's open. The stay is the primary hold. The rope must not stop the lid before the stay latches.

- Set the rope to go taut at about **108° to 110°**, just past the stay's 105° hold.
- **Anchors:** one on the inside face of each side panel, below and forward of the hinge. One on the lid underside, forward of the hinge. Both anchors go into face grain.
- Keep each rope clear of the stay's travel path and of contents in the bench.

### Rope length

Use the hinge pivot as the origin, with x pointing forward and y pointing up.

- **Case anchor:** a forward of the pivot and b below it, at (a, -b).
- **Lid anchor:** c forward of the pivot along the lid underside when the lid is closed.
- **Target open angle:** θ (for example 108°).

```
L = sqrt( (a - c*cos(θ))^2 + (c*sin(θ) + b)^2 )
```

Cut the rope to L plus enough extra for the knots, then adjust it on the bench.

## Geometry: wall clearance

At open angle θ beyond 90°, the lid's top front edge ends up behind the case back face by about:

```
clearance ≈ d*sin(θ - 90°) + t*cos(θ - 90°)
```

where d is the lid depth front to back and t is the lid thickness (0.75").

- At θ = 105°: clearance ≈ 0.26*d + 0.72". For a 16" lid, that's about 4.9".
- If a wall stops the lid before the stay's 105° hold, the stay won't latch and the lid will slowly lower itself shut.
- Either keep the bench that far from the wall, or switch to a stay that holds at any angle.

Size the rope target angle (θ) with the available wall clearance in mind.

## Open inputs (to be measured)

- Lid dimensions: length, depth d, thickness t.
- Lid weight. This determines the number of stays.
- Case interior height. Check the stay's installation envelope.
- Distance from the wall where the bench will sit.
- Rope anchor positions a, b and c.

## Tasks for Claude Code

1. Write a small script (Python or Go) that takes the open inputs above and outputs:
   - the required wall clearance at 105° and at the rope stop angle,
   - the rope length L for each end,
   - the recommended number of stays, by comparing lid weight to the 6 to 10 lb per-stay range and flagging anything borderline,
   - the rabbet dimensions, from the measured leaf thickness.
2. Generate a dimensioned side-section SVG of the closed and open states, showing the hinge, the rabbet, the stay and the rope, with dimensions taken from the inputs.
3. Produce a one-page build sheet (markdown) with the computed numbers filled in.

## References

- Rockford piano hinge: https://www.cabinetparts.com/p/rockford-process-control-hinges-piano-continuous-hinge-RPCCP22203S48-p37180
- Sugatsune SDS-210 at Rockler: https://rockler.com/sugatsune-sds-210-soft-down-lid-support
- SDS-200/210 spec sheet (install dimensions): https://www.sugatsune.com/content/site-assets/501_PDF/SDS-200_SDS-210.pdf
- SDS-210 lid weight listing: https://www.hdlusa.com/susds-210-u-conf.html

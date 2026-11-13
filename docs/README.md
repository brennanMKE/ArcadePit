# Design Documentation

Detailed notes for the Arcade Conversation Pit. The [project README](../README.md) has the overview and quick
start.

- [layout.md](layout.md): pit layout and clearances
- [bench.md](bench.md): bench module construction
- [hinge.md](hinge.md): lid hinge, stays and rope limiter
- [lighting.md](lighting.md): display lighting
- [display-contents.md](display-contents.md): display prop themes
- [workflow.md](workflow.md): scripts, outputs and viewers
- [open-items.md](open-items.md): pending decisions and measurements

All dimensions are in millimetres unless noted. The model is the source of truth: if a number here disagrees with
`cad/arcade_pit.py` or `cad/hinge_calc.py`, the code wins. Regenerate and update the doc.

## Coordinate conventions

- **Pit:** origin at the pit centre on the floor. X runs along the table's long axis (player to player), Z is up.
- **Bench (local):** X along the bench length, Y = 0 at the outer display face, increasing toward the seat front
  (the table side), Z = 0 on the floor.

## Design history

How the design got to where it is, so the reasons aren't lost.

1. **Concept.** A classic conversation pit around the arcade table, with storage benches, plywood tops and acrylic
   display windows on the outside. The concept renders are in `raw/` (01–05). The chosen direction is
   `05-wood-top-stainless-continuous-hinge.png`: a wood top on a continuous hinge, not upholstery.
2. **Two bench types (rejected).** At first there were short side benches and long end benches. Each long bench
   was a short bench's width plus twice the depth, so it could cross the ends of the side benches. This was
   dropped because the long benches were too big for two people to move.
3. **One bench size.** Every bench is identical, so any bench fits any spot and each is a two-person carry. Placing
   two per side was considered, then refined.
4. **Gaps on the long sides.** The walk-in gaps sit in the middle of each long side. The player ends and corners are
   closed (3 benches per end), which gives the enclosed pit shape.
5. **Real table.** The table size first came from `raw/Coffee Table - Noisebridge.pdf`. It was then replaced by
   the Onshape model, exported to `raw/Arcade Table.step`. The layout is now derived from that file.
6. **Display contents.** Generic boxes became themed retro game props: cartridges, discs, consoles and toys.
7. **Hinge rework.** The first hinge layout couldn't open properly. The design now follows
   `raw/storage-bench-hinge-spec.md`: a wrap-around steel piano hinge, a full-depth lid with no rear overhang,
   soft-down stays and rope limiters. The fixed rear strip, maple edging and cleat were removed, and the bench went
   to 508 mm deep.
8. **Lighting rework.** The lights moved from under the lid and the end windows to one down-facing LED strip at the
   front, just behind the acrylic. It sits in a routed channel under an opal diffuser, so the items are lit from
   the front and above with no glow from the back.

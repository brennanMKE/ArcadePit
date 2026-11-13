"""Lid hinge calculator for the pit benches (raw/storage-bench-hinge-spec.md).

Wrap-around steel piano hinge on the outside back corner (the display/window side
of a pit bench), Sugatsune SDS-210 soft-down stays, and a rope limiter per end.

Outputs (out/hinge/):
  * printed summary: wall clearance, rope length per end, stay count, rabbet size
  * hinge_section.svg: dimensioned side section, closed and open
  * build_sheet.md: one-page build sheet with the numbers filled in

Run:  python3 cad/hinge_calc.py [--wall 300] [--lid-weight-lb 12.9] [--leaf 0.06] ...
All internal maths is in mm; inch values are printed alongside.
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field, asdict
from pathlib import Path

IN = 25.4
OUT = Path(__file__).resolve().parent.parent / "out" / "hinge"


@dataclass
class Inputs:
    # lid (from the CAD model: bench length minus 1 mm seams each end, full depth, 3/4" ply)
    lid_length: float = 890.0
    lid_depth: float = 508.0           # d, front to back
    lid_thickness: float = 19.05       # t
    lid_weight_lb: float | None = None  # measured; None = estimate from ply density
    ply_density: float = 680.0         # kg/m^3, birch ply
    # hinge
    leaf_thickness_in: float = 0.06    # measure the actual hinge
    rabbet_width_in: float = 11 / 16
    hinge_end_trim_in: float = 0.5     # cut hinge to lid length minus this at each end
    knuckle_dia: float = 5.5
    # stay (Sugatsune SDS-210)
    stay_hold_deg: float = 105.0
    stay_min_lb: float = 6.0
    stay_max_lb: float = 10.0
    # rope limiter: pivot = origin, x forward (into bench), y up
    rope_stop_deg: float = 108.0
    # long a/c and short b make the span change fastest near 105-108 deg (d span/d theta ~ c(a sin - b cos)),
    # giving a few mm between the stay latching and the rope going taut.
    rope_a: float = 150.0              # case anchor forward of pivot (on the solid end panel)
    rope_b: float = 20.0               # case anchor below pivot (in the end liner's notch, on the 18 mm panel)
    rope_c: float = 150.0              # lid anchor forward of pivot (lid underside)
    # site
    wall_distance: float | None = None  # bench back face to wall/obstruction, mm
    case_interior_height: float = 363.0


@dataclass
class Results:
    lid_weight_lb: float
    lid_weight_estimated: bool
    stays: int
    per_stay_lb: float
    stay_flag: str
    clearance_hold: float
    clearance_stop: float
    rope_length: float
    rope_closed_span: float
    rope_slack_closed: float
    rope_span_at_hold: float
    rope_ok: bool
    rope_margin: float
    rabbet_width: float
    rabbet_depth: float
    hinge_length: float
    wall_flag: str
    notes: list = field(default_factory=list)


def clearance(d, t, theta_deg):
    """How far the lid's top front edge ends up behind the case back face."""
    a = math.radians(theta_deg - 90)
    return d * math.sin(a) + t * math.cos(a)


def rope_span(a, b, c, theta_deg):
    th = math.radians(theta_deg)
    return math.hypot(a - c * math.cos(th), c * math.sin(th) + b)


def compute(i: Inputs) -> Results:
    notes = []
    if i.lid_weight_lb is None:
        kg = i.lid_length * i.lid_depth * i.lid_thickness * 1e-9 * i.ply_density
        w, est = kg * 2.20462, True
    else:
        w, est = i.lid_weight_lb, False

    # stays: 1 if the lid is within one stay's range, else one per end
    stays = 1 if w <= i.stay_max_lb else 2
    per = w / stays
    lo, hi = i.stay_min_lb, i.stay_max_lb
    if per < lo:
        flag = f"LIGHT: {per:.1f} lb per stay is under the {lo:.0f} lb minimum; the lid may not close fully"
    elif per > hi:
        flag = f"HEAVY: {per:.1f} lb per stay is over the {hi:.0f} lb maximum; choose a stronger stay"
    elif per - lo < 0.75 or hi - per < 0.75:
        flag = f"BORDERLINE: {per:.1f} lb per stay is near the edge of {lo:.0f}-{hi:.0f} lb; confirm on Sugatsune's chart"
    else:
        flag = f"OK: {per:.1f} lb per stay, inside {lo:.0f}-{hi:.0f} lb"
    if stays > 1 and w > 2 * hi:
        flag = f"HEAVY: {w:.1f} lb needs more than two SDS-210 stays"

    c_hold = clearance(i.lid_depth, i.lid_thickness, i.stay_hold_deg)
    c_stop = clearance(i.lid_depth, i.lid_thickness, i.rope_stop_deg)

    L = rope_span(i.rope_a, i.rope_b, i.rope_c, i.rope_stop_deg)
    closed = rope_span(i.rope_a, i.rope_b, i.rope_c, 0)
    at_hold = rope_span(i.rope_a, i.rope_b, i.rope_c, i.stay_hold_deg)
    rope_ok = at_hold < L - 2.0   # rope must still be slack when the stay latches
    if not rope_ok:
        notes.append("Rope goes taut before the stay latches; move anchors or raise the stop angle.")

    if i.wall_distance is None:
        wall = f"UNKNOWN: keep at least {c_stop:.0f} mm ({c_stop / IN:.1f} in) clear behind each bench"
    elif i.wall_distance >= c_stop:
        wall = f"OK: {i.wall_distance:.0f} mm available, {c_stop:.0f} mm needed at the rope stop"
    elif i.wall_distance >= c_hold:
        wall = (f"TIGHT: lid latches at {i.stay_hold_deg:.0f} deg but touches the wall before the rope stop; "
                f"lower the rope stop angle")
    else:
        wall = (f"BLOCKED: wall stops the lid before the stay latches ({c_hold:.0f} mm needed); "
                f"the lid will lower itself shut. Move the bench or use a free-stop stay")

    return Results(
        lid_weight_lb=w, lid_weight_estimated=est, stays=stays, per_stay_lb=per, stay_flag=flag,
        clearance_hold=c_hold, clearance_stop=c_stop,
        rope_length=L, rope_closed_span=closed, rope_slack_closed=L - closed, rope_span_at_hold=at_hold,
        rope_ok=rope_ok, rope_margin=L - at_hold,
        rabbet_width=i.rabbet_width_in * IN, rabbet_depth=i.leaf_thickness_in * IN,
        hinge_length=i.lid_length - 2 * i.hinge_end_trim_in * IN,
        wall_flag=wall, notes=notes,
    )


# ---------------------------------------------------------------- SVG section
def section_svg(i: Inputs, r: Results, H=457.0, HC=438.0, T=18.0, floor_z=75.0, win_top=393.0, base_h=45.0) -> str:
    """Side section through a bench end, looking along the hinge. Back (display) face
    on the left, seat front on the right. Closed state left, open state right."""
    s = 0.95                        # px per mm
    W_view, gap = 760, 120
    W, Hs = 2 * W_view + gap, 1080
    ink, mute, acc, rope_c, steel = "#1d1b18", "#7b7468", "#c76a12", "#d2541e", "#6d7a86"
    t, d = i.lid_thickness, i.lid_depth
    lt = r.rabbet_depth
    piv = (-lt / 2, HC + lt / 2)    # knuckle centre (x = forward of back face, y = up)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hs}" width="{W}" height="{Hs}" '
           f'font-family="Helvetica, Arial, sans-serif" font-size="12">',
           f'<rect width="{W}" height="{Hs}" fill="#fbfaf7"/>',
           '<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#1d1b18"/></marker></defs>']

    def view(ox, open_deg, title):
        X = lambda x: ox + 200 + x * s
        Y = lambda y: Hs - 70 - y * s
        g = [f'<text x="{ox + 20}" y="34" font-size="16" font-weight="bold" fill="{ink}">{title}</text>']
        # wall line (if known) or required clearance marker
        # case: back (display) panel rails, front (seat) panel, bottom, display floor
        def rect(x0, y0, x1, y1, fill, stroke=ink, dash=None, sw=1.2):
            da = f' stroke-dasharray="{dash}"' if dash else ""
            return (f'<rect x="{X(x0):.1f}" y="{Y(y1):.1f}" width="{(x1 - x0) * s:.1f}" height="{(y1 - y0) * s:.1f}" '
                    f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')
        g += [rect(20, 0, d - 20, base_h - 12, "#4a4a4a", mute), rect(20, base_h - 12, d - 20, base_h, "#3a3a3a"),
              rect(0, base_h, T, floor_z, "#2b2b2b"), rect(0, win_top, T, HC, "#2b2b2b"),
              rect(T, floor_z - 15, T + 6, win_top, "#cfe3f0", mute),
              rect(T, win_top, T + 38, HC - 0.5, "#2b2b2b"),
              rect(T + 7, win_top, T + 7 + 16.7, win_top + 3, "#fff1d6", acc),
              rect(T + 9, win_top + 7.5, T + 9 + 12.7, win_top + 10, "#ffd27a", acc),
              rect(d - T, base_h, d, HC, "#2b2b2b"), rect(T, base_h, d - T, base_h + T, "#2b2b2b"),
              rect(T + 6, floor_z - 12, d - T, floor_z, "#e2c99c", mute)]
        g.append(f'<text x="{X(T + 10):.1f}" y="{Y((floor_z + win_top) / 2):.1f}" fill="{mute}" '
                 f'transform="rotate(-90 {X(T + 10):.1f} {Y((floor_z + win_top) / 2):.1f})" text-anchor="middle">display window</text>')
        g.append(f'<text x="{X(d / 2):.1f}" y="{Y(base_h / 2) + 4:.1f}" fill="#fff" text-anchor="middle">base {base_h:.0f} mm</text>')
        # downlight cone from the LED channel
        cx, cz = T + 15.4, win_top
        g.append(f'<path d="M{X(cx):.1f},{Y(cz):.1f} L{X(cx - 4):.1f},{Y(floor_z + 30):.1f} L{X(cx + 230):.1f},{Y(floor_z + 30):.1f} Z" '
                 f'fill="#ffd27a" opacity="0.18"/>')
        # stay (on the side panel, behind the section plane: dashed)
        g.append(rect(20, HC - 110, 100, HC - 20, "none", steel, "5 3"))
        g.append(f'<text x="{X(60):.1f}" y="{Y(HC - 128):.1f}" fill="{steel}" text-anchor="middle">SDS-210 stay</text>')
        g.append(f'<text x="{X(60):.1f}" y="{Y(HC - 128) + 14:.1f}" fill="{steel}" text-anchor="middle">(on end panel)</text>')

        th = math.radians(open_deg)
        def rot(x, y):  # rotate lid point about the knuckle; positive = front edge up
            dx, dy = x - piv[0], y - piv[1]
            return (piv[0] + dx * math.cos(th) - dy * math.sin(th), piv[1] + dx * math.sin(th) + dy * math.cos(th))
        # lid outline with rabbet, rotated
        rw = r.rabbet_width
        lid = [(0, HC + lt), (rw, HC + lt), (rw, HC), (d, HC), (d, H), (0, H)]
        pts = " ".join(f"{X(px):.1f},{Y(py):.1f}" for px, py in (rot(*p) for p in lid))
        g.append(f'<polygon points="{pts}" fill="#e7cfa3" stroke="{ink}" stroke-width="1.4"/>')
        # hinge: lid leaf (rotates), case leaf (fixed), knuckle
        lf = [rot(2.8, HC + 0.1), rot(rw, HC + 0.1), rot(rw, HC + lt - 0.1), rot(2.8, HC + lt - 0.1)]
        g.append(f'<polygon points="{" ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in lf)}" fill="{steel}"/>')
        g.append(rect(-lt, HC - 0.66 * IN, 0, HC - 2.8, steel, steel))
        g.append(f'<circle cx="{X(piv[0]):.1f}" cy="{Y(piv[1]):.1f}" r="{i.knuckle_dia / 2 * s + 1.2:.1f}" fill="{steel}" stroke="{ink}"/>')
        # rope: case anchor fixed, lid anchor rotates
        ca = (piv[0] + i.rope_a, piv[1] - i.rope_b)
        la = rot(piv[0] + i.rope_c, HC)
        span = math.dist(ca, la)
        if span < r.rope_length - 0.5:
            sag = math.sqrt(max(r.rope_length ** 2 - span ** 2, 0)) / 2
            mx, my = (ca[0] + la[0]) / 2, min(ca[1], la[1]) - sag
            g.append(f'<path d="M{X(ca[0]):.1f},{Y(ca[1]):.1f} Q{X(mx):.1f},{Y(my):.1f} {X(la[0]):.1f},{Y(la[1]):.1f}" '
                     f'fill="none" stroke="{rope_c}" stroke-width="2.4"/>')
        else:
            g.append(f'<line x1="{X(ca[0]):.1f}" y1="{Y(ca[1]):.1f}" x2="{X(la[0]):.1f}" y2="{Y(la[1]):.1f}" '
                     f'stroke="{rope_c}" stroke-width="2.4"/>')
        for p in (ca, la):
            g.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="3.5" fill="#fff" stroke="{rope_c}" stroke-width="2"/>')
        return g, X, Y, rot

    # ---- closed view + dimensions
    g, X, Y, rot = view(20, 0, "CLOSED")
    out += g
    def dim_h(x0, x1, y, label, below=True):
        ty = y + (16 if below else -6)
        return [f'<line x1="{X(x0):.1f}" y1="{Y(y):.1f}" x2="{X(x1):.1f}" y2="{Y(y):.1f}" stroke="{ink}" '
                f'marker-start="url(#ar)" marker-end="url(#ar)"/>',
                f'<text x="{(X(x0) + X(x1)) / 2:.1f}" y="{Y(y) + (14 if below else -6):.1f}" text-anchor="middle" fill="{ink}">{label}</text>']
    def dim_v(x, y0, y1, label, left=True):
        tx = X(x) + (-8 if left else 8)
        return [f'<line x1="{X(x):.1f}" y1="{Y(y0):.1f}" x2="{X(x):.1f}" y2="{Y(y1):.1f}" stroke="{ink}" '
                f'marker-start="url(#ar)" marker-end="url(#ar)"/>',
                f'<text x="{tx:.1f}" y="{(Y(y0) + Y(y1)) / 2 + 4:.1f}" text-anchor="{"end" if left else "start"}" fill="{ink}">{label}</text>']
    out += dim_h(0, d, H + 80, f"d = {d:.0f} mm ({d / IN:.1f}\")", below=False)
    out += dim_v(d + 30, HC, H, f"t = {t:.2f} mm (3/4\")", left=False)
    out += dim_v(d + 30, 0, H, "")
    out.append(f'<text x="{X(d + 38):.1f}" y="{Y(H / 2):.1f}" fill="{ink}">seat {H:.0f} mm</text>')
    # rabbet callout
    out.append(f'<line x1="{X(r.rabbet_width / 2):.1f}" y1="{Y(HC + 1):.1f}" x2="{X(70):.1f}" y2="{Y(H + 34):.1f}" stroke="{ink}"/>')
    out.append(f'<text x="{X(73):.1f}" y="{Y(H + 34) + 4:.1f}" fill="{ink}">rabbet {r.rabbet_width:.1f} x {r.rabbet_depth:.2f} mm deep '
               f'({i.rabbet_width_in * 16:.0f}/16" x {i.leaf_thickness_in:.3f}")</text>')
    out.append(f'<line x1="{X(-2):.1f}" y1="{Y(HC):.1f}" x2="{X(-90):.1f}" y2="{Y(HC + 60):.1f}" stroke="{ink}"/>')
    out.append(f'<text x="{X(-92):.1f}" y="{Y(HC + 64):.1f}" text-anchor="end" fill="{ink}">piano hinge, knuckle at</text>')
    out.append(f'<text x="{X(-92):.1f}" y="{Y(HC + 64) + 14:.1f}" text-anchor="end" fill="{ink}">outside back corner</text>')
    out.append(f'<line x1="{X(T + 15):.1f}" y1="{Y(win_top - 1):.1f}" x2="{X(150):.1f}" y2="{Y(win_top - 175):.1f}" stroke="{acc}"/>')
    out.append(f'<text x="{X(153):.1f}" y="{Y(win_top - 175) + 4:.1f}" fill="{acc}">LED header: strip faces down in a 1/2" routed</text>')
    out.append(f'<text x="{X(153):.1f}" y="{Y(win_top - 175) + 18:.1f}" fill="{acc}">channel, opal diffuser flush; acrylic slides up under it</text>')
    # rope anchor dims
    piv = (-r.rabbet_depth / 2, HC + r.rabbet_depth / 2)
    out += dim_h(piv[0], piv[0] + i.rope_a, piv[1] - i.rope_b - 22, f"a {i.rope_a:.0f} (case eye)")
    out += dim_v(piv[0] + i.rope_a + 14, piv[1] - i.rope_b, piv[1], f"b {i.rope_b:.0f}", left=False)
    out += dim_h(piv[0], piv[0] + i.rope_c, HC - 75, f"c {i.rope_c:.0f} (lid eye)")
    out.append(f'<text x="{X(0):.1f}" y="{Hs - 40}" fill="{mute}">BACK (display face)</text>')
    out.append(f'<text x="{X(d):.1f}" y="{Hs - 40}" text-anchor="end" fill="{mute}">SEAT FRONT (pit side)</text>')

    # ---- open view at the rope stop
    ox = 20 + W_view + gap
    g, X2, Y2, rot2 = view(ox, i.rope_stop_deg, f"OPEN: stay holds {i.stay_hold_deg:.0f}°, rope stop {i.rope_stop_deg:.0f}°")
    out += g
    # clearance behind the back face
    c = r.clearance_stop
    out.append(f'<line x1="{X2(-c):.1f}" y1="{Y2(0):.1f}" x2="{X2(-c):.1f}" y2="{Y2(H + 520):.1f}" stroke="{acc}" stroke-dasharray="6 4"/>')
    out += [f'<line x1="{X2(-c):.1f}" y1="{Y2(60):.1f}" x2="{X2(0):.1f}" y2="{Y2(60):.1f}" stroke="{acc}" '
            f'marker-start="url(#ar)" marker-end="url(#ar)"/>',
            f'<text x="{X2(-c / 2):.1f}" y="{Y2(60) - 8:.1f}" text-anchor="middle" fill="{acc}">{c:.0f} mm ({c / IN:.1f}")</text>',
            f'<text x="{X2(-c) - 6:.1f}" y="{Y2(140):.1f}" text-anchor="end" fill="{acc}">min. wall</text>',
            f'<text x="{X2(-c) - 6:.1f}" y="{Y2(140) + 14:.1f}" text-anchor="end" fill="{acc}">clearance</text>']
    # angle arc
    pv = (-r.rabbet_depth / 2, HC + r.rabbet_depth / 2)
    R = 120
    a0, a1 = 0, math.radians(i.rope_stop_deg)
    p0 = (pv[0] + R, pv[1])
    p1 = (pv[0] + R * math.cos(a1), pv[1] + R * math.sin(a1))
    out.append(f'<path d="M{X2(p0[0]):.1f},{Y2(p0[1]):.1f} A{R * 0.95:.1f},{R * 0.95:.1f} 0 0 0 {X2(p1[0]):.1f},{Y2(p1[1]):.1f}" '
               f'fill="none" stroke="{ink}" stroke-dasharray="3 3"/>')
    out.append(f'<text x="{X2(pv[0] + 70):.1f}" y="{Y2(pv[1] + 70):.1f}" fill="{ink}">θ = {i.rope_stop_deg:.0f}°</text>')
    out.append(f'<text x="{X2(140):.1f}" y="{Y2(HC - 170):.1f}" fill="{rope_c}">rope L = {r.rope_length:.0f} mm, taut</text>')
    out.append(f'<text x="{X2(0):.1f}" y="{Hs - 40}" fill="{mute}">BACK (display face)</text>')
    out.append('</svg>')
    return "\n".join(out)


# ---------------------------------------------------------------- build sheet
def build_sheet(i: Inputs, r: Results, n_benches=10) -> str:
    f = lambda mm: f"{mm:.0f} mm ({mm / IN:.2f}\")"
    w_note = "estimated from 3/4\" birch ply" if r.lid_weight_estimated else "measured"
    rope_cut = r.rope_length + 2 * 60
    return f"""# Pit Bench Lid Hinge: Build Sheet

Per bench, ×{n_benches} benches. Generated by `cad/hinge_calc.py` from `raw/storage-bench-hinge-spec.md`.
Section drawing: `hinge_section.svg`.

## Design

Steel piano hinge wrapped around the **outside top corner of the display (window) face**. The case leaf screws
to the black frame rail above the window; the lid leaf sits in a rabbet under the lid's back edge. The lid lifts
at the seat front and swings back over the display side. Nothing is proud on the seat. Every screw goes into
plywood face grain.

## Numbers

| Item | Value |
|---|---|
| Lid | {i.lid_length:.0f} × {i.lid_depth:.0f} × {i.lid_thickness:.2f} mm, **{r.lid_weight_lb:.1f} lb** ({w_note}) |
| Piano hinge | Steel, 1-1/2" open width, 0.66" leaf, cut to **{f(r.hinge_length)}** (lid length − 1/2" each end) |
| Rabbet (lid underside, back edge) | **{r.rabbet_width:.1f} mm wide × {r.rabbet_depth:.2f} mm deep** ({i.rabbet_width_in * 16:.0f}/16" × {i.leaf_thickness_in:.3f}"). Re-cut depth to the measured leaf. |
| Screws | Lid leaf #4 FH × 1/2"; case leaf #4 FH × 5/8"; every hole (2" spacing) |
| Stays | **{r.stays} × Sugatsune SDS-210** ({'one per end' if r.stays == 2 else 'one'}). {r.stay_flag} |
| Stay hold | {i.stay_hold_deg:.0f}° |
| Rope stop | {i.rope_stop_deg:.0f}° |
| Rope anchors (from knuckle) | case a = {i.rope_a:.0f} mm forward, b = {i.rope_b:.0f} mm down; lid c = {i.rope_c:.0f} mm forward |
| Rope length L (each end) | **{f(r.rope_length)}** knot-to-knot; cut ≈ {rope_cut:.0f} mm and adjust |
| Rope check | span at {i.stay_hold_deg:.0f}° = {r.rope_span_at_hold:.0f} mm, so the rope is **{r.rope_margin:.1f} mm** short of taut when the stay latches {'✓' if r.rope_ok else '✗ too tight'}. Tie with an adjustable knot (taut-line hitch) and set it on the bench. {r.rope_slack_closed:.0f} mm of slack hangs inside when closed. |
| Wall clearance behind each bench | {f(r.clearance_hold)} at {i.stay_hold_deg:.0f}°, **{f(r.clearance_stop)}** at {i.rope_stop_deg:.0f}° |
| Site | {r.wall_flag} |

## Build steps

1. Measure the hinge leaf thickness; set the rabbet depth to match.
2. Cut the rabbet under the lid's back edge: {r.rabbet_width:.1f} mm wide × leaf depth.
3. Cut the hinge to {r.hinge_length:.0f} mm; file the ends.
4. Screw the lid leaf into the rabbet, knuckle centre on the lid's back edge (#4 × 1/2", pilot holes).
5. Set the lid closed on the case, back edge flush with the display face; clamp.
6. Screw the case leaf to the frame rail above the window (#4 × 5/8", pilot holes). Keep the leaf inside the 45 mm rail so it never crosses the window.
7. Fit {r.stays} SDS-210 stay{'s' if r.stays > 1 else ''} to each solid 18 mm end panel, in the notch at the top of the end liner. Use Sugatsune's drawing, measured from the hinge centre.
8. Fit the rope limiters inboard of each stay: screw eyes into the end panel face and the lid underside at a, b, c above.
9. Open and close 20 times. The stay must latch at {i.stay_hold_deg:.0f}° before the rope goes taut at {i.rope_stop_deg:.0f}°.

## Still to measure

- Actual leaf thickness and lid weight (re-run with `--leaf` and `--lid-weight-lb`).
- Clearance behind each bench where the pit is placed (re-run with `--wall`).
- Stay envelope against the {i.case_interior_height:.0f} mm interior height.
""" + ("".join(f"\n> {n}" for n in r.notes))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for k, v in asdict(Inputs()).items():
        ap.add_argument("--" + k.replace("_", "-"), type=float, default=v)
    ap.add_argument("--wall", type=float, default=None, help="bench back face to wall, mm")
    ap.add_argument("--leaf", type=float, default=None, help="measured leaf thickness, inches")
    args = vars(ap.parse_args(argv))
    wall, leaf = args.pop("wall"), args.pop("leaf")
    inp = Inputs(**{k: args[k] for k in asdict(Inputs())})
    if wall is not None:
        inp.wall_distance = wall
    if leaf is not None:
        inp.leaf_thickness_in = leaf
    res = compute(inp)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "hinge_section.svg").write_text(section_svg(inp, res))
    (OUT / "build_sheet.md").write_text(build_sheet(inp, res))
    print(f"lid weight      {res.lid_weight_lb:.1f} lb ({'est.' if res.lid_weight_estimated else 'measured'})")
    print(f"stays           {res.stays} x SDS-210  -> {res.stay_flag}")
    print(f"wall clearance  {res.clearance_hold:.0f} mm @ {inp.stay_hold_deg:.0f} deg, {res.clearance_stop:.0f} mm @ {inp.rope_stop_deg:.0f} deg  -> {res.wall_flag}")
    print(f"rope L          {res.rope_length:.0f} mm per end, {res.rope_margin:.1f} mm slack at stay hold (ok={res.rope_ok}), {res.rope_slack_closed:.0f} mm slack closed")
    print(f"rabbet          {res.rabbet_width:.1f} x {res.rabbet_depth:.2f} mm")
    print(f"hinge length    {res.hinge_length:.0f} mm")
    print("wrote", OUT / "hinge_section.svg", OUT / "build_sheet.md")


if __name__ == "__main__":
    main()

"""Arcade conversation pit: one parametric bench module + the Noisebridge coffee table.

Layout (plan, table long axis = X):

     ┌───┐┌─────────┐         ┌─────────┐┌───┐
     │   ││         │   gap   │         ││   │
     │   │└─────────┘         └─────────┘│   │
     ├───┤                               ├───┤
     │   │        [ coffee table ]       │   │   player ends: 3 benches run
     ├───┤                               ├───┤   full width, closing corners
     │   │┌─────────┐         ┌─────────┐│   │
     │   ││         │   gap   │         ││   │
     └───┘└─────────┘         └─────────┘└───┘

All 10 benches are identical (one window on the outer face; solid wood ends for strength) so any
bench fits any spot and each is a two-person carry.  Everything is derived from
the table size and the knee-room clearances below.

The table is the real Noisebridge coffee table, exported from Onshape
(Super Assembly) to raw/Arcade Table.step.  Its size drives the layout.

Run:  uv run --python 3.12 --with build123d python cad/arcade_pit.py
Units: mm.  Bench frame: X = length, Y = depth (Y=0 outer/display face), Z = up.
"""
from __future__ import annotations

import base64
import json
import random
from pathlib import Path

import sys

import numpy as np
from build123d import (Align, Box, Compound, Cylinder, Location, Rotation,
                       Sphere, Axis, export_step, fillet)

# ---------------------------------------------------------------- parameters
# Coffee table: real model from Onshape.  Size is measured from the STEP on load;
# the fallback numbers are only used if the file is missing.
TABLE_STEP = Path(__file__).resolve().parent.parent / "raw" / "Arcade Table.step"
TBL_TOP_T = 88.9                              # top frame thickness (3.5")
CTRL_OVERHANG = 0.0                           # controller boxes sit inside the top


def _table_size():
    if TABLE_STEP.exists():
        from build123d import import_step
        bb = import_step(str(TABLE_STEP)).bounding_box()
        top_z = max(sl.bounding_box().max.Z for sl in import_step(str(TABLE_STEP)).solids()
                    if sl.bounding_box().size.X > 1000 and sl.bounding_box().size.Z < 150)
        return bb.size.X, bb.size.Y, top_z - bb.min.Z, True
    return 1708.2, 730.2, 514.6, False


TBL_L, TBL_W, TBL_H, TABLE_FROM_STEP = _table_size()   # top length, width, height to top

# Knee room from bench front to table edge
CLEAR_END = 480.0    # player ends (must reach controls)
CLEAR_SIDE = 465.0   # long sides
END_BENCHES = 3      # benches across each player end
GAP_MIN = 915.0      # walk-in gap at least 36"

D = 508.0            # bench depth (20")
INNER_W = TBL_W + 2 * CLEAR_SIDE                      # clear space inside, across table
L = (INNER_W + 2 * D) / END_BENCHES                   # the one bench length
# along the table: player knee room, widened if needed so the gaps stay walkable
INNER_L = max(TBL_L + 2 * CTRL_OVERHANG + 2 * CLEAR_END, 2 * L + GAP_MIN)
CLEAR_END = (INNER_L - TBL_L - 2 * CTRL_OVERHANG) / 2
GAP = INNER_L - 2 * L                                 # walk-in gap, centred on long sides
XO, YO = INNER_L / 2 + D, INNER_W / 2 + D             # outer half-extents (carcass)
H = 457.0          # finished seat height (18")
T_TOP = 19.0       # plywood top (3/4")
T = 18.0           # black carcass panels
T_ACR = 6.0        # acrylic window
T_LINER = 6.0      # plywood interior liner
T_FLOOR = 12.0     # plywood display floor
OVERHANG = 0.0     # no rear overhang: lid back edge is flush with the display face (hinge spec)
SEAM = 1.0         # half-gap between neighbouring tops
# Lid hinge (raw/storage-bench-hinge-spec.md): one full-depth 3/4" lid, steel piano
# hinge wrapped round the OUTSIDE TOP CORNER of the display face.  Case leaf on the
# frame rail above the window, lid leaf in a rabbet under the lid's back edge, knuckle
# on the corner.  Nothing proud on the seat; every screw in face grain.  Two Sugatsune
# SDS-210 soft-down stays (hold 105 deg) and a rope limiter per end (stop 108 deg).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hinge_calc  # noqa: E402

HINGE_IN = hinge_calc.Inputs()
LEAF_T = HINGE_IN.leaf_thickness_in * 25.4        # rabbet depth = leaf thickness
RABBET_W = HINGE_IN.rabbet_width_in * 25.4        # 11/16"
LEAF_W = 0.66 * 25.4                              # 0.66" leaf
KNUCKLE_R = HINGE_IN.knuckle_dia / 2
STAY_HOLD = HINGE_IN.stay_hold_deg
ROPE_STOP = HINGE_IN.rope_stop_deg
# End liners are notched at the top front so the stays and rope eyes mount on the solid 18 mm end panel
LINER_NOTCH_Y = 200.0   # notch depth from the display face (clears the stay arm's travel)
LINER_NOTCH_H = 125.0   # notch height down from the carcass top

# Display lighting: LED strip facing DOWN, just behind the front acrylic, in a channel
# routed into the underside of a black LED header glued behind the frame's top rail.
# The front acrylic slides up under the header (which captures its top edge).
# An opal acrylic diffuser sits flush in a rebate over the channel.
HEADER_D = 38.0          # header depth behind the frame rail (1-1/2")
LED_CH_W = 12.7          # 1/2" router bit channel for a 10 mm strip
LED_CH_D = 10.0          # channel depth
DIFF_W = LED_CH_W + 4.0  # diffuser rebate, 2 mm wider each side
DIFF_T = 3.0             # 1/8" opal acrylic diffuser
HINGE_INSET = 20.0 # hinge stops short of each lid end
BORDER_SIDE = 45.0
BORDER_TOP = 45.0
BORDER_BOT = 75.0  # black base rail below window
MULLION = 40.0
HC = H - T_TOP     # carcass top (Z of the lid underside, from the room floor)
FLOOR_Z = BORDER_BOT  # display floor top surface aligns with window bottom

# Base: each bench drops onto its own low base.  The base fills the dead space that used
# to sit under the display floor, so seat height, windows and display height are unchanged:
# base 45 + bench bottom 18 + display floor 12 = window bottom at 75.
BASE_H = 45.0        # base height; the bench bottom sits on it
BASE_TOP = 12.0      # base top plate (ply)
BASE_RAIL = 18.0     # base frame rails (ply)
BASE_SET = 20.0      # base set back from the display face and seat front (toe kick)
# Locating pins: steel, in the bench bottom, drop into bushed holes in the base top plate.
# They protrude further than the connector so they align the bench before it mates.
PIN_R = 6.0
PIN_L = 25.0         # below the bench bottom
PIN_X = 90.0         # from each bench end, on the depth centreline
# Blind-mate 5 V connector: Anderson Powerpole pair (red +5 V, black GND), bench half fixed
# in the bench bottom, base half in a floating bracket.  Under the wire chase at the left end.
PP = 7.9             # Powerpole housing cross-section
PP_L = 24.6          # housing length
CONN_X, CONN_Y = 40.0, 48.0   # pair centre, bench-local
CONN_DROP = 12.0     # bench half protrudes this far below the bench bottom (< PIN_L)
# Wire chase: black raceway up the inside of the display face, hidden behind the 45 mm side
# border, from the connector to the end of the LED header.  The far end of the strip is fed by
# a pair run back along the LED channel, so both ends get power.
CHASE_X = (35.0, 44.5)
CHASE_Y = (T + T_ACR + 1, 55.0)
assert abs(BASE_H + T + T_FLOOR - FLOOR_Z) < 0.01, "base + bottom + display floor must meet the window"
assert PIN_L > CONN_DROP + 8, "pins must engage before the connector"

OUT = Path(__file__).resolve().parent.parent / "out"


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3).moved(
        Location((x0, y0, z0)))


class Part:
    def __init__(self, name, shape, mat, color=None, lid=None):
        self.name, self.shape, self.mat, self.color, self.lid = name, shape, mat, color, lid


# ---------------------------------------------------------------- shared top
def top_parts(xa, xb, y_outer, y_inner, lid_index=0, tag=""):
    """Full-depth lid on a wrap-around piano hinge at the outer top corner.
    Returns parts, pivot (+ rope anchors), hinge length."""
    xa, xb = xa + SEAM, xb - SEAM
    hinge_len = (xb - xa) - 2 * HINGE_IN.hinge_end_trim_in * 25.4
    hx = xa + HINGE_IN.hinge_end_trim_in * 25.4
    y_ax, z_ax = -LEAF_T / 2, HC + LEAF_T / 2          # knuckle on the corner, at the leaves' mid-planes
    knuckle_seat = Cylinder(KNUCKLE_R + 0.4, xb - xa + 2, rotation=(0, 90, 0),
                            align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((xa - 1, y_ax, z_ax)))
    lid = box(xa, xb, 0, y_inner, HC, H)
    lid -= box(xa - 1, xb + 1, -1, RABBET_W, HC - 1, HC + LEAF_T)   # rabbet for the lid leaf
    lid -= knuckle_seat
    parts = [Part(f"lid{tag}", lid, "ply", lid=lid_index)]
    # piano hinge: lid leaf in the rabbet (moves), case leaf on the display face rail (fixed)
    parts.append(Part(f"hinge_leaf_lid{tag}", box(hx, hx + hinge_len, KNUCKLE_R, RABBET_W - 0.5, HC, HC + LEAF_T),
                      "steel", lid=lid_index))
    parts.append(Part(f"hinge_leaf_case{tag}", box(hx, hx + hinge_len, -LEAF_T, 0, HC - LEAF_W + KNUCKLE_R, HC - KNUCKLE_R),
                      "steel"))
    knuckle = Cylinder(KNUCKLE_R, hinge_len, rotation=(0, 90, 0),
                       align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((hx, y_ax, z_ax)))
    parts.append(Part(f"hinge_knuckle{tag}", knuckle, "steel"))
    for i in range(int(hinge_len // 50.8)):          # #4 FH screws, 2" spacing, face grain
        x = hx + 25.4 + i * 50.8
        parts.append(Part(f"screw_case{tag}_{i}", Cylinder(2.8, 0.6, rotation=(90, 0, 0),
                     align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
                     Location((x, -LEAF_T, HC - LEAF_W / 2))), "steel"))
    # SDS-210 soft-down stays, one per end, on the solid zone of each end panel
    for i, (xs, sgn) in enumerate(((xa + T - SEAM, 1), (xb - T + SEAM, -1))):
        x0, x1 = (xs, xs + 16) if sgn > 0 else (xs - 16, xs)
        parts.append(Part(f"stay_body{tag}_{i}", box(x0, x1, T + T_ACR + 3, 100, HC - 120, HC - 22), "stay"))
        parts.append(Part(f"stay_arm{tag}_{i}", box(x0 + 3, x1 - 3, 30, 190, HC - 9, HC - 1), "stay", lid=lid_index))
    # rope limiter anchors (pivot-relative, from hinge_calc), inboard of each stay
    rope = {"a": HINGE_IN.rope_a, "b": HINGE_IN.rope_b, "c": HINGE_IN.rope_c,
            "L": hinge_calc.rope_span(HINGE_IN.rope_a, HINGE_IN.rope_b, HINGE_IN.rope_c, ROPE_STOP),
            "x": [xa - SEAM + T + 22, xb + SEAM - T - 22],   # rope plane, inboard of the stay
            "lid_dz": (HC - 4) - (HC + LEAF_T / 2)}
    for i, xr in enumerate(rope["x"]):
        yc, zc = y_ax + rope["a"], z_ax - rope["b"]
        x_face = T if i == 0 else LENGTH_HINT[0] - T
        parts.append(Part(f"rope_eye_shank{tag}_{i}", box(min(x_face, xr), max(x_face, xr), yc - 1.5, yc + 1.5,
                                                          zc - 1.5, zc + 1.5), "steel"))
        parts.append(Part(f"rope_eye_case{tag}_{i}", Sphere(4).moved(Location((xr, yc, zc))), "steel"))
        parts.append(Part(f"rope_eye_lid{tag}_{i}", Sphere(4).moved(
            Location((xr, y_ax + rope["c"], HC - 4))), "steel", lid=lid_index))
    pivot = {"y": y_ax, "z": z_ax, "dir": 1, "max": ROPE_STOP, "hold": STAY_HOLD, "rope": rope}
    return parts, pivot, hinge_len


LED_SPEC = {}
LENGTH_HINT = [0.0]   # set by bench() so the cleat spans the carcass


# ---------------------------------------------------------------- contents
CASE_COLORS = ["#c0392b", "#1f4e9c", "#2e8b57", "#d4a017", "#6a2c91", "#e86a17",
               "#202020", "#b03a6f", "#3a7bd5", "#f2f2f2", "#8b0000", "#0f6b6b"]


def contents(rng, x0, x1, y0, y1, prefix):
    """Generic display items: game cases on edge, a console-sized box, a controller-ish puck."""
    parts = []
    x = x0 + 10
    span = x1 - x0
    n_cases = int(span * 0.35 // 15)
    for i in range(n_cases):
        h = rng.choice([190, 190, 170, 135])
        c = box(x, x + 14, y0 + 40, y0 + 175, FLOOR_Z, FLOOR_Z + h)
        parts.append(Part(f"{prefix}case_{i}", c, "item", rng.choice(CASE_COLORS)))
        x += 15
    x += 25
    w = min(280.0, x1 - x - 20)
    if w > 150:
        parts.append(Part(f"{prefix}console", box(x, x + w, y0 + 30, y0 + 230, FLOOR_Z, FLOOR_Z + 75),
                          "item", rng.choice(["#d9d9de", "#3b3b40", "#5b4b8a"])))
        parts.append(Part(f"{prefix}console_top", box(x + 20, x + w - 30, y0 + 50, y0 + 210,
                                                     FLOOR_Z + 75, FLOOR_Z + 135),
                          "item", rng.choice(["#2a2a2e", "#c9c9cf", "#7a1f1f"])))
        pad = Cylinder(45, 30, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((x + w / 2, y0 + 300, FLOOR_Z)))
        parts.append(Part(f"{prefix}pad", pad, "item", rng.choice(["#9a9aa2", "#24242a"])))
    return parts


# ---------------------------------------------------------------- base + 5 V power
def pp_pair(x_mid, y0, y1, z0, z1, tag, along="z"):
    """Anderson Powerpole pair: red (+5 V) then black (GND) side by side along X."""
    return [Part(f"{tag}_pos", box(x_mid - PP, x_mid, y0, y1, z0, z1), "pp_red"),
            Part(f"{tag}_gnd", box(x_mid, x_mid + PP, y0, y1, z0, z1), "pp_black")]


def power_parts_bench(length):
    """Bench-side power hardware: locating pins, fixed connector half, wire chase."""
    from build123d import Cone
    p = []
    for i, x in enumerate((PIN_X, length - PIN_X)):
        z_tip = BASE_H - PIN_L
        pin = Cylinder(PIN_R, PIN_L - 6 + T, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((x, D / 2, z_tip + 6)))
        pin += Cone(PIN_R / 2, PIN_R, 6, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((x, D / 2, z_tip)))
        p.append(Part(f"pin_{i}", pin, "steel"))
    z0 = BASE_H - CONN_DROP
    p += pp_pair(CONN_X, CONN_Y - PP / 2, CONN_Y + PP / 2, z0, z0 + PP_L, "conn_bench")
    p.append(Part("wire_chase", box(*CHASE_X, *CHASE_Y, BASE_H + T, HC - BORDER_TOP), "black"))
    return p


def base_parts(length, power=False):
    """Low base the bench drops onto.  Open-bottom ply frame under a 12 mm top plate, with
    cable slots through every rail so each bench's 5 V run can pass through its neighbours.
    power=True adds the fused distribution block and the feeder inlet (middle end bench)."""
    x0, x1, y0, y1 = SEAM, length - SEAM, BASE_SET, D - BASE_SET
    zt, R = BASE_H - BASE_TOP, BASE_RAIL
    slot_z = (4.0, 26.0)
    p = []
    top = box(x0, x1, y0, y1, zt, BASE_H)
    top -= box(CONN_X - PP - 1.5, CONN_X + PP + 1.5, CONN_Y - PP / 2 - 1.5, CONN_Y + PP / 2 + 1.5, zt - 1, BASE_H + 1)
    for i, x in enumerate((PIN_X, length - PIN_X)):
        hole = Cylinder(PIN_R + 2, BASE_TOP + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((x, D / 2, zt - 1)))
        top -= hole
        bush = Cylinder(PIN_R + 2, BASE_TOP, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((x, D / 2, zt)))
        bush -= Cylinder(PIN_R + 0.4, BASE_TOP + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((x, D / 2, zt - 1)))
        p.append(Part(f"base_bushing_{i}", bush, "steel"))
    p.append(Part("base_top", top, "base_ply"))
    front = box(x0, x1, y0, y0 + R, 0, zt)
    back = box(x0, x1, y1 - R, y1, 0, zt)
    for a, b in ((x0 + 40, x0 + 220), (x1 - 220, x1 - 40)):
        back -= box(a, b, y1 - R - 1, y1 + 1, *slot_z)
    ys = (y0 + R + 60, y1 - R - 60)
    rails = [box(x0, x0 + R, y0 + R, y1 - R, 0, zt), box(x1 - R, x1, y0 + R, y1 - R, 0, zt),
             box(length / 2 - R / 2, length / 2 + R / 2, y0 + R, y1 - R, 0, zt)]
    rails = [r - box(r.bounding_box().min.X - 1, r.bounding_box().max.X + 1, *ys, *slot_z) for r in rails]
    # floating bracket for the base connector half, screwed to the front rail
    br = box(CONN_X - 14, CONN_X + 14, y0 + R, CONN_Y + 10, 4, zt)
    br -= box(CONN_X - PP - 0.6, CONN_X + PP + 0.6, CONN_Y - PP / 2 - 0.6, CONN_Y + PP / 2 + 0.6, 3, zt + 1)
    p.append(Part("base_conn_bracket", br, "base_ply"))
    z1 = BASE_H - CONN_DROP
    p += pp_pair(CONN_X, CONN_Y - PP / 2, CONN_Y + PP / 2, z1 - PP_L, z1, "conn_base")
    if power:
        fx = length / 2 + 110
        p.append(Part("fuse_block", box(fx - 60, fx + 60, D / 2 - 35, D / 2 + 35, zt - 28, zt), "stay"))
        ix = length / 2 + 100
        front -= box(ix - PP - 0.5, ix + PP + 0.5, y0 - 1, y0 + R + 1, 12 - 0.5, 12 + PP + 0.5)
        p += pp_pair(ix, y0 - 10, y0 - 10 + PP_L, 12, 12 + PP, "feeder_inlet")
    p.append(Part("base_front", front, "base_ply"))
    p.append(Part("base_back", back, "base_ply"))
    for k, r in enumerate(rails):
        p.append(Part(f"base_rail_{k}", r, "base_ply"))
    return p


POWER = {"conn": [CONN_X, CONN_Y], "fuse": None, "feeder": None}


# ---------------------------------------------------------------- variants
def bench(length, n_bays, end_windows, n_lids, seed):
    """Generic display bench.  Returns parts, pivots, lights, spec dict."""
    rng = random.Random(seed)
    p = []
    wz0, wz1 = BORDER_BOT, HC - BORDER_TOP
    win_h = wz1 - wz0

    # top spans: outer overhang on display face, and on exposed ends
    ox = 0.0  # ends butt neighbours: no end overhang
    t0, t1 = -ox, length + ox
    splits = [t0 + k * (t1 - t0) / n_lids for k in range(n_lids + 1)]
    # bay boundaries (mullions/dividers) line up with lid joints
    bays = [0.0] + [splits[k] for k in range(1, n_bays)] + [length] if n_bays == n_lids else \
           [k * length / n_bays for k in range(n_bays + 1)]

    # outer display face with one window per bay
    face = box(0, length, 0, T, BASE_H, HC)
    win_w = []
    for k in range(n_bays):
        a = bays[k] + (BORDER_SIDE if k == 0 else MULLION / 2)
        b = bays[k + 1] - (BORDER_SIDE if k == n_bays - 1 else MULLION / 2)
        face -= box(a, b, -1, T + 1, wz0, wz1)
        win_w.append(b - a)
    p.append(Part("display_face", face, "black"))
    p.append(Part("acrylic", box(BORDER_SIDE - 15, length - BORDER_SIDE + 15, T, T + T_ACR,
                                 wz0 - 15, wz1), "acrylic"))   # top edge captured under the LED header
    # LED header: between the stays, routed channel + diffuser rebate in its underside
    hx0, hx1 = T + 20, length - T - 20
    ch_y0 = T + T_ACR + 3                        # channel starts 3 mm behind the acrylic
    lx0, lx1 = BORDER_SIDE, length - BORDER_SIDE
    header = box(hx0, hx1, T, T + HEADER_D, wz1, HC - 0.5)
    header -= box(lx0, lx1, ch_y0, ch_y0 + LED_CH_W, wz1 - 1, wz1 + LED_CH_D)
    header -= box(lx0 - 2, lx1 + 2, ch_y0 - 2, ch_y0 + LED_CH_W + 2, wz1 - 1, wz1 + DIFF_T)
    p.append(Part("led_header", header, "black"))
    p.append(Part("led_strip", box(lx0 + 2, lx1 - 2, ch_y0 + 1.3, ch_y0 + LED_CH_W - 1.3,
                                   wz1 + LED_CH_D - 2.5, wz1 + LED_CH_D), "led"))
    p.append(Part("led_diffuser", box(lx0 - 2, lx1 + 2, ch_y0 - 2, ch_y0 + LED_CH_W + 2, wz1, wz1 + DIFF_T),
                  "diffuser"))
    LED_SPEC.update({"strip_len": lx1 - lx0, "channel": [LED_CH_W, LED_CH_D], "diffuser": [DIFF_W, DIFF_T],
                     "header": [hx1 - hx0, HEADER_D, HC - 0.5 - wz1], "y": ch_y0 + LED_CH_W / 2, "z": wz1})
    LENGTH_HINT[0] = length
    inner = box(0, length, D - T, D, BASE_H, HC)
    # finger pull: scoop in the top of the seat-front panel, centred
    inner -= box(length / 2 - 70, length / 2 + 70, D - T - 1, D + 1, HC - 22, HC + 1)
    p.append(Part("inner_face", inner, "black"))
    bottom = box(T, length - T, T, D - T, BASE_H, BASE_H + T)
    p += power_parts_bench(length)
    for pt in p:
        if pt.name.startswith(("pin_", "conn_bench")):
            bottom -= pt.shape
    p.append(Part("bottom", bottom, "black"))

    # ends: solid 18 mm panels (structural) with a birch liner, or optional windows
    end_win_w = 0.0
    for side, (x0, x1) in (("l", (0, T)), ("r", (length - T, length))):
        end = box(x0, x1, T, D - T, BASE_H, HC)
        if end_windows:
            ya, yb = 125.0, D - T - BORDER_SIDE + 5
            end -= box(x0 - 1, x1 + 1, ya, yb, wz0, wz1)
            end_win_w = yb - ya
            ax0, ax1 = (T, T + T_ACR) if side == "l" else (length - T - T_ACR, length - T)
            p.append(Part(f"acrylic_end_{side}", box(ax0, ax1, 115.0, D - T - 25, wz0 - 15, wz1 + 15), "acrylic"))
        else:
            ex0, ex1 = (T, T + T_LINER) if side == "l" else (length - T - T_LINER, length - T)
            liner = box(ex0, ex1, T + T_ACR, D - T - T_LINER, FLOOR_Z, HC)
            liner -= box(ex0 - 1, ex1 + 1, T, LINER_NOTCH_Y, HC - LINER_NOTCH_H, HC + 1)
            p.append(Part(f"end_liner_{side}", liner, "ply"))
        p.append(Part(f"end_{side}", end, "black"))

    inset = T + (T_ACR if end_windows else T_LINER)
    dfloor = box(T, length - T, T + T_ACR, D - T, FLOOR_Z - T_FLOOR, FLOOR_Z)
    dfloor -= box(CHASE_X[0] - 0.5, CHASE_X[1] + 0.5, T, CHASE_Y[1] + 0.5, FLOOR_Z - T_FLOOR - 1, FLOOR_Z + 1)
    p.append(Part("display_floor", dfloor, "ply"))
    p.append(Part("back_liner", box(T, length - T, D - T - T_LINER, D - T, FLOOR_Z, HC), "ply"))
    for k in range(1, n_bays):
        x = bays[k]
        p.append(Part(f"divider_{k}", box(x - 6, x + 6, T + T_ACR, D - T - T_LINER, FLOOR_Z, HC - 2), "ply"))

    pivots, hinge_lens = [], []
    for k in range(n_lids):
        tp, pv, hl = top_parts(splits[k], splits[k + 1], -OVERHANG, D, lid_index=k,
                               tag=f"_{k}" if n_lids > 1 else "")
        p += tp
        pivots.append(pv)
        hinge_lens.append(hl)

    yi0, yi1 = T + T_ACR, D - T - T_LINER
    lights = []
    for k in range(n_bays):
        a = bays[k] + (inset if k == 0 else 6)
        b = bays[k + 1] - (inset if k == n_bays - 1 else 6)
        lights.append({"x": (a + b) / 2, "y": LED_SPEC["y"], "z": LED_SPEC["z"] - 2,
                       "target": [(a + b) / 2, D * 0.6, FLOOR_Z], "span": b - a})

    clear_h = HC - FLOOR_Z
    storage = (length - 2 * T - (n_bays - 1) * 12 - (0 if end_windows else 2 * T_LINER)) \
        * (D - 2 * T - T_ACR - T_LINER) * clear_h / 1e6
    spec = {
        "length": length, "depth": D + OVERHANG, "height": H,
        "top_length": t1 - t0,
        "windows": [round(w) for w in win_w], "end_windows": round(end_win_w) if end_windows else 0,
        "window_h": round(win_h), "lids": n_lids, "hinge": [round(h) for h in hinge_lens],
        "storage_l": round(storage),
    }
    return p, pivots, lights, spec


def pit_bench():
    return bench(L, n_bays=1, end_windows=False, n_lids=1, seed=7)


def coffee_table():
    """The real table from raw/Arcade Table.step, centred on the origin with its
    floor at Z=0.  Parts are classified by size for display materials."""
    if not TABLE_STEP.exists():
        return coffee_table_standin()
    from build123d import import_step
    asm = import_step(str(TABLE_STEP))
    bb = asm.bounding_box()
    move = Location((-(bb.min.X + bb.max.X) / 2, -(bb.min.Y + bb.max.Y) / 2, -bb.min.Z))
    btn_cols = ["#d62828", "#f4c430", "#2a6fdb", "#2e8b57", "#f2f2f2", "#6a2c91", "#e86a17", "#1f4e9c"]
    parts, nbtn = [], 0
    for i, sl in enumerate(asm.solids()):
        b = sl.bounding_box()
        sx, sy, sz = sorted((b.size.X, b.size.Y))[::-1] + [b.size.Z]
        sh = sl.moved(move)
        if sz > 400:
            parts.append(Part("base", sh, "pine"))
        elif sx > 1500:
            parts.append(Part("top_frame", sh, "black"))
        elif sx > 900 and sz < 30:
            parts.append(Part("tv_43in", sh, "screen"))
        elif 200 < sx < 450 and sz > 60:
            parts.append(Part(f"controller_{i}", sh, "black"))
        elif abs(sx - 34) < 2 and sz > 40:
            parts.append(Part(f"button_{i}", sh, "item", btn_cols[nbtn % len(btn_cols)]))
            nbtn += 1
        elif abs(sx - 35) < 2 and abs(sz - 34) < 2:
            parts.append(Part(f"stick_ball_{i}", sh, "item", "#d62828"))
        elif abs(sx - 65) < 2:
            parts.append(Part(f"stick_base_{i}", sh, "black"))
        else:
            parts.append(Part(f"hw_{i}", sh, "steel"))
    return parts


def coffee_table_standin():
    """Stand-in for the Noisebridge coffee table: black top slab with a 43" TV
    under acrylic in the middle and a flush control panel at each end, on 4x4 legs.
    Centred on the origin, long axis = X."""
    p = []
    hl, hw = TBL_L / 2, TBL_W / 2
    z0 = TBL_H - TBL_TOP_T
    scr_w, scr_h = 1000.0, 585.0          # 43" TV opening
    ctrl_w = (TBL_L - scr_w) / 2 - 140    # control panel width along X
    top = box(-hl, hl, -hw, hw, z0, TBL_H)
    top -= box(-scr_w / 2, scr_w / 2, -scr_h / 2, scr_h / 2, TBL_H - 12, TBL_H + 1)
    for sx in (1, -1):
        cx = sx * (scr_w / 2 + 70 + ctrl_w / 2)
        top -= box(cx - ctrl_w / 2, cx + ctrl_w / 2, -hw + 90, hw - 90, TBL_H - 6, TBL_H + 1)
    p.append(Part("table_top", top, "black"))
    p.append(Part("screen", box(-scr_w / 2 + 20, scr_w / 2 - 20, -scr_h / 2 + 20, scr_h / 2 - 20,
                                TBL_H - 12, TBL_H - 11), "screen"))
    p.append(Part("screen_acrylic", box(-scr_w / 2, scr_w / 2, -scr_h / 2, scr_h / 2,
                                        TBL_H - 6, TBL_H - 1), "glass"))
    # control panels: player at each end faces the screen; joystick left, 8 buttons right
    for sx, tag in ((1, "p1"), (-1, "p2")):
        cx = sx * (scr_w / 2 + 70 + ctrl_w / 2)
        p.append(Part(f"panel_{tag}", box(cx - ctrl_w / 2, cx + ctrl_w / 2, -hw + 90, hw - 90,
                                         TBL_H - 6, TBL_H - 3), "steel"))
        jy = sx * -150
        p.append(Part(f"stick_{tag}", Cylinder(5, 40, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((cx, jy, TBL_H - 3))), "steel"))
        p.append(Part(f"ball_{tag}", Sphere(17).moved(Location((cx, jy, TBL_H + 50))), "item", "#d62828"))
        cols = ["#2a6fdb", "#f4c430", "#2e8b57", "#d62828"]
        for r in range(2):
            for c in range(4):
                bx = cx + sx * (r * 45 - 22)
                by = sx * (10 + c * 42)
                b_ = Cylinder(14, 6, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
                    Location((bx, by, TBL_H - 3)))
                p.append(Part(f"btn_{tag}_{r}{c}", b_, "item", cols[c]))
    # 4x4 legs + 2x4 apron
    leg = 89.0
    for sx in (1, -1):
        for sy in (1, -1):
            x, y = sx * (hl - 120), sy * (hw - 90)
            p.append(Part(f"leg_{sx}_{sy}", box(x - leg / 2, x + leg / 2, y - leg / 2, y + leg / 2, 0, z0),
                          "pine"))
    for sy in (1, -1):
        y = sy * (hw - 90)
        p.append(Part(f"apron_{sy}", box(-hl + 120, hl - 120, y - 19, y + 19, z0 - 89, z0), "pine"))
    return p


# ---------------------------------------------------------------- export
def b64(arr):
    return base64.b64encode(arr.tobytes()).decode()


def mesh_record(part, tol=0.4):
    verts, tris = part.shape.tessellate(tol, 0.25)
    pos = np.array([[v.X, v.Y, v.Z] for v in verts], dtype=np.float32)
    idx = np.array(tris, dtype=np.uint32).reshape(-1)
    rec = {"name": part.name, "mat": part.mat, "pos": b64(pos), "idx": b64(idx)}
    if part.color:
        rec["color"] = part.color
    if part.lid is not None:
        rec["lid"] = part.lid
    return rec


def check(parts, label):
    total = 0.0
    for pt in parts:
        assert pt.shape.is_valid, f"{label}:{pt.name} invalid"
        assert pt.shape.volume > 0, f"{label}:{pt.name} empty"
        total += pt.shape.volume
    bb = Compound([pt.shape for pt in parts]).bounding_box()
    print(f"{label:9s} parts={len(parts):3d}  vol={total/1e6:8.2f} L  "
          f"bbox={bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm")


def labelled(parts, label):
    shapes = []
    for pt in parts:
        sh = pt.shape
        sh.label = pt.name
        shapes.append(sh)
    c = Compound(shapes)
    c.label = label
    return c


def swing_check(parts, pivot, steps=(15, 30, 45, 60, 75, 90, 105, 108)):
    """Rotate the lid group about the hinge axis and make sure it never cuts into
    the fixed parts (beyond a 0.5 cm^3 tolerance for touching knuckle/leaf faces)."""
    lid = [(pt.name, pt.shape) for pt in parts if pt.lid is not None]
    fixed = [(pt.name, pt.shape) for pt in parts if pt.lid is None and pt.mat not in ("led",)
             and not pt.name.startswith("hinge_knuckle") and not pt.name.startswith("stay_body")]
    ax = Axis((0, pivot["y"], pivot["z"]), (1, 0, 0))
    worst = (0.0, 0, "")
    for ang in (0,) + tuple(steps):
        for ln, sh in lid:
            m = sh.rotate(ax, ang * pivot["dir"])
            for fn, f in fixed:
                if not m.bounding_box().overlaps(f.bounding_box()):
                    continue
                v = (m & f).volume
                if v > worst[0]:
                    worst = (v, ang, f"{ln} x {fn}")
    assert worst[0] < 500, f"lid collides at {worst[1]} deg ({worst[2]}): {worst[0]:.0f} mm^3"
    print(f"swing check OK to {steps[-1]} deg (max overlap {worst[0]:.0f} mm^3)")


def ring_locations():
    """Placements as (x, y, rot_deg, side) in pit coordinates (origin = pit centre).
    Bench local Y=0 (display face) always points away from the table."""
    out = []
    for i in range(END_BENCHES):              # player ends: west (rot -90) / east (rot 90)
        b = -YO + i * L
        out.append((-XO, b + L, -90.0, "west"))
        out.append((XO, b, 90.0, "east"))
    for a in (-INNER_L / 2, GAP / 2):         # long sides, either side of the gap
        out.append((a, -YO, 0.0, "south"))
        out.append((a + L, YO, 180.0, "north"))
    return out


def main():
    OUT.mkdir(exist_ok=True)
    for old in ("short_bench.step", "long_end_bench.step", "straight_bench.step", "corner_bench.step"):
        (OUT / old).unlink(missing_ok=True)
    bp, b_piv, b_lights, b_spec = pit_bench()
    swing_check(bp, b_piv[0])
    assert H - LEAF_W > HC, 'hinge leaf deeper than the top board'
    tp = coffee_table()
    basep, powerp = base_parts(L), base_parts(L, power=True)
    check(bp, "bench")
    check(basep, "base")
    check(powerp, "base_pwr")
    check(tp, "table")
    # bench sits on its base: bottom panel on the top plate, pins in the bushings, connector halves meet
    bench_bb = Compound([pt.shape for pt in bp if pt.name == "bottom"]).bounding_box()
    assert abs(bench_bb.min.Z - BASE_H) < 0.01
    for pt in bp:
        if pt.name.startswith("pin_"):
            for bt in basep:
                if bt.name.startswith(("base_top", "base_rail", "base_front", "base_back", "base_conn")):
                    v = (pt.shape & bt.shape).volume
                    assert v < 1, f"{pt.name} hits {bt.name} ({v:.1f} mm^3)"
    print("base fit OK: pins clear the base, connector halves meet at Z =", BASE_H - CONN_DROP)

    b_c, t_c = labelled(bp, "pit_bench"), labelled(tp, "coffee_table")
    base_c, power_c = labelled(basep, "pit_base"), labelled(powerp, "pit_base_power")
    export_step(b_c, str(OUT / "pit_bench.step"))
    export_step(base_c, str(OUT / "pit_base.step"))
    export_step(power_c, str(OUT / "pit_base_power.step"))

    places = ring_locations()
    # the middle bench at each player end gets the power base (one 5 V supply per half of the ring)
    ends = {s: [k for k, pl in enumerate(places) if pl[3] == s] for s in ("west", "east")}
    power_idx = {ends["west"][1], ends["east"][1]}

    # display collections: one themed set per bench, rotated around the pit
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from collection import THEMES, build_contents
    ix0, ix1 = CHASE_X[1] + 2, L - T - T_ACR - 2      # left edge clears the wire chase
    iy0, iy1 = T + T_ACR + 2, D - T - T_LINER - 2
    sets = []
    for ti in range(len(THEMES)):
        nm, raw = build_contents(ti, ix0, ix1, iy0, iy1, FLOOR_Z, seed=5)
        prts = [Part(n, sh, mat, col) for n, sh, mat, col in raw]
        cb = Compound([pt.shape for pt in prts]).bounding_box()
        assert cb.min.X >= ix0 - 3 and cb.max.X <= ix1 + 3 and cb.min.Y >= iy0 - 5 and cb.max.Y <= iy1 + 3 \
            and cb.max.Z < HC - 15, f"theme {nm} pokes out of the bench: {cb}"
        check(prts, nm[:9])
        sets.append((nm, prts))
    benches = [b_c.moved(Location((x, y, 0)) * Rotation(0, 0, r)) for x, y, r, _ in places]
    bases = [(power_c if k in power_idx else base_c).moved(Location((x, y, 0)) * Rotation(0, 0, r))
             for k, (x, y, r, _) in enumerate(places)]
    asm = benches + bases + [t_c]
    for i, a in enumerate(asm):
        a.label = f"{a.label}_{i}"
    # sanity: no two benches overlap
    solids = [Compound([s for s in a.solids()]) for a in benches]
    for i in range(len(solids)):
        for j in range(i + 1, len(solids)):
            bi, bj = solids[i].bounding_box(), solids[j].bounding_box()
            ox = min(bi.max.X, bj.max.X) - max(bi.min.X, bj.min.X)
            oy = min(bi.max.Y, bj.max.Y) - max(bi.min.Y, bj.min.Y)
            assert not (ox > 2.5 and oy > 2.5), f"benches {i} and {j} overlap ({ox:.1f} x {oy:.1f})"
    full = Compound(asm)
    full.label = "arcade_pit"
    export_step(full, str(OUT / "arcade_pit_assembly.step"))

    weight = sum(pt.shape.volume for pt in bp if pt.mat in ("ply", "black")) * 0.68e-6 \
        + sum(pt.shape.volume for pt in bp if pt.mat == "maple") * 0.70e-6 \
        + sum(pt.shape.volume for pt in bp if pt.mat == "acrylic") * 1.19e-6 \
        + sum(pt.shape.volume for pt in bp if pt.mat == "steel") * 8.0e-6
    b_spec["weight_kg"] = round(weight)
    b_spec["base"] = {"h": BASE_H, "setback": BASE_SET, "pin_d": 2 * PIN_R, "pin_l": PIN_L,
                      "weight_kg": round(sum(pt.shape.volume for pt in basep if pt.mat == "base_ply") * 0.68e-6, 1)}
    b_spec["led"] = {k: (round(v, 1) if isinstance(v, float) else [round(x, 1) for x in v]) for k, v in LED_SPEC.items()}
    params = {"D": D, "L": L, "H": H, "OVERHANG": OVERHANG, "GAP": GAP,
              "INNER_L": INNER_L, "INNER_W": INNER_W,
              "OUTER_L": 2 * XO, "OUTER_W": 2 * YO + 2 * OVERHANG, "OUTER_L_TOP": 2 * XO + 2 * OVERHANG,
              "CLEAR_END": CLEAR_END, "CLEAR_SIDE": CLEAR_SIDE, "END_BENCHES": END_BENCHES,
              "table": [TBL_L, TBL_W, TBL_H], "table_estimated": not TABLE_FROM_STEP}
    data = {
        "units": "mm",
        "params": params,
        "placements": [{"variant": "bench", "base": "base_power" if i in power_idx else "base",
                        "pos": [x, y], "rot": r, "side": sd, "contents": i % len(sets),
                        "half": "west" if x < 0 or sd == "west" else "east"}
                       for i, (x, y, r, sd) in enumerate(places)],
        "power": {"conn": [CONN_X, CONN_Y], "fuse": [L / 2 + 110, D / 2], "feeder": [L / 2 + 100, BASE_SET],
                  "strip_len": LED_SPEC["strip_len"], "base_h": BASE_H, "pin_l": PIN_L, "conn_drop": CONN_DROP},
        "contents": [{"name": nm, "parts": [mesh_record(x) for x in prts]} for nm, prts in sets],
        "variants": {
            "bench": {"parts": [mesh_record(x) for x in bp], "pivots": b_piv, "lights": b_lights,
                      "spec": b_spec, "qty": len(places)},
            "base": {"parts": [mesh_record(x) for x in basep]},
            "base_power": {"parts": [mesh_record(x) for x in powerp]},
            "table": {"parts": [mesh_record(x) for x in tp]},
        },
    }
    (OUT / "pit_meshes.json").write_text(json.dumps(data))
    print("bench spec:", b_spec)
    print({k: round(v) if isinstance(v, float) else v for k, v in params.items()})
    print("wrote", *sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()

"""Display contents for the pit benches: low-poly retro game collection props.

Simple, unbranded shapes that read as the real things at display scale:
cartridges (8-bit / 16-bit / 64-bit / handheld), disc cases and discs,
consoles with controllers, and toys (block, mushroom, pixel critters, ghosts,
coins, a mini arcade cabinet).

Every builder returns a list of (name, shape, material, colour) tuples in
bench-local coordinates (mm): X along the bench, Y = 0 at the display window,
Z = 0 on the floor of the room.  Items sit on the display floor at z0.
"""
from __future__ import annotations

import random

from build123d import Align, Box, Cylinder, Location, Rotation, Sphere

MIN = (Align.MIN, Align.MIN, Align.MIN)
CTR_BASE = (Align.CENTER, Align.CENTER, Align.MIN)

LABELS = ["#c0392b", "#1f4e9c", "#2e8b57", "#d4a017", "#6a2c91", "#e86a17",
          "#b03a6f", "#3a7bd5", "#0f6b6b", "#8b0000", "#f2f2f2", "#2a2a2a"]


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=MIN).moved(Location((x0, y0, z0)))


def cyl(r, h, x, y, z, rot=(0, 0, 0)):
    return Cylinder(r, h, rotation=rot, align=CTR_BASE).moved(Location((x, y, z)))


class Kit:
    """Collects props for one bench."""

    def __init__(self, z0, seed):
        self.z0, self.rng, self.items, self.n = z0, random.Random(seed), [], 0

    def add(self, name, shape, colour, mat="item"):
        self.n += 1
        self.items.append((f"{name}_{self.n}", shape, mat, colour))

    def label(self):
        return self.rng.choice(LABELS)

    # ---------------------------------------------------------- media
    def cart_face_out(self, kind, x, y, z=None):
        """Cartridge standing upright, label facing the window (-Y)."""
        z = self.z0 if z is None else z
        w, t, h, body, lw, lh = {
            "8bit": (120, 20, 133, "#8e8e8e", 100, 72),
            "16bit": (135, 20, 92, "#b9b9b9", 104, 52),
            "64bit": (116, 18, 76, "#6b6b6e", 92, 46),
            "hand": (57, 8, 65, "#a3a3a3", 46, 36),
        }[kind]
        self.add(f"cart_{kind}", box(x, x + w, y, y + t, z, z + h), body)
        self.add(f"cart_{kind}_label", box(x + (w - lw) / 2, x + (w + lw) / 2, y - 0.8, y,
                                           z + h - lh - (h - lh) * 0.35, z + h - (h - lh) * 0.35), self.label())
        if kind == "8bit":  # grip ridges at the bottom
            for i in range(4):
                self.add("cart_ridge", box(x + 12, x + w - 12, y - 1.5, y, z + 6 + i * 6, z + 9 + i * 6), "#7a7a7a")
        return w

    def spine_row(self, kind, x, y, n):
        """Disc cases standing spine-out (spine faces the window)."""
        t, d, h, colours = {
            "dvd": (14, 135, 190, ["#111114", "#111114", "#1c3f94", "#111114"]),
            "jewel": (10, 125, 142, ["#141414"]),
        }[kind]
        for i in range(n):
            xi = x + i * (t + 1)
            hi = h - (self.rng.choice([0, 0, 0, 8]) if kind == "dvd" else 0)
            self.add(f"case_{kind}", box(xi, xi + t, y, y + d, self.z0, self.z0 + hi), self.rng.choice(colours))
            self.add(f"case_{kind}_spine", box(xi + 1.5, xi + t - 1.5, y - 0.8, y,
                                               self.z0 + hi - 55, self.z0 + hi - 12), self.label())
        return n * (t + 1)

    def jewel_face_out(self, x, y, z=None, tilt=False):
        z = self.z0 if z is None else z
        self.add("jewel_case", box(x, x + 142, y, y + 10, z, z + 125), "#151515")
        self.add("jewel_art", box(x + 8, x + 134, y - 0.8, y, z + 4, z + 121), self.label())
        return 142

    def jewel_stack(self, x, y, n):
        for i in range(n):
            z = self.z0 + i * 10.5
            self.add("jewel_flat", box(x, x + 142, y, y + 125, z, z + 10), "#151515")
            self.add("jewel_flat_art", box(x + 6, x + 136, y + 4, y + 121, z + 10, z + 10.5), self.label())

    def disc_on_stand(self, x, y):
        self.add("disc_stand", box(x - 30, x + 30, y - 10, y + 25, self.z0, self.z0 + 12), "#202024")
        zc = self.z0 + 12 + 60
        self.add("disc", cyl(60, 1.2, x, y + 6, zc, rot=(90, 0, 0)).moved(Location((0, 0, -0.0))),
                 "#c9ccd2", mat="steel")
        self.add("disc_print", cyl(57, 0.6, x, y + 5.4, zc, rot=(90, 0, 0)), self.label())
        self.add("disc_hub", cyl(18, 0.8, x, y + 4.8, zc, rot=(90, 0, 0)), "#d9dbe0", mat="steel")

    # ---------------------------------------------------------- consoles
    def console_8bit(self, x, y):
        z = self.z0
        self.add("con8_body", box(x, x + 256, y, y + 203, z, z + 85), "#c8c8c6")
        self.add("con8_band", box(x, x + 256, y - 0.8, y, z + 8, z + 34), "#2b2b2b")
        self.add("con8_lid", box(x + 30, x + 200, y + 8, y + 120, z + 85, z + 89), "#8d8d8b")
        for i, c in enumerate(["#c9302c", "#6f6f6f"]):
            self.add("con8_btn", box(x + 20 + i * 40, x + 50 + i * 40, y - 3, y, z + 46, z + 58), c)
        self.add("con8_port", box(x + 150, x + 240, y - 1.2, y, z + 14, z + 28), "#555555")

    def console_16bit(self, x, y):
        z = self.z0
        self.add("con16_body", box(x, x + 200, y, y + 242, z, z + 62), "#d3d2cf")
        self.add("con16_hump", box(x + 25, x + 175, y + 70, y + 210, z + 62, z + 78), "#c4c3c0")
        self.add("con16_slot", box(x + 45, x + 155, y + 125, y + 150, z + 78, z + 79), "#3a3a3a")
        for i in range(2):
            self.add("con16_slider", box(x + 30 + i * 105, x + 65 + i * 105, y + 30, y + 52, z + 62, z + 70), "#6b56a8")

    def console_64bit(self, x, y):
        z = self.z0
        self.add("con64_body", box(x, x + 260, y, y + 190, z, z + 55), "#3a3a3e")
        self.add("con64_hump", box(x + 45, x + 215, y + 70, y + 180, z + 55, z + 78), "#36363a")
        self.add("con64_cart", box(x + 72, x + 188, y + 115, y + 133, z + 78, z + 125), "#6b6b6e")
        self.add("con64_cart_label", box(x + 84, x + 176, y + 114.2, y + 115, z + 85, z + 120), self.label())
        for i, c in enumerate(["#4a4a4e", "#4a4a4e"]):
            self.add("con64_switch", box(x + 60 + i * 110, x + 90 + i * 110, y + 25, y + 45, z + 55, z + 60), c)
        for i in range(4):
            self.add("con64_port", box(x + 30 + i * 55, x + 55 + i * 55, y - 1.0, y, z + 15, z + 30), "#1b1b1d")

    def console_disc(self, x, y):
        """32-bit disc console: light grey, round lid."""
        z = self.z0
        self.add("conps_body", box(x, x + 270, y, y + 188, z, z + 55), "#c9c9cd")
        self.add("conps_lid", cyl(68, 5, x + 175, y + 100, z + 55), "#bdbdc2")
        for i, c in enumerate(["#6f6f75", "#6f6f75", "#3b6fd4"]):
            self.add("conps_btn", cyl(9, 4, x + 40 + i * 32, y + 45, z + 55), c)
        self.add("conps_port", box(x + 30, x + 120, y - 1.0, y, z + 12, z + 28), "#2c2c30")

    def console_tower(self, x, y):
        """Black slim-line disc console lying flat, blue status light."""
        z = self.z0
        self.add("conp2_body", box(x, x + 301, y, y + 178, z, z + 78), "#141417")
        for i in range(6):
            self.add("conp2_groove", box(x, x + 301, y - 0.8, y, z + 10 + i * 11, z + 13 + i * 11), "#24242a")
        self.add("conp2_tray", box(x + 20, x + 210, y - 1.2, y, z + 52, z + 62), "#1c1c22")
        self.add("conp2_led", box(x + 270, x + 285, y - 1.6, y, z + 55, z + 60), "#3a7bff", mat="led_blue")

    def handheld(self, x, y, colour="#b9b8b0"):
        """Brick handheld propped upright facing the window."""
        z = self.z0
        self.add("hh_body", box(x, x + 90, y, y + 32, z, z + 148), colour)
        self.add("hh_bezel", box(x + 8, x + 82, y - 0.8, y, z + 76, z + 140), "#4a4a63")
        self.add("hh_screen", box(x + 20, x + 70, y - 1.4, y, z + 86, z + 132), "#8bac0f", mat="glow_green")
        self.add("hh_dpad_h", box(x + 10, x + 34, y - 3, y, z + 46, z + 54), "#222222")
        self.add("hh_dpad_v", box(x + 18, x + 26, y - 3, y, z + 38, z + 62), "#222222")
        for i in range(2):
            self.add("hh_btn", cyl(6, 3, x + 62 + i * 14, y, z + 44 + i * 8, rot=(90, 0, 0)), "#9b2257")

    # ---------------------------------------------------------- controllers
    def pad_rect(self, x, y):
        z = self.z0
        self.add("pad8", box(x, x + 120, y, y + 53, z, z + 14), "#c8c8c6")
        self.add("pad8_face", box(x + 6, x + 114, y + 6, y + 47, z + 14, z + 15), "#2a2a2a")
        self.add("pad8_dpad", box(x + 14, x + 40, y + 22, y + 30, z + 15, z + 18), "#111111")
        self.add("pad8_dpad2", box(x + 23, x + 31, y + 13, y + 39, z + 15, z + 18), "#111111")
        for i in range(2):
            self.add("pad8_btn", cyl(6, 3, x + 88 + i * 16, y + 26, z + 15), "#c9302c")

    def pad_round(self, x, y, colour="#cfcfd3", buttons=("#3b6fd4", "#d62828", "#2e8b57", "#e6c32a")):
        z = self.z0
        self.add("padr_mid", box(x + 30, x + 120, y, y + 50, z, z + 20), colour)
        for dx in (30, 120):
            self.add("padr_grip", cyl(26, 20, x + dx, y + 30, z), colour)
        for i, c in enumerate(buttons):
            ox, oy = [(0, 10), (10, 0), (0, -10), (-10, 0)][i]
            self.add("padr_btn", cyl(5, 3, x + 120 + ox, y + 25 + oy, z + 20), c)

    def pad_trident(self, x, y):
        z = self.z0
        self.add("pad64_mid", box(x + 40, x + 120, y + 20, y + 70, z, z + 22), "#5b5b60")
        for dx in (0, 70, 140):
            self.add("pad64_prong", box(x + dx + 10, x + dx + 40, y, y + 30, z, z + 22), "#5b5b60")
        self.add("pad64_stick", cyl(7, 18, x + 80, y + 40, z + 22), "#9a9aa0")
        for i, c in enumerate(["#2a6fdb", "#2e8b57", "#e6c32a", "#e6c32a"]):
            self.add("pad64_btn", cyl(5, 3, x + 140 + (i % 2) * 14, y + 30 + (i // 2) * 14, z + 22), c)

    # ---------------------------------------------------------- toys
    def q_block(self, x, y, s=90, z=None):
        z = self.z0 if z is None else z
        self.add("block", box(x, x + s, y, y + s, z, z + s), "#f2a20c")
        for dx, dz in ((8, 8), (s - 16, 8), (8, s - 16), (s - 16, s - 16)):
            self.add("block_rivet", box(x + dx, x + dx + 8, y - 1.2, y, z + dz, z + dz + 8), "#7a4a06")
        # a simple bold mark on the face
        self.add("block_mark", box(x + s * 0.42, x + s * 0.58, y - 1.2, y, z + s * 0.22, z + s * 0.36), "#fff3c4")
        self.add("block_mark", box(x + s * 0.42, x + s * 0.58, y - 1.2, y, z + s * 0.44, z + s * 0.78), "#fff3c4")

    def mushroom(self, x, y, cap="#d62828"):
        z = self.z0
        self.add("shroom_stem", cyl(26, 50, x, y, z), "#f1e2c4")
        cap_shape = Sphere(52).moved(Location((x, y, z + 50))) & box(x - 60, x + 60, y - 60, y + 60, z + 50, z + 120)
        self.add("shroom_cap", cap_shape, cap)
        for ang in (0, 120, 240):
            import math
            a = math.radians(ang + 30)
            self.add("shroom_spot", Sphere(11).moved(Location((x + 40 * math.cos(a), y + 40 * math.sin(a), z + 78))),
                     "#fbfbf6")
        self.add("shroom_spot", Sphere(12).moved(Location((x, y, z + 101))), "#fbfbf6")
        for dx in (-9, 9):
            self.add("shroom_eye", box(x + dx - 3, x + dx + 3, y - 27, y - 22, z + 22, z + 38), "#1a1a1a")

    def pixel_critter(self, x, y, colour, px=11, seed=0):
        """Original symmetric pixel creature (random 5x7 half, mirrored), standing upright."""
        r = random.Random(seed)
        half = [[r.random() < 0.55 for _ in range(4)] + [r.random() < 0.8] for _ in range(7)]
        half[2][1] = False  # eye
        z = self.z0 + 6
        self.add("critter_base", box(x - 5, x + 9 * px + 5, y - 5, y + 25, self.z0, self.z0 + 6), "#202024")
        for row in range(7):
            cols = half[row][:4] + [half[row][4]] + half[row][:4][::-1]
            for c, on in enumerate(cols):
                if on:
                    zz = z + (6 - row) * px
                    self.add("critter_px", box(x + c * px, x + (c + 1) * px, y, y + px, zz, zz + px), colour)

    def ghost(self, x, y, colour):
        z = self.z0
        self.add("ghost_body", cyl(42, 55, x, y, z), colour)
        self.add("ghost_head", Sphere(42).moved(Location((x, y, z + 55))) & box(x - 50, x + 50, y - 50, y + 50, z + 55, z + 110), colour)
        for dx in (-15, 15):
            self.add("ghost_eye", Sphere(11).moved(Location((x + dx, y - 33, z + 62))), "#ffffff")
            self.add("ghost_pupil", Sphere(5.5).moved(Location((x + dx, y - 42, z + 60))), "#1f4e9c")

    def coins(self, x, y, n=5):
        for i in range(n):
            self.add("coin", cyl(22, 4.5, x + self.rng.uniform(-2, 2), y + self.rng.uniform(-2, 2),
                                 self.z0 + i * 4.6), "#f4c430", mat="gold")
        self.add("coin_up", cyl(22, 4.5, x + 55, y + 4, self.z0 + 22, rot=(90, 0, 0)), "#f4c430", mat="gold")

    def pixel_heart(self, x, y, px=10):
        rows = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]
        self.add("heart_base", box(x - 4, x + 7 * px + 4, y - 4, y + 20, self.z0, self.z0 + 6), "#202024")
        for r_, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch == "1":
                    zz = self.z0 + 6 + (len(rows) - 1 - r_) * px
                    self.add("heart_px", box(x + c * px, x + (c + 1) * px, y, y + px, zz, zz + px), "#e0263b")

    def mini_cabinet(self, x, y):
        z = self.z0
        self.add("mini_cab", box(x, x + 70, y, y + 60, z, z + 150), "#1d1d22")
        self.add("mini_cab_side", box(x - 1, x, y, y + 60, z + 10, z + 140), "#e63946")
        self.add("mini_cab_side", box(x + 70, x + 71, y, y + 60, z + 10, z + 140), "#e63946")
        self.add("mini_cab_marquee", box(x + 6, x + 64, y - 1, y, z + 128, z + 144), "#ffd166", mat="glow_warm")
        self.add("mini_cab_screen", box(x + 10, x + 60, y - 1, y, z + 80, z + 120), "#4cc9f0", mat="glow_blue")
        self.add("mini_cab_panel", box(x + 4, x + 66, y - 14, y, z + 62, z + 72), "#2b2b33")
        self.add("mini_cab_ball", Sphere(4).moved(Location((x + 20, y - 7, z + 78))), "#d62828")


def riser(kit, x0, x1, y0, y1, h):
    kit.add("riser", box(x0, x1, y0, y1, kit.z0, kit.z0 + h), "#1a1a1d")
    return kit.z0 + h


# ---------------------------------------------------------------- themes
# Interior usable span is roughly x in [24, L-24], y in [24, D-24].

def theme_8bit(k, x0, x1, y0, y1):
    k.console_8bit(x0 + 10, y1 - 215)
    k.pad_rect(x0 + 40, y0 + 95)
    zr = riser(k, x0 + 290, x0 + 690, y1 - 120, y1 - 20, 70)
    for i in range(3):
        k.cart_face_out("8bit", x0 + 295 + i * 130, y1 - 100, zr)
    for i in range(3):
        k.cart_face_out("8bit", x0 + 360 + i * 125 - 60, y0 + 160)
    k.q_block(x1 - 110, y0 + 20)
    k.mushroom(x1 - 60, y1 - 90)
    k.coins(x0 + 130, y0 + 40)


def theme_16bit(k, x0, x1, y0, y1):
    k.console_16bit(x0 + 10, y1 - 250)
    k.handheld(x0 + 30, y0 + 40)
    k.pad_round(x0 + 230, y0 + 30, colour="#cfcfd3", buttons=("#6b56a8", "#8a78c4", "#6b56a8", "#8a78c4"))
    zr = riser(k, x0 + 240, x0 + 680, y1 - 110, y1 - 20, 60)
    for i in range(3):
        k.cart_face_out("16bit", x0 + 245 + i * 145, y1 - 95, zr)
    for i in range(3):
        k.cart_face_out("hand", x0 + 430 + i * 66, y0 + 120)
    k.pixel_critter(x1 - 115, y0 + 40, "#3ad13a", seed=3)
    k.pixel_heart(x1 - 100, y1 - 70)


def theme_64bit(k, x0, x1, y0, y1):
    k.console_64bit(x0 + 260, y1 - 200)
    for i in range(5):
        k.cart_face_out("64bit", x0 + 30 + i * 125, y0 + 150)
    k.pad_trident(x0 + 20, y1 - 140)
    k.ghost(x1 - 70, y0 + 80, "#ff5fa2")
    k.ghost(x1 - 70, y1 - 90, "#38c7f2")
    k.q_block(x0 + 670, y1 - 80, s=70)


def theme_disc(k, x0, x1, y0, y1):
    k.console_disc(x0 + 300, y1 - 200)
    k.pad_round(x0 + 340, y0 + 150, colour="#bdbdc4")
    k.jewel_stack(x0 + 20, y1 - 150, 5)
    for i in range(2):
        k.jewel_face_out(x0 + 15 + i * 150, y0 + 60)
    k.disc_on_stand(x0 + 400, y0 + 70)
    k.mini_cabinet(x1 - 100, y0 + 60)
    k.pixel_critter(x1 - 120, y1 - 70, "#ff8c1a", seed=11)


def theme_tower(k, x0, x1, y0, y1):
    k.console_tower(x0 + 280, y1 - 190)
    k.pad_round(x0 + 300, y0 + 70, colour="#1b1b1f")
    k.spine_row("dvd", x0 + 15, y0 + 30, 16)
    k.disc_on_stand(x0 + 520, y0 + 60)
    k.ghost(x1 - 70, y0 + 80, "#ff3b3b")
    k.mushroom(x1 - 75, y1 - 90, cap="#2e8b57")


THEMES = [("8-bit", theme_8bit), ("16-bit & handheld", theme_16bit), ("64-bit", theme_64bit),
          ("32-bit discs", theme_disc), ("disc tower", theme_tower)]


def build_contents(theme_index, x0, x1, y0, y1, z0, seed=0):
    k = Kit(z0, seed + theme_index * 101)
    THEMES[theme_index][1](k, x0, x1, y0, y1)
    return THEMES[theme_index][0], k.items

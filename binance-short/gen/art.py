"""Character, environment and prop art."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import core as C

_img = {}


def binance_mark(size, color, hole=True):
    key = ("bm", int(size), color, hole)
    if key in _img:
        return _img[key]
    s = int(size)
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = max(2, int(s * 0.05))
    u = (s - 2 * pad) / 3
    c = s / 2

    def dm(cx, cy, r):
        d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=color)

    dm(c, c, u * 0.52)
    if hole:
        d.polygon(
            [(c, c - u * 0.2), (c + u * 0.2, c), (c, c + u * 0.2), (c - u * 0.2, c)],
            fill=(8, 10, 18, 255),
        )
    dm(c, c - u, u * 0.5)
    dm(c, c + u, u * 0.5)
    dm(c - u, c, u * 0.5)
    dm(c + u, c, u * 0.5)
    _img[key] = img
    return img


def coin_sprite(r):
    key = ("coin", int(r))
    if key in _img:
        return _img[key]
    r = int(r)
    s = r * 2 + 8
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 4, s - 4, s - 4), fill=(196, 148, 10, 255),
              outline=(255, 214, 80, 255), width=max(2, int(r * 0.14)))
    d.ellipse((4 + r * 0.22, 4 + r * 0.22, s - 4 - r * 0.22, s - 4 - r * 0.22),
              outline=(255, 224, 96, 200), width=2)
    mk = binance_mark(max(6, int(r * 0.9)), (255, 224, 96, 255), hole=False)
    img.alpha_composite(mk, (int(s / 2 - mk.width / 2), int(s / 2 - mk.height / 2)))
    d.arc((4, 4, s - 4, s - 4), 200, 250, fill=(255, 255, 255, 160), width=max(2, int(r * 0.1)))
    _img[key] = img
    return img


def hacker_sprite(scale=1.0):
    """Faceless hooded figure seen from behind (460x640 design box)."""
    key = ("hk", round(scale, 3))
    if key in _img:
        return _img[key]
    bw, bh = 460, 640
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = bw // 2
    body = (13, 15, 24, 255)
    d.polygon([(cx - 150, bh), (cx - 125, 380), (cx - 80, 330),
               (cx + 80, 330), (cx + 125, 380), (cx + 150, bh)], fill=body)
    d.ellipse((cx - 135, 300, cx + 135, 420), fill=body)
    d.ellipse((cx - 100, 40, cx + 100, 260), fill=body)
    d.ellipse((cx - 64, 100, cx + 64, 250), fill=(3, 4, 8, 255))
    d.polygon([(cx - 125, 380), (cx - 175, 520), (cx - 125, 570), (cx - 85, 430)], fill=body)
    d.polygon([(cx + 125, 380), (cx + 175, 520), (cx + 125, 570), (cx + 85, 430)], fill=body)
    d.arc((cx - 100, 40, cx + 100, 260), 150, 250, fill=(86, 226, 214, 220), width=4)
    d.arc((cx - 100, 40, cx + 100, 260), 300, 395, fill=(255, 64, 52, 190), width=3)
    d.line([(cx - 125, 380), (cx - 175, 520)], fill=(86, 226, 214, 200), width=3)
    d.line([(cx + 125, 380), (cx + 175, 520)], fill=(255, 64, 52, 170), width=3)
    d.arc((cx - 135, 300, cx + 135, 420), 190, 260, fill=(86, 226, 214, 160), width=3)
    d.arc((cx - 135, 300, cx + 135, 420), 285, 350, fill=(255, 64, 52, 140), width=3)
    if scale != 1.0:
        img = img.resize((int(bw * scale), int(bh * scale)), Image.Resampling.LANCZOS)
    _img[key] = img
    return img


def hand_sprite(scale=1.0):
    key = ("hand", round(scale, 3))
    if key in _img:
        return _img[key]
    s = max(8, int(70 * scale))
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((6, 10, s - 6, s - 4), fill=(13, 15, 24, 255))
    d.arc((6, 10, s - 6, s - 4), 200, 340, fill=(70, 80, 100, 200), width=3)
    _img[key] = img
    return img


_gp = None


def _globe_pts():
    global _gp
    if _gp is None:
        rng = np.random.default_rng(4)
        v = rng.normal(size=(30, 3))
        v /= np.linalg.norm(v, axis=1, keepdims=True)
        _gp = v
    return _gp


def globe(img, t, cx, cy, r, accent=C.RED, spin=0.22, tilt=0.22):
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(120, 150, 195, 150), width=2)
    ct, st = math.cos(tilt), math.sin(tilt)
    for k in range(6):
        m = spin * t + k * math.pi / 6
        rw = abs(math.cos(m)) * r
        if rw > r * 0.05:
            d.ellipse((cx - rw, cy - r, cx + rw, cy + r), outline=(96, 124, 168, 110), width=2)
    for la in (-0.5, -0.25, 0.0, 0.25, 0.5):
        rc = math.cos(la) * r
        ycen = cy - math.sin(la) * r * ct * 0.9
        eh = max(2.0, rc * st * 0.35)
        d.ellipse((cx - rc, ycen - eh, cx + rc, ycen + eh), outline=(96, 124, 168, 90), width=2)
    for v in _globe_pts():
        x, y, z = v
        x2 = x * math.cos(spin * t) + z * math.sin(spin * t)
        z2 = -x * math.sin(spin * t) + z * math.cos(spin * t)
        y2 = y * ct - z2 * st
        zz = y * st + z2 * ct
        if zz > 0.05:
            sx, sy = cx + r * x2, cy - r * y2
            d.ellipse((sx - 2.5, sy - 2.5, sx + 2.5, sy + 2.5), fill=(140, 220, 230, int(90 + 140 * zz)))
    ex, ey = cx - r * 0.58, cy + r * 0.30
    dx_, dy_ = cx + r * 0.52, cy - r * 0.34
    mx, my = (ex + dx_) / 2, (ey + dy_) / 2 - r * 0.75
    pts = []
    for i in range(25):
        u = i / 24
        bx = (1 - u) ** 2 * ex + 2 * (1 - u) * u * mx + u * u * dx_
        by = (1 - u) ** 2 * ey + 2 * (1 - u) * u * my + u * u * dy_
        pts.append((bx, by))
    d.line(pts, fill=(*accent, 170), width=3)
    u = (t * 0.45) % 1
    sx = (1 - u) ** 2 * ex + 2 * (1 - u) * u * mx + u * u * dx_
    sy = (1 - u) ** 2 * ey + 2 * (1 - u) * u * my + u * u * dy_
    d.ellipse((sx - 4, sy - 4, sx + 4, sy + 4), fill=(255, 224, 96, 230))
    phase = (t * 0.8) % 1.0
    rr_ = r * 0.06 + phase * r * 0.13
    d.ellipse((dx_ - rr_, dy_ - rr_, dx_ + rr_, dy_ + rr_), outline=(*accent, int(180 * (1 - phase))), width=3)
    d.ellipse((dx_ - 5, dy_ - 5, dx_ + 5, dy_ + 5), fill=(*accent, 255))
    d.ellipse((ex - 4, ey - 4, ex + 4, ey + 4), fill=(*C.GOLD, 255))


class Room:
    """Wide server-room environment with the hacker at his desk."""

    def __init__(self):
        self.S = 1.12
        self.W2, self.H2 = int(C.W * self.S), int(C.H * self.S)
        self.base = self._build_base()
        self.leds = self._build_leds()
        self.beams = self._build_beams()
        self.dust = C.Dust(n=46, seed=11, box=(40, 140, self.W2 - 40, 1700))
        self.hk = hacker_sprite(0.78)
        self.hand = hand_sprite(0.85)
        self.code = self._build_code(640, 1200)

    def _build_base(self):
        W2, H2 = self.W2, self.H2
        img = C.vgrad(W2, H2, [(0, (6, 8, 16)), (0.42, (13, 17, 32)),
                               (0.72, (10, 13, 24)), (1, (5, 6, 12))]).convert("RGBA")
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle((0.07 * W2, 0.15 * H2, 0.93 * W2, 0.80 * H2), radius=24,
                            fill=(16, 21, 36, 255), outline=(38, 46, 66, 255), width=2)
        d.rounded_rectangle((0.14 * W2, 0.245 * H2, 0.86 * W2, 0.53 * H2), radius=18,
                            fill=(6, 8, 14, 255), outline=(46, 60, 86, 255), width=3)
        for bx, by, ex_, ey_ in ((0.14 * W2, 0.245 * H2, 1, 1), (0.86 * W2, 0.245 * H2, -1, 1),
                                 (0.14 * W2, 0.53 * H2, 1, -1), (0.86 * W2, 0.53 * H2, -1, -1)):
            d.line((bx, by, bx + 26 * ex_, by), fill=(*C.CYAN, 190), width=4)
            d.line((bx, by, bx, by + 26 * ey_), fill=(*C.CYAN, 190), width=4)
        for x in (0.07 * W2, 0.93 * W2):
            d.line((x, 0.05 * H2, x, 0.43 * H2), fill=(20, 26, 40, 255), width=10)
        for x0, x1 in ((0.02, 0.12), (0.88, 0.98)):
            rx0, rx1 = int(x0 * W2), int(x1 * W2)
            ry0, ry1 = int(0.42 * H2), int(0.755 * H2)
            d.rounded_rectangle((rx0, ry0, rx1, ry1), radius=10,
                                fill=(13, 17, 30, 255), outline=(40, 50, 72, 255), width=2)
            for yy in range(ry0 + 18, ry1 - 10, 36):
                d.line((rx0 + 8, yy, rx1 - 8, yy), fill=(24, 31, 52, 255), width=10)
        fy = int(0.74 * H2)
        d.rectangle((0, fy, W2, H2), fill=(10, 12, 20, 255))
        vx, vy = W2 / 2, fy - 30
        for i in range(-8, 9):
            xb = W2 / 2 + i * 0.16 * W2
            tmax = (H2 - fy) / (H2 - vy)
            xe = xb + tmax * (vx - xb)
            ye = H2 + tmax * (vy - H2)
            d.line((xb, H2, xe, ye), fill=(40, 52, 76, 90), width=3)
        for gy in (0.78, 0.83, 0.89, 0.955):
            d.line((0, gy * H2, W2, gy * H2), fill=(40, 52, 76, 70), width=2)
        d.rounded_rectangle((0.28 * W2, 0.765 * H2, 0.72 * W2, 0.806 * H2), radius=14, fill=(24, 30, 48, 255))
        d.line((0.28 * W2, 0.765 * H2, 0.72 * W2, 0.765 * H2), fill=(90, 110, 140, 255), width=3)
        d.rounded_rectangle((W2 / 2 - 190, 0.775 * H2, W2 / 2 + 190, 0.792 * H2), radius=10,
                            fill=(12, 15, 26, 255), outline=(60, 74, 100, 255), width=2)
        for mx0, my0, mx1, my1 in ((0.235, 0.605, 0.385, 0.763), (0.40, 0.585, 0.60, 0.763),
                                   (0.615, 0.605, 0.765, 0.763)):
            x0, y0, x1, y1 = mx0 * W2, my0 * H2, mx1 * W2, my1 * H2
            d.rounded_rectangle((x0, y0, x1, y1), radius=12,
                                fill=(10, 12, 20, 255), outline=(46, 58, 84, 255), width=3)
            for yy in range(int(y0) + 26, int(y1) - 18, 24):
                d.line((x0 + 16, yy, x1 - 16, yy), fill=(22, 28, 46, 255), width=5)
            d.rectangle(((x0 + x1) / 2 - 24, y1, (x0 + x1) / 2 + 24, 0.765 * H2), fill=(16, 20, 34, 255))
        return img

    def _build_leds(self):
        rng = np.random.default_rng(3)
        leds = []
        for x0, x1 in ((0.02, 0.12), (0.88, 0.98)):
            for row in range(16):
                y = 0.44 * self.H2 + row * (0.30 * self.H2 / 16)
                for k in range(4):
                    x = x0 * self.W2 + 12 + k * (x1 - x0) * self.W2 / 4.6
                    col = rng.choice([(255, 80, 64), (86, 226, 214), (52, 199, 164), (240, 185, 11)],
                                     p=[0.25, 0.4, 0.25, 0.1])
                    leds.append((x, y, tuple(col), rng.uniform(0, 6.28), rng.uniform(0.4, 1.6)))
        return leds

    def _build_beams(self):
        W2, H2 = self.W2, self.H2
        m = Image.new("L", (W2, H2), 0)
        dm = ImageDraw.Draw(m)
        dm.polygon([(0.34 * W2, 0), (0.46 * W2, 0), (0.60 * W2, 0.765 * H2), (0.30 * W2, 0.765 * H2)], fill=70)
        dm.polygon([(0.56 * W2, 0), (0.68 * W2, 0), (0.74 * W2, 0.765 * H2), (0.46 * W2, 0.765 * H2)], fill=46)
        m = m.filter(ImageFilter.GaussianBlur(26))
        col = Image.new("RGBA", (W2, H2), (150, 190, 230, 0))
        col.putalpha(m)
        return col

    def _build_code(self, w, h):
        rng = np.random.default_rng(9)
        img = Image.new("RGB", (w, h), (6, 10, 16))
        d = ImageDraw.Draw(img)
        f = C.F_MONO(18)
        cols = [(86, 226, 214), (52, 199, 164), (120, 140, 170)]
        toks = ["0x3f9a", "MOV", "xor", "call", "%rbx", "0x00", "get", "http", "::",
                "auth", "->", "key", "0xff21", "sig", "tx", "blk"]
        for y in range(0, h, 26):
            x = 8
            while x < w - 30:
                tok = toks[rng.integers(0, len(toks))]
                c = cols[rng.integers(0, 3)]
                d.text((x, y), tok, font=f, fill=c)
                x += int(len(tok) * 11.5) + 18
        return img

    def _wallscreen(self, img, d, t):
        W2, H2 = self.W2, self.H2
        sx0, sy0 = int(0.14 * W2), int(0.245 * H2)
        sx1, sy1 = int(0.86 * W2), int(0.53 * H2)
        sw, sh = sx1 - sx0, sy1 - sy0
        row = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        C.blit(row, C.soft_dot(150, C.CYAN), sw * 0.31, sh * 0.52, alpha=0.14)
        globe(row, t, sw * 0.31, sh * 0.50, 150)
        f = C.fit(C.F_DISPLAY, "$6,300,000,000", 340, 64)
        C.blit(row, C.text_sprite("$6,300,000,000", f, (*C.GOLD_HI, 255),
                                  glow=(12, C.GOLD, 0.8)), sw * 0.70, sh * 0.33)
        fc = C.F_COND(56)
        C.blit(row, C.text_sprite("DRAINED", fc, (*C.RED, 255),
                                  glow=(10, C.RED, 0.7)), sw * 0.70, sh * 0.47)
        fm = C.F_MONO(22)
        C.blit(row, C.text_sprite("LIVE LEDGER - WITHDRAWAL FLOW", fm, (*C.CYAN, 200)), sw * 0.70, sh * 0.16)
        if C.pulse(t, 1.6) > 0.5:
            d.ellipse((sx1 - 46, sy0 + 22, sx1 - 30, sy0 + 38), fill=(*C.RED, 230))
            C.blit(row, C.text_sprite("REC", C.F_MONO(20), (*C.GREY, 220)), sx1 - sx0 - 62, 30)
        tk = C.text_sprite("$6.3B STOLEN   -   FBI: TRADERTRAITOR   -   DPRK DENIES   -   40% FROZEN   -   ",
                           C.F_COND(34), (*C.GREY, 210), tracking=2)
        tw = tk.width
        pos = -int((t * 140) % tw)
        for k in range(int(sw / tw) + 2):
            row.paste(tk, (pos + k * tw, sh - 64), tk)
        img.paste(row, (sx0, sy0), row)

    def frame(self, t, zoom=1.0, cy=None, alert=0.0):
        W2, H2 = self.W2, self.H2
        img = self.base.copy()
        d = ImageDraw.Draw(img, "RGBA")
        for x, y, col, ph, sp in self.leds:
            a = int(120 + 120 * math.sin(2 * math.pi * sp * t + ph))
            a = max(0, min(255, a))
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(*col, a))
        self._wallscreen(img, d, t)
        fa = 0.75 + 0.25 * C.pulse(t, 0.35)
        b = self.beams.copy()
        b.putalpha(b.getchannel("A").point(lambda v: int(v * fa)))
        img.alpha_composite(b)
        for mx0, mx1, my in ((0.235, 0.385, 0.605), (0.40, 0.60, 0.585), (0.615, 0.765, 0.605)):
            x0, x1 = mx0 * W2 + 14, mx1 * W2 - 14
            y = my * H2 + 5
            a = int(90 + 90 * C.pulse(t, 6.0 + x0 % 3))
            d.line((x0, y, x1, y), fill=(*C.CYAN, a), width=3)
        C.blit(img, C.soft_dot(150, C.CYAN), W2 / 2, 0.80 * H2, alpha=0.15)
        bob = int(math.sin(t * 1.4) * 4)
        img.alpha_composite(self.hk, (int(W2 / 2 - self.hk.width / 2), int(0.765 * H2 - self.hk.height + bob)))
        wgl = 2 if math.sin(t * 9) > 0 else 0
        img.alpha_composite(self.hand, (int(W2 / 2 - 105 - self.hand.width / 2), int(0.782 * H2 + wgl)))
        img.alpha_composite(self.hand, (int(W2 / 2 + 105 - self.hand.width / 2), int(0.782 * H2 - wgl)))
        self.dust.draw(img, t)
        if alert > 0:
            img.alpha_composite(Image.new("RGBA", img.size, (255, 40, 30, int(70 * alert))))
        zw, zh = int(W2 / zoom), int(H2 / zoom)
        cxx = W2 / 2
        cyy = (0.50 * H2) if cy is None else cy
        x0 = int(C.clamp(cxx - zw / 2, 0, W2 - zw))
        y0 = int(C.clamp(cyy - zh / 2, 0, H2 - zh))
        return img.convert("RGB").crop((x0, y0, x0 + zw, y0 + zh)).resize(
            (C.W, C.H), Image.Resampling.BILINEAR)


class Vault:
    def __init__(self, cx, cy, r):
        self.cx, self.cy, self.r = cx, cy, r
        self.door = self._door()
        self.back = self._back()

    def _door(self):
        r = self.r
        s = int(r * 2.5)
        img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(img, "RGBA")
        c = s / 2
        for rr_, col in ((0.99, (52, 60, 84)), (0.86, (38, 45, 66)), (0.60, (30, 36, 54))):
            d.ellipse((c - rr_ * r, c - rr_ * r, c + rr_ * r, c + rr_ * r), fill=(*col, 255))
        d.ellipse((c - 0.99 * r, c - 0.99 * r, c + 0.99 * r, c + 0.99 * r),
                  outline=(120, 140, 180, 200), width=4)
        for k in range(12):
            a = k * math.pi / 6
            bx, by = c + 0.78 * r * math.cos(a), c + 0.78 * r * math.sin(a)
            d.ellipse((bx - 9, by - 9, bx + 9, by + 9), fill=(90, 104, 134, 255))
        for k in range(3):
            a = k * 2 * math.pi / 3 + math.pi / 6
            d.line((c - 0.42 * r * math.cos(a), c - 0.42 * r * math.sin(a),
                    c + 0.42 * r * math.cos(a), c + 0.42 * r * math.sin(a)),
                   fill=(150, 166, 196, 255), width=10)
        d.ellipse((c - 26, c - 26, c + 26, c + 26), fill=(70, 82, 110, 255),
                  outline=(170, 190, 220, 255), width=3)
        mk = binance_mark(int(0.5 * r), (*C.GOLD, 230))
        img.alpha_composite(mk, (int(c - mk.width / 2), int(c - 0.72 * r)))
        return img

    def _back(self):
        r = self.r
        s = int(r * 2.6)
        m = C.radial_mask(s, s, s / 2, s / 2, r * 1.05, 255, 0, 1.6)
        col = Image.new("RGBA", (s, s), (255, 190, 60, 0))
        col.putalpha(m.point(lambda v: int(v * 0.9)))
        return col

"""Theme, fonts, easing and image helpers for the Binance-heist short."""
import math
import os

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
DUR = 48.0

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FDIR = os.path.join(ROOT, "fonts")
DJ = "/usr/share/fonts/truetype/dejavu"


def _first(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(paths)


ANTON = _first(os.path.join(FDIR, "Anton-Regular.ttf"))
BEBAS = _first(os.path.join(FDIR, "BebasNeue-Regular.ttf"))
DJ_BOLD = _first(os.path.join(DJ, "DejaVuSans-Bold.ttf"))
DJ_BOOK = _first(os.path.join(DJ, "DejaVuSans.ttf"))
DJ_MONO = _first(
    os.path.join(DJ, "DejaVuSansMono-Bold.ttf"),
    os.path.join(DJ, "DejaVuSansMono.ttf"),
)

_fc = {}


def _ttf(path, size):
    k = (path, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, int(size))
    return _fc[k]


def F_DISPLAY(s):
    return _ttf(ANTON, s)


def F_COND(s):
    return _ttf(BEBAS, s)


def F_BODY(s):
    return _ttf(DJ_BOLD, s)


def F_BOOK(s):
    return _ttf(DJ_BOOK, s)


def F_MONO(s):
    return _ttf(DJ_MONO, s)


# palette
DEEP = (6, 8, 16)
DEEP2 = (12, 16, 30)
PANEL = (17, 22, 38)
PANEL2 = (24, 31, 52)
INK = (8, 10, 18)
GOLD = (240, 185, 11)
GOLD_HI = (255, 224, 96)
GOLD_DIM = (146, 111, 10)
RED = (255, 64, 52)
RED_DEEP = (168, 28, 24)
CYAN = (86, 226, 214)
TEAL = (52, 199, 164)
WHITE = (243, 246, 250)
GREY = (150, 160, 175)
GREY2 = (86, 95, 112)


# ---------- math ----------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)


def remap(t, a, b):
    if b <= a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def lerp(a, b, t):
    return a + (b - a) * t


def ease_out_expo(t):
    t = clamp(t)
    return 1.0 if t >= 1 else 1 - 2 ** (-10 * t)


def ease_out_cubic(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out_back(t, s=1.70158):
    t = clamp(t) - 1
    return 1 + t * t * ((s + 1) * t + s)


def pulse(t, f=2.0, ph=0.0):
    return 0.5 + 0.5 * math.sin(2 * math.pi * f * t + ph)


def fmt_money(v):
    return "${:,.0f}".format(v)


# ---------- text ----------
_ts = {}


def text_sprite(text, font, fill, tracking=0.0, glow=None):
    key = (text, id(font), fill, tracking, glow)
    if key in _ts:
        return _ts[key]
    pad = 48
    if tracking:
        wid = sum(font.getlength(ch) + tracking for ch in text)
        asc, desc = font.getmetrics()
        tw, th = int(wid) + pad * 2, asc + desc + pad * 2
        sp = Image.new("RGBA", (max(2, tw), max(2, th)), (0, 0, 0, 0))
        d = ImageDraw.Draw(sp)
        x = float(pad)
        for ch in text:
            d.text((x, pad), ch, font=font, fill=fill)
            x += font.getlength(ch) + tracking
    else:
        bb = font.getbbox(text)
        tw = bb[2] - bb[0] + pad * 2
        th = bb[3] - bb[1] + pad * 2
        sp = Image.new("RGBA", (max(2, tw), max(2, th)), (0, 0, 0, 0))
        ImageDraw.Draw(sp).text((pad - bb[0], pad - bb[1]), text, font=font, fill=fill)
    if glow:
        rad, col, gain = glow
        am = sp.getchannel("A").filter(ImageFilter.GaussianBlur(rad))
        gr = Image.new("RGBA", sp.size, tuple(col) + (0,))
        gr.putalpha(am.point(lambda v: min(255, int(v * gain))))
        sp = Image.alpha_composite(gr, sp)
    _ts[key] = sp
    return sp


def blit(base, sp, x, y, alpha=1.0):
    """Paste RGBA sprite centered at (x, y) onto any-mode base."""
    if alpha <= 0:
        return
    if alpha < 1:
        sp = sp.copy()
        sp.putalpha(sp.getchannel("A").point(lambda v: int(v * alpha)))
    base.paste(sp, (int(x - sp.width / 2), int(y - sp.height / 2)), sp)


def text_w(font, text, tracking=0.0):
    if tracking:
        return sum(font.getlength(ch) + tracking for ch in text) - tracking
    return font.getlength(text)


def fit(fontfn, text, maxw, start, tracking=0.0):
    s = start
    while s > 14 and text_w(fontfn(s), text, tracking) > maxw:
        s -= 3
    return fontfn(s)


def chip(base, cx, cy, text, font, bg, fg, padx=26, pady=12, border=None):
    w = int(text_w(font, text)) + padx * 2 + 8
    asc, desc = font.getmetrics()
    h = asc + desc + pady * 2 + 8
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle(
        (4, 4, w - 4, h - 4),
        radius=(h - 8) // 2,
        fill=bg,
        outline=border,
        width=2 if border else 0,
    )
    d.text((w / 2, h / 2 - 2), text, font=font, fill=fg, anchor="mm")
    blit(base, c, cx, cy)


# ---------- images ----------
def vgrad(w, h, stops):
    ys = np.linspace(0.0, 1.0, h)
    pos = np.array([p for p, _ in stops])
    cols = np.array([c for _, c in stops], dtype=float)
    bands = np.zeros((h, 3))
    for c in range(3):
        bands[:, c] = np.interp(ys, pos, cols[:, c])
    arr = np.repeat(bands[:, None, :], w, axis=1).astype(np.uint8)
    return Image.fromarray(arr)


def radial_mask(w, h, cx, cy, r, inner=255, outer=0, fall=2.0):
    yy = np.arange(h, dtype=np.float32)[:, None]
    xx = np.arange(w, dtype=np.float32)[None, :]
    d = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2) / max(1e-6, r)
    m = np.clip(1.0 - d, 0.0, 1.0) ** fall
    a = outer + (inner - outer) * m
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


_sd = {}


def soft_dot(r, color, gain=1.0):
    k = (int(r), color, gain)
    if k in _sd:
        return _sd[k]
    rr = int(r)
    s = rr * 2 + 2
    m = radial_mask(s, s, s / 2, s / 2, rr * 0.98, 255, 0, 2.2)
    m = m.point(lambda v: int(v * gain))
    sp = Image.new("RGBA", (s, s), tuple(color) + (0,))
    sp.putalpha(m)
    _sd[k] = sp
    return sp


_vig = None


def vignette():
    global _vig
    if _vig is None:
        m = radial_mask(W, H, W / 2, H * 0.47, W * 0.64, 0, 175, 1.35)
        _vig = (Image.new("RGB", (W, H), (0, 0, 0)), m)
    return _vig


def apply_vignette(img):
    bg, m = vignette()
    img.paste(bg, (0, 0), m)


_gr = []


def _grains():
    global _gr
    if not _gr:
        rng = np.random.default_rng(20261)
        for _ in range(12):
            a = rng.integers(0, 15, (H // 2, W // 2, 3), dtype=np.uint8)
            _gr.append(Image.fromarray(a).resize((W, H), Image.Resampling.NEAREST))
    return _gr


def apply_grain(img, idx):
    return ImageChops.add(img, _grains()[idx % 12], scale=1, offset=-7)


_sc = None


def scanlines(w, h):
    global _sc
    if _sc is None or _sc.size != (w, h):
        a = np.zeros((h, w, 4), np.uint8)
        a[::3, :, 3] = 26
        _sc = Image.fromarray(a)
    return _sc


# ---------- fx ----------
def glitch(img, rng, k=1.0):
    w, h = img.size
    out = img.copy()
    for _ in range(int(4 + 10 * k)):
        y = int(rng.integers(0, max(1, h - 40)))
        bh = int(rng.integers(8, 90))
        dx = int(rng.integers(-90, 90) * k)
        band = img.crop((0, y, w, min(h, y + bh)))
        out.paste(band, (dx, y))
    if k > 0.35:
        r, g, b = out.split()
        sh = int(6 * k)
        out = Image.merge(
            "RGB", (ImageChops.offset(r, sh, 0), g, ImageChops.offset(b, -sh, 0))
        )
    return out


def flash(img, a):
    if a <= 0:
        return img
    return Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), clamp(a, 0, 0.9))


def fade_to(img, a, color=(0, 0, 0)):
    if a <= 0:
        return img
    return Image.blend(img, Image.new("RGB", img.size, color), clamp(a))


class Dust:
    """Stateless drifting motes, deterministic in t."""

    def __init__(self, n=40, seed=11, box=(0, 0, W, H), vmin=6, vmax=26):
        rng = np.random.default_rng(seed)
        self.x0 = rng.uniform(box[0], box[2], n)
        self.y0 = rng.uniform(box[1], box[3], n)
        self.v = rng.uniform(vmin, vmax, n)
        self.ph = rng.uniform(0, 6.28, n)
        self.sz = rng.integers(2, 6, n)
        self.al = rng.uniform(0.25, 0.8, n)
        self.box = box

    def draw(self, img, t, color=(185, 212, 232)):
        y0b, y1b = self.box[1], self.box[3]
        h = y1b - y0b
        for x0, y0, v, p, s, a in zip(self.x0, self.y0, self.v, self.ph, self.sz, self.al):
            x = x0 + math.sin(t * 0.6 + p) * 10
            y = y0b + ((y0 - y0b) - v * t) % h
            blit(img, soft_dot(int(s), color), x, y, alpha=a * (0.6 + 0.4 * pulse(t, 0.7, p)))

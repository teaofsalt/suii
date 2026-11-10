"""Scenes, timeline and global post-processing."""
import math

import numpy as np
from PIL import Image, ImageDraw

from . import art as A
from . import core as C

ROOM = None
CLOSE = None
VAULT = None
FCARD = None

_grads = {}


def scene_bg(name, stops):
    if name not in _grads:
        _grads[name] = C.vgrad(C.W, C.H, stops).convert("RGB")
    return _grads[name].copy()


def blit_scaled(img, sp, x, y, scale, alpha=1.0):
    if scale != 1.0:
        sp = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))),
                       Image.Resampling.BILINEAR)
    C.blit(img, sp, x, y, alpha)


def kicker(img, text, y=330, bgc=None, fgc=None, font=None, border=None):
    C.chip(img, C.W / 2, y, text, font or C.F_BODY(32),
           bgc or (*C.RED, 235), fgc or C.WHITE, border=border)


def lower_third(img, l1, l2, p):
    if p <= 0:
        return
    e = C.ease_out_cubic(p)
    bw, bh = 950, 190
    ov = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle((0, 0, bw, bh), radius=18, fill=(10, 13, 22, int(235 * e)))
    d.rectangle((0, 0, 8, bh), fill=(*C.GOLD, int(255 * e)))
    s1 = C.text_sprite(l1, C.F_COND(52), (*C.GOLD_HI, 255), tracking=1)
    s2 = C.text_sprite(l2, C.F_BODY(29), (*C.WHITE, 255))
    C.blit(ov, s1, bw / 2 + 10, 62, alpha=e)
    C.blit(ov, s2, bw / 2 + 10, 140, alpha=e)
    img.paste(ov, (int((C.W - bw) / 2), int(1530 + 40 * (1 - e))), ov)


def sources(img, y=1680, alpha=1.0):
    s = C.text_sprite("SOURCES: FBI / BBC / NPR / TRM LABS / COINDESK",
                      C.F_MONO(24), (*C.GREY, 255))
    C.blit(img, s, C.W / 2, y, alpha=alpha)


def bez(a, c, b, u):
    x = (1 - u) ** 2 * a[0] + 2 * (1 - u) * u * c[0] + u * u * b[0]
    y = (1 - u) ** 2 * a[1] + 2 * (1 - u) * u * c[1] + u * u * b[1]
    return x, y


# ---------------------------------------------------------------- S1 hook
def s1(tl, idx):
    img = scene_bg("hook", [(0, (14, 4, 10)), (0.5, (12, 8, 20)), (1, (5, 4, 12))])
    d = ImageDraw.Draw(img, "RGBA")
    C.blit(img, C.soft_dot(520, C.RED), 540, 900, alpha=0.10 + 0.08 * C.pulse(tl, 1.2))
    for k in range(3):
        rr = 180 + ((tl * 170 + k * 230) % 680)
        a = (1 - rr / 680) * 0.45
        d.ellipse((540 - rr, 900 - rr, 540 + rr, 900 + rr), outline=(*C.RED, int(255 * a)), width=4)
    if tl > 0.15:
        C.chip(img, 540, 420, "BREAKING", C.F_BODY(34), (*C.RED, 235), C.WHITE)
    p = C.ease_out_expo(C.remap(tl, 0.25, 2.0))
    f = C.fit(C.F_DISPLAY, "$6,300,000,000", 950, 165)
    sp = C.text_sprite("$6,300,000,000", f,
                       (*C.WHITE, 255) if tl > 2.0 else (*C.GOLD_HI, 255),
                       glow=(16, C.RED if tl > 2.0 else C.GOLD, 0.9))
    shx = int(7 * (1 - p) * math.sin(tl * 80))
    shy = int(5 * (1 - p) * math.cos(tl * 70))
    C.blit(img, sp, 540 + shx, 860 + shy)
    if tl > 2.15:
        q = C.remap(tl, 2.15, 2.6)
        sp2 = C.text_sprite("STOLEN", C.F_DISPLAY(150), (*C.RED, 255), tracking=6,
                            glow=(18, C.RED, 1.0))
        sp2 = sp2.rotate(-4, resample=Image.Resampling.BILINEAR, expand=True)
        blit_scaled(img, sp2, 540, 1150, 2.2 - 1.2 * C.ease_out_back(q),
                    alpha=C.clamp(q * 1.5))
    if tl > 2.95:
        q = C.ease_out_back(C.remap(tl, 2.95, 3.3))
        sp3 = C.text_sprite("IN ~20 MINUTES", C.F_COND(72), (*C.GOLD, 255), tracking=3)
        blit_scaled(img, sp3, 540, 1290, 0.7 + 0.3 * q, alpha=C.clamp(q * 1.6))
    if tl > 3.3:
        C.blit(img, C.text_sprite("THE LARGEST CRYPTO HEIST IN HISTORY",
                                  C.F_BODY(36), (*C.WHITE, 235)), 540, 1385)
    if tl > 3.5:
        C.chip(img, 540, 1470, "BINANCE  -  OCT 29, 2026", C.F_MONO(26),
               (16, 21, 36, 220), (*C.GREY, 255), border=(*C.GREY2, 160))
    for ht, gk in ((0.5, 0.5), (1.4, 0.45), (2.2, 0.6), (3.82, 1.0)):
        if abs(tl - ht) < 0.08:
            img = C.glitch(img, np.random.default_rng(idx), gk)
    if tl < 0.3:
        img = C.fade_to(img, 1 - tl / 0.3)
    return img


# ---------------------------------------------------------------- S2 room reveal
def s2(tl, idx):
    global ROOM
    if ROOM is None:
        ROOM = A.Room()
    zoom = 1.0 + 0.05 * C.ease_in_out(C.remap(tl, 0.2, 6.4))
    cy = ROOM.H2 * (0.505 + 0.02 * C.ease_in_out(C.remap(tl, 0.2, 6.4)))
    alert = C.remap(tl, 5.0, 5.6) * 0.55
    img = ROOM.frame(tl + 6.0, zoom, cy=cy, alert=alert)
    p = C.ease_out_back(C.remap(tl, 0.15, 0.75))
    fh = C.fit(C.F_DISPLAY, "BINANCE BREACHED", 900, 100)
    sp = C.text_sprite("BINANCE BREACHED", fh, (*C.WHITE, 255), glow=(14, C.GOLD, 0.55))
    blit_scaled(img, sp, 540, 320, 0.6 + 0.4 * p, alpha=C.clamp(p * 1.4))
    if tl > 0.35:
        C.chip(img, 540, 205, "BREAKING  -  OCT 29", C.F_BODY(30), (*C.RED, 235), C.WHITE)
    if tl > 0.7:
        q = C.ease_out_cubic(C.remap(tl, 0.7, 1.2))
        C.blit(img, C.text_sprite("$6.3B IN CUSTOMER CRYPTO DRAINED - LARGEST EVER",
                                  C.F_COND(56), (*C.GOLD, 255), tracking=2),
               540, 432, alpha=q)
    lower_third(img, "FBI: NORTH KOREA'S TRADERTRAITOR (LAZARUS)",
                "ATTRIBUTED BY THE FBI AND BLOCKCHAIN ANALYSTS",
                C.remap(tl, 2.3, 3.0))
    return img


# ---------------------------------------------------------------- S3 the trap
def _close():
    global CLOSE
    if CLOSE is None:
        img = scene_bg("close", [(0, (5, 6, 12)), (0.55, (10, 13, 24)), (1, (4, 5, 10))])
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle((80, 1490, 1000, 1600), radius=18, fill=(22, 28, 46, 255))
        d.line((80, 1490, 1000, 1490), fill=(90, 110, 140, 255), width=3)

        def mon(x0, y0, x1, y1):
            d.rounded_rectangle((x0, y0, x1, y1), radius=14, fill=(10, 12, 20, 255),
                                outline=(46, 58, 84, 255), width=3)
            for yy in range(y0 + 28, y1 - 18, 24):
                d.line((x0 + 18, yy, x1 - 18, yy), fill=(22, 28, 46, 255), width=5)

        mon(110, 760, 370, 1160)
        mon(390, 640, 690, 1160)
        mon(710, 760, 970, 1160)
        d.rounded_rectangle((330, 1440, 750, 1512), radius=12, fill=(12, 15, 26, 255),
                            outline=(60, 74, 100, 255), width=2)
        CLOSE = img
    return CLOSE.copy()


def _close_frame(tl, speed=9.0, red=0.0):
    img = _close()
    hk = A.hacker_sprite(2.05)
    bob = int(math.sin(tl * 1.6) * 5)
    img.paste(hk, (int(540 - hk.width / 2), int(1490 - hk.height + bob)), hk)
    C.blit(img, C.soft_dot(240, C.CYAN), 380, 900, alpha=0.10 + 0.05 * C.pulse(tl, 5))
    C.blit(img, C.soft_dot(200, C.RED), 720, 880, alpha=0.08 + 0.05 * C.pulse(tl, 4, 1.5))
    h = A.hand_sprite(2.2)
    wgl = 4 if math.sin(tl * speed) > 0 else 0
    C.blit(img, h, 440, 1470 + wgl)
    C.blit(img, h, 640, 1470 - wgl)
    C.Dust(n=26, seed=5, box=(60, 120, 1020, 1380)).draw(img, tl)
    if red > 0:
        img = Image.blend(img, Image.new("RGB", img.size, (120, 10, 8)), red * 0.5)
    return img


def _fcard():
    global FCARD
    if FCARD is None:
        c = Image.new("RGBA", (600, 560), (0, 0, 0, 0))
        dd = ImageDraw.Draw(c)
        dd.rounded_rectangle((0, 0, 600, 560), radius=24, fill=(16, 21, 36, 245),
                             outline=(52, 64, 92, 255), width=2)
        dd.rounded_rectangle((250, 60, 350, 220), radius=12, fill=(30, 40, 64, 255),
                             outline=(90, 110, 150, 255), width=3)
        dd.polygon([(310, 60), (350, 100), (310, 100)], fill=(90, 110, 150, 255))
        dd.line((275, 160, 325, 160), fill=(140, 170, 210, 255), width=6)
        dd.line((275, 185, 325, 185), fill=(140, 170, 210, 255), width=6)
        dd.line((300, 250, 300, 300), fill=(*C.CYAN, 255), width=8)
        dd.polygon([(285, 292), (315, 292), (300, 322)], fill=(*C.CYAN, 255))
        FCARD = c
    return FCARD


def s3(tl, idx):
    if tl < 2.7:
        img = scene_bg("bait", [(0, (8, 10, 20)), (1, (5, 6, 13))])
        kicker(img, "THE BAIT", y=290)
        C.blit(img, C.text_sprite("A 'RECRUITER' PINGS A BINANCE ENGINEER",
                                  C.F_BODY(32), (*C.GREY, 255)), 540, 372)
        card = Image.new("RGBA", (880, 640), (0, 0, 0, 0))
        dd = ImageDraw.Draw(card)
        dd.rounded_rectangle((0, 0, 880, 640), radius=24, fill=(16, 21, 36, 240),
                             outline=(52, 64, 92, 255), width=2)
        dd.ellipse((40, 40, 76, 76), fill=(*C.CYAN, 255))
        C.blit(card, C.text_sprite("scout_77   JOB PLATFORM MESSAGE", C.F_BODY(28),
                                   (*C.GREY, 255)), 480, 58)
        msgs = [("Hi! We're hiring a Senior Platform Engineer", 0.25),
                ("Comp: 2x your current package", 0.95),
                ("Can you do a quick interview today?", 1.65)]
        for i, (m, t0) in enumerate(msgs):
            q = C.remap(tl, t0, t0 + 0.3)
            if q <= 0:
                continue
            sp = C.text_sprite(m, C.fit(C.F_BODY, m, 620, 30), (*C.WHITE, 255))
            bub = Image.new("RGBA", (sp.width + 60, 96), (0, 0, 0, 0))
            bd = ImageDraw.Draw(bub)
            bd.rounded_rectangle((0, 0, bub.width, 96), radius=20, fill=(28, 36, 58, 255))
            C.blit(bub, sp, bub.width / 2, 48)
            blit_scaled(card, bub, 60 + bub.width / 2, 150 + i * 140,
                        0.85 + 0.15 * C.ease_out_back(q), alpha=C.clamp(q * 2))
        if tl > 2.15:
            for k in range(3):
                a = C.pulse(tl, 3.0, k * 0.7)
                dd.ellipse((700 + k * 34, 560, 720 + k * 34, 580),
                           fill=(*C.CYAN, int(120 + 120 * a)))
        img.paste(card, (100, 560), card)
        if tl > 2.2:
            C.chip(img, 540, 1295, "INTERVIEW SCHEDULED", C.F_BODY(30),
                   (24, 31, 52, 220), (*C.TEAL, 255), border=(*C.TEAL, 170))
        return img
    if tl < 5.3:
        img = _close_frame(tl - 2.7, speed=11)
        kicker(img, "SOCIAL ENGINEERING", y=260, bgc=(*C.GOLD, 235), fgc=(12, 12, 16))
        for txt, t0, y in ((u"\u2713 ROUND 1 - FAKE HR VIDEO CALL", 0.35, 360),
                           (u"\u2713 ROUND 2 - FAKE 'CEO' ON A CHAT APP", 1.15, 450)):
            q = C.remap(tl - 2.7, t0, t0 + 0.3)
            if q > 0:
                C.chip(img, 540, y, txt, C.F_BODY(30), (24, 31, 52, 230),
                       (*C.WHITE, 255), border=(*C.TEAL, int(170 * C.clamp(q * 2))))
        return img
    if tl < 7.4:
        red = C.remap(tl, 6.45, 6.9) * 0.6
        img = _close_frame(tl - 2.7, speed=4, red=red)
        kicker(img, "THE 'ASSIGNMENT'", y=500, bgc=(*C.GOLD, 235), fgc=(12, 12, 16))
        img.paste(_fcard(), (240, 580), _fcard())
        f = C.F_MONO(36)
        C.blit(img, C.text_sprite("assignment.zip", f, (*C.WHITE, 255)), 540, 1058)
        pr = C.remap(tl, 5.6, 6.35) * 0.87
        d = ImageDraw.Draw(img, "RGBA")
        d.rounded_rectangle((320, 1108, 760, 1132), radius=10, fill=(14, 18, 30, 255),
                            outline=(60, 74, 100, 255), width=2)
        if pr > 0:
            bad = tl > 6.45
            d.rounded_rectangle((322, 1110, 322 + int(436 * pr), 1130), radius=8,
                                fill=(*C.RED, 255) if bad else (*C.CYAN, 255))
        C.blit(img, C.text_sprite("%d%%" % int(pr * 100), C.F_MONO(28),
                                  (*C.CYAN, 255) if tl <= 6.45 else (*C.RED, 255)), 812, 1120)
        if tl > 6.55:
            C.blit(img, C.text_sprite("MALWARE EXECUTED ON WORK LAPTOP",
                                      C.F_BODY(32), (*C.RED, 255), glow=(8, C.RED, 0.8)),
                   540, 1230)
        if abs(tl - 6.5) < 0.1:
            img = C.glitch(img, np.random.default_rng(idx), 0.7)
        return img
    img = scene_bg("alert", [(0, (120, 16, 14)), (1, (70, 10, 10))])
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(2):
        rr = 220 + ((tl * 300 + k * 300) % 620)
        a = (1 - rr / 620) * 0.4
        d.ellipse((540 - rr, 900 - rr, 540 + rr, 900 + rr),
                  outline=(255, 255, 255, int(255 * a)), width=4)
    f = C.fit(C.F_DISPLAY, "ENDPOINT TAKEN", 900, 130)
    C.blit(img, C.text_sprite("ENDPOINT TAKEN", f, (*C.WHITE, 255),
                              glow=(18, (20, 10, 10), 0.9)), 540, 880)
    C.blit(img, C.text_sprite("INTERNAL TOOLS EXPOSED", C.F_COND(60),
                              (*C.GOLD, 255), tracking=3), 540, 1030)
    return img


# ---------------------------------------------------------------- S4 the heist
def s4(tl, idx):
    global VAULT
    if VAULT is None:
        VAULT = A.Vault(540, 940, 290)
    img = scene_bg("heist", [(0, (7, 6, 14)), (0.6, (12, 9, 18)), (1, (5, 5, 11))])
    d = ImageDraw.Draw(img, "RGBA")
    C.blit(img, C.soft_dot(420, C.GOLD), 540, 940, alpha=0.07 + 0.05 * C.pulse(tl, 1.4))
    p = C.ease_out_expo(C.remap(tl, 0.3, 3.2))
    f = C.fit(C.F_DISPLAY, "$6,300,000,000", 900, 140)
    C.blit(img, C.text_sprite("$%s" % format(int(6_300_000_000 * p), ",d"), f,
                              (*C.GOLD_HI, 255), glow=(16, C.GOLD, 0.85)), 540, 350)
    C.blit(img, C.text_sprite("WITHDRAWN FROM BINANCE", C.F_COND(50),
                              (*C.GREY, 255), tracking=3), 540, 448)
    if tl > 3.3:
        q = C.remap(tl, 3.3, 3.7)
        st = C.text_sprite("IN ~20 MINUTES", C.F_DISPLAY(74), (*C.RED, 255), tracking=4,
                           glow=(14, C.RED, 0.9)).rotate(-3, expand=True,
                                                         resample=Image.Resampling.BILINEAR)
        blit_scaled(img, st, 540, 568, 1.25 - 0.25 * C.ease_out_back(q), alpha=C.clamp(q * 2))
    r = VAULT.r
    d.ellipse((540 - r * 0.92, 940 - r * 0.92, 540 + r * 0.92, 940 + r * 0.92), fill=(8, 9, 15, 255))
    if 0.85 < tl < 1.6:
        cp = C.remap(tl, 0.85, 1.35)
        rng = np.random.default_rng(42)
        pts = [(540 + int(rng.uniform(-8, 8)), 680 + k * 26) for k in range(20)]
        a = (0.4 + 0.6 * C.pulse(tl, 9)) * cp
        d.line(pts, fill=(*C.GOLD_HI, int(220 * a)), width=5)
        C.blit(img, C.soft_dot(180, C.GOLD), 540, 940, alpha=0.3 * cp)
    if tl > 0.85:
        C.blit(img, VAULT.back, 540, 940, alpha=0.35 + 0.65 * C.ease_in_out(C.remap(tl, 1.5, 2.4)))
    op = C.ease_in_out(C.remap(tl, 1.5, 2.35))
    ds = VAULT.door
    if op > 0:
        sc = 1 - 0.14 * op
        ds = ds.resize((int(ds.width * sc), int(ds.height * sc)), Image.Resampling.BILINEAR)
    C.blit(img, ds, 540 + 250 * op, 940)
    if tl > 2.1:
        coin = A.coin_sprite(34)
        for i in range(22):
            t0 = 2.1 + i * 0.24
            u = C.remap(tl, t0, t0 + 1.05) ** 2
            if 0 < u < 1:
                for tr, al in ((0.10, 0.10), (0.05, 0.22)):
                    u2 = u - tr
                    if u2 > 0:
                        x2, y2 = bez((540, 940), (700, 1200), (905, 1500), u2)
                        C.blit(img, coin, x2, y2, alpha=al)
                x, y = bez((540, 940), (700, 1200), (905, 1500), u)
                spc = coin.rotate((tl * 380 + i * 47) % 360, resample=Image.Resampling.BILINEAR,
                                  expand=True)
                C.blit(img, spc, x, y)
    nx, ny = 905, 1500
    phase = (tl * 0.9) % 1.0
    rr_ = 26 + phase * 46
    d.ellipse((nx - rr_, ny - rr_, nx + rr_, ny + rr_), outline=(*C.RED, int(180 * (1 - phase))), width=4)
    d.ellipse((nx - 10, ny - 10, nx + 10, ny + 10), fill=(*C.RED, 255))
    C.blit(img, C.text_sprite("DPRK WALLETS", C.F_COND(44), (*C.RED, 255), tracking=3), nx - 12, ny - 62)
    C.blit(img, C.text_sprite("UNAUTHORIZED WITHDRAWALS - TRANSACTION APPROVALS BYPASSED",
                              C.F_MONO(25), (*C.GREY, 220)), 540, 1720)
    for ht, gk in ((1.32, 0.6), (6.6, 0.45)):
        if abs(tl - ht) < 0.08:
            img = C.glitch(img, np.random.default_rng(idx), gk)
    return img


# ---------------------------------------------------------------- S5 scale
def s5(tl, idx):
    img = scene_bg("scale", [(0, (7, 9, 17)), (1, (5, 6, 12))])
    ft = C.fit(C.F_DISPLAY, "BIGGEST CRYPTO HEISTS - EVER", 940, 88)
    C.blit(img, C.text_sprite("BIGGEST CRYPTO HEISTS - EVER", ft, (*C.WHITE, 255),
                              glow=(12, C.GOLD, 0.4)), 540, 300)
    C.blit(img, C.text_sprite("THE $6.3B BINANCE DRAIN = 4.2X THE OLD RECORD",
                              C.F_COND(54), (*C.GOLD, 255), tracking=2), 540, 398)
    rows = ((305, "DMM BITCOIN - 2024", "$305M"), (611, "POLY NETWORK - 2021", "$611M"),
            (625, "RONIN - 2022", "$625M"), (1500, "BYBIT - 2025", "$1.5B"),
            (6300, "BINANCE - 2026", "$6.3B"))
    d = ImageDraw.Draw(img, "RGBA")
    y0, rh = 520, 168
    for i, (v, name, vs) in enumerate(rows):
        q = C.ease_out_cubic(C.remap(tl, 0.35 + i * 0.28, 0.9 + i * 0.28))
        y = y0 + i * rh
        last = i == len(rows) - 1
        d.rounded_rectangle((70, y + 34, 1010, y + 94), radius=12, fill=(16, 20, 34, 255))
        w = (90 + (v / 6300) * 700) * q
        if w > 8:
            col = (*C.GOLD, 255) if last else (52, 76, 110, 255)
            d.rounded_rectangle((70, y + 34, int(70 + w), y + 94), radius=12, fill=col)
            if last:
                d.rectangle((70, y + 34, int(70 + w), y + 42), fill=(*C.GOLD_HI, 255))
        spn = C.text_sprite(name, C.F_COND(44), (*C.WHITE, 255) if not last else (*C.GOLD_HI, 255))
        img.paste(spn, (70, y - 8), spn)
        spv = C.text_sprite(vs, C.F_DISPLAY(54), (*C.WHITE, 255) if not last else (*C.GOLD_HI, 255))
        C.blit(img, spv, 940, y + 64)
        if last and q > 0.92:
            C.chip(img, 240, y + 64, "NEW RECORD", C.F_BODY(24), (*C.RED, 235), C.WHITE)
    note = u"\u2248 2X ALL CRYPTO DPRK-LINKED HACKERS STOLE SINCE 2017 (TRM LABS)"
    C.blit(img, C.text_sprite(note, C.fit(C.F_BODY, note, 920, 28), (*C.GREY, 255)), 540, 1442)
    sources(img, y=1520)
    if abs(tl - 1.98) < 0.07:
        img = C.glitch(img, np.random.default_rng(idx), 0.55)
    return img


# ---------------------------------------------------------------- S6 aftermath
def s6(tl, idx):
    img = scene_bg("after", [(0, (7, 9, 17)), (1, (5, 6, 12))])
    ft = C.fit(C.F_DISPLAY, "WHAT HAPPENS NOW?", 900, 88)
    C.blit(img, C.text_sprite("WHAT HAPPENS NOW?", ft, (*C.WHITE, 255),
                              glow=(12, C.CYAN, 0.4)), 540, 290)
    qb = Image.new("RGBA", (940, 130), (0, 0, 0, 0))
    qd = ImageDraw.Draw(qb)
    qd.rounded_rectangle((0, 0, 940, 130), radius=18, fill=(16, 21, 36, 240),
                         outline=(52, 64, 92, 255), width=2)
    qd.rectangle((0, 0, 8, 130), fill=(*C.RED, 255))
    q1 = C.text_sprite(u"\u201cABSURD RHETORIC\u201d - PYONGYANG DENIES ROLE", C.F_COND(48), (*C.WHITE, 255))
    C.blit(qb, q1, 480, 46, alpha=C.ease_out_cubic(C.remap(tl, 0.2, 0.6)))
    q2 = C.text_sprite("KIM YO JONG - FBI STANDS BY TRADERTRAITOR ATTRIBUTION",
                       C.F_BODY(24), (*C.GREY, 255))
    C.blit(qb, q2, 480, 102, alpha=C.ease_out_cubic(C.remap(tl, 0.5, 0.9)))
    img.paste(qb, (70, 380), qb)
    cards = (
        (">40%", C.GOLD, "OF STOLEN FUNDS FROZEN BY THE INDUSTRY", "TRM LABS", "snow"),
        ("MADE WHOLE", C.GOLD, "STOLEN USER CRYPTO REPLACED FROM BINANCE'S OWN FUNDS", "BINANCE", "shield"),
        ("$4.72B", C.GOLD, "NET WITHDRAWALS POST-REOPENING - FLOWS STABILISING", "BINANCE SPOKESPERSON", "coin"),
        ("TRADERTRAITOR", C.RED, "SAME DPRK UNIT BEHIND THE $1.5B BYBIT HEIST (2025)", "FBI", "mark"),
    )
    cw, ch, gap = 465, 380, 30
    x0, y0 = 60, 610
    for i, (head, hc, body, cite, icon) in enumerate(cards):
        t0 = 0.5 + i * 0.42
        q = C.remap(tl, t0, t0 + 0.38)
        if q <= 0:
            continue
        cx0 = x0 + (i % 2) * (cw + gap)
        cy0 = y0 + (i // 2) * (ch + gap)
        sc = 0.85 + 0.15 * C.ease_out_back(q)
        card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        dd = ImageDraw.Draw(card)
        dd.rounded_rectangle((0, 0, cw, ch), radius=20, fill=(16, 21, 36, 242),
                             outline=(52, 64, 92, 255), width=2)
        dd.rectangle((0, 0, cw, 6), fill=(*hc, 255))
        ic = C.W / 2  # icon glyph
        mxx, myy = cw / 2, 86
        if icon == "snow":
            for a in (0, 60, 120):
                ar = math.radians(a + 90)
                dd.line((mxx - 34 * math.cos(ar), myy - 34 * math.sin(ar),
                         mxx + 34 * math.cos(ar), myy + 34 * math.sin(ar)),
                        fill=(*C.CYAN, 255), width=5)
        elif icon == "shield":
            dd.polygon([(mxx, myy - 36), (mxx + 30, myy - 20), (mxx + 30, myy + 10),
                        (mxx, myy + 38), (mxx - 30, myy + 10), (mxx - 30, myy - 20)],
                       fill=(*C.TEAL, 255))
        elif icon == "coin":
            dd.ellipse((mxx - 32, myy - 32, mxx + 32, myy + 32), fill=(196, 148, 10, 255),
                       outline=(255, 214, 80, 255), width=4)
            C.blit(card, C.text_sprite("$", C.F_DISPLAY(52), (20, 20, 24, 255)), mxx, myy + 2)
        else:
            mk = A.binance_mark(64, (*C.RED, 255))
            card.alpha_composite(mk, (int(mxx - 32), int(myy - 32)))
        fh = C.fit(C.F_DISPLAY, head, cw - 60, 66)
        C.blit(card, C.text_sprite(head, fh, (*hc, 255), glow=(8, hc, 0.5)), cw / 2, 200)
        fbs = C.F_BOOK(24)
        words = body.split()
        lines, cur = [], ""
        for wd in words:
            if C.text_w(fbs, cur + " " + wd) > cw - 70:
                lines.append(cur)
                cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines.append(cur)
        for j, ln in enumerate(lines[:2]):
            C.blit(card, C.text_sprite(ln, fbs, (*C.GREY, 255)), cw / 2, 262 + j * 32)
        C.blit(card, C.text_sprite(cite, C.F_MONO(20), (*C.GREY2, 255)), cw / 2, ch - 30)
        blit_scaled(img, card, cx0 + cw / 2, cy0 + ch / 2, sc, alpha=C.clamp(q * 2))
    sources(img, y=1680)
    return img


# ---------------------------------------------------------------- S7 cta
def s7(tl, idx):
    img = scene_bg("cta", [(0, (6, 7, 14)), (0.6, (10, 8, 18)), (1, (4, 5, 10))])
    d = ImageDraw.Draw(img, "RGBA")
    C.blit(img, C.soft_dot(260, C.GOLD), 540, 430, alpha=0.16 + 0.1 * C.pulse(tl, 1.2))
    mk = A.binance_mark(150, (*C.GOLD, 255)).rotate(tl * 80, resample=Image.Resampling.BILINEAR,
                                                    expand=True)
    C.blit(img, mk, 540, 430)
    q = C.ease_out_back(C.remap(tl, 0.15, 0.6))
    blit_scaled(img, C.text_sprite("ONE ENGINEER.", C.F_DISPLAY(104), (*C.WHITE, 255)),
                540, 660, 0.7 + 0.3 * q, alpha=C.clamp(q * 1.6))
    q2 = C.ease_out_back(C.remap(tl, 0.5, 0.95))
    blit_scaled(img, C.text_sprite("ONE DOWNLOAD.", C.F_DISPLAY(104), (*C.WHITE, 255)),
                540, 800, 0.7 + 0.3 * q2, alpha=C.clamp(q2 * 1.6))
    q3 = C.ease_out_expo(C.remap(tl, 0.9, 1.7))
    f = C.fit(C.F_DISPLAY, "$6,300,000,000", 940, 150)
    C.blit(img, C.text_sprite("$6,300,000,000", f, (*C.GOLD_HI, 255),
                              glow=(16, C.GOLD, 0.9)), 540, 970,
           alpha=q3 * (0.85 + 0.15 * C.pulse(tl, 2)))
    if tl > 1.5:
        d.rectangle((240, 1078, 840, 1082), fill=(*C.GOLD, int(140 * C.clamp(C.remap(tl, 1.5, 1.9)))))
    if tl > 1.9:
        C.chip(img, 540, 1160, "VERIFY EVERY RECRUITER", C.F_BODY(32),
               (16, 21, 36, 230), (*C.CYAN, 255), border=(*C.CYAN, 150))
    if tl > 2.2:
        C.chip(img, 540, 1250, "NEVER RUN 'ASSIGNMENTS' ON WORK DEVICES", C.F_BODY(32),
               (16, 21, 36, 230), (*C.CYAN, 255), border=(*C.CYAN, 150))
    if tl > 2.7:
        q4 = C.ease_out_back(C.remap(tl, 2.7, 3.2))
        btn = Image.new("RGBA", (500, 130), (0, 0, 0, 0))
        bd = ImageDraw.Draw(btn)
        bd.rounded_rectangle((0, 0, 500, 130), radius=32, fill=(*C.RED, 255))
        bd.rounded_rectangle((6, 6, 494, 124), radius=28, outline=(255, 255, 255, 70), width=2)
        C.blit(btn, C.text_sprite("SUBSCRIBE", C.F_DISPLAY(64), (255, 255, 255, 255)), 250, 62)
        blit_scaled(img, btn, 540, 1430, 0.8 + 0.2 * q4, alpha=C.clamp(q4 * 2))
        ph = (tl * 1.1) % 1.0
        rr = 250 + ph * 60
        d.ellipse((540 - rr, 1430 - rr * 0.28, 540 + rr, 1430 + rr * 0.28),
                  outline=(*C.RED, int(150 * (1 - ph))), width=4)
    if tl > 3.3:
        C.blit(img, C.text_sprite("FOLLOW FOR CRYPTO SECURITY BREAKDOWNS",
                                  C.F_COND(52), (*C.GREY, 255), tracking=3), 540, 1580)
    sources(img, y=1680)
    return img


SCENES = ((0.0, s1), (4.2, s2), (10.6, s3), (19.2, s4), (27.2, s5),
          (33.8, s6), (41.4, s7))


def frame(idx):
    t = idx / C.FPS
    si = 0
    for k, (st, _) in enumerate(SCENES):
        if t >= st:
            si = k
    tl = t - SCENES[si][0]
    img = SCENES[si][1](tl, idx)
    if tl < 0.16 and si > 0:
        k = 1 - tl / 0.16
        img = C.flash(img, 0.7 * k)
        img = C.glitch(img, np.random.default_rng(idx), 0.5 * k)
    if si == 0 and tl < 0.3:
        img = C.fade_to(img, 1 - tl / 0.3)
    if t > C.DUR - 0.9:
        img = C.fade_to(img, C.remap(t, C.DUR - 0.9, C.DUR - 0.1))
    img = C.apply_grain(img, idx)
    C.apply_vignette(img)
    d = ImageDraw.Draw(img)
    d.rectangle((0, C.H - 6, C.W * t / C.DUR, C.H), fill=C.GOLD)
    return img

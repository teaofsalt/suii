"""Render the Binance $6.3B hack YouTube Short (1080x1920, ~60s)."""

import math
import os
import subprocess
import wave

import numpy as np
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
FPS = 30
SR = 24000
LEAD, TAIL = 0.35, 0.55
RATE = "+10%"
VOICE = "en-US-ChristopherNeural"

RED = (255, 59, 59)
WHITE = (245, 247, 250)
GRAY = (154, 163, 178)
GREEN = (52, 211, 153)
AMBER = (255, 197, 59)
INK = (6, 8, 16)

SCENES = [
    dict(vo="The biggest crypto heist in history just happened. And the F B I says North Korea did it.",
         lines=[("THE BIGGEST", WHITE), ("CRYPTO HEIST", WHITE), ("IN HISTORY", WHITE)],
         hero="$6,300,000,000", sub="GONE IN 20 MINUTES"),
    dict(vo="October 29th. Six point three billion dollars drains out of Binance in about twenty minutes, across ten blockchains.",
         lines=[("OCT 29, 2026 · 20:05 UTC", GRAY)], hero="$6.36 BILLION", sub="DRAINED IN ~20 MIN", chip="ACROSS 10 BLOCKCHAINS"),
    dict(vo="That's four times the Bybit hack. The largest theft in crypto history.",
         bars=[("BINANCE", 6.36, RED), ("BYBIT", 1.5, GRAY)], hero="4X BIGGER", sub="LARGEST HEIST. EVER."),
    dict(vo="The F B I blames TraderTraitor. A North Korean hacking unit linked to Lazarus Group. Pyongyang calls it absurd rhetoric.",
         lines=[("FBI SAYS:", GRAY)], hero="TRADERTRAITOR", sub="NORTH KOREAN HACKING UNIT", stamp="PYONGYANG DENIES"),
    dict(vo="How did they get in? They didn't break crypto. They broke a person. A fake job interview, and one infected laptop.",
         lines=[("THEY DIDN'T", WHITE), ("BREAK CRYPTO.", WHITE)], hero="THEY BROKE A PERSON", chips=["FAKE RECRUITER", "FAKE JOB TEST", "INFECTED LAPTOP"]),
    dict(vo="From there, they hijacked a hot wallet using an Ethereum feature called E I P 7702.",
         lines=[("HOT WALLET", WHITE)], hero="EIP-7702", sub="HIJACKED VIA DELEGATION"),
    dict(vo="Binance says users won't lose a cent. It's refilling the funds from its own treasury. Traders still pulled billions out anyway.",
         lines=[("USERS WON'T", GREEN), ("LOSE A CENT", GREEN)], sub="BINANCE REFILLING 90%+", chip="NET OUTFLOW: ~$4.7B"),
    dict(vo="North Korea has now stolen nearly thirteen billion dollars in crypto since 2017. Most of it, this year.",
         lines=[("STOLEN SINCE 2017", GRAY)], hero="$12.8B", sub="NORTH KOREA'S CRYPTO HAUL"),
    dict(vo="Follow for the intel nobody else will give you.",
         lines=[("FOLLOW FOR", WHITE), ("CRYPTO INTEL", RED)], sources=True),
]


def sh(cmd):
    subprocess.run(cmd, check=True, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# --- audio -----------------------------------------------------------------
def read_wav(path):
    with wave.open(path, "rb") as w:
        assert w.getframerate() == SR and w.getnchannels() == 1
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0


def build_audio(vo_files, starts, durs, total):
    n = int(total * SR)
    vo = np.zeros(n)
    for f, s in zip(vo_files, starts):
        x = read_wav(f)
        i = int((s + LEAD) * SR)
        vo[i:i + len(x)] += x
    t = np.arange(n) / SR
    lfo = 1 + 0.35 * np.sin(2 * np.pi * 0.06 * t)
    drone = (np.sin(2 * np.pi * 55 * t) + 0.7 * np.sin(2 * np.pi * 58.3 * t)) * lfo
    beat = 0.6
    ph = t % beat
    pulse = np.exp(-ph * 9) * np.sin(2 * np.pi * 52 * ph)
    bed = drone * 0.5 + pulse * 1.1
    env = np.abs(vo)
    env = np.convolve(env, np.ones(9600) / 9600, mode="same")
    bed *= 1 - 0.6 * np.clip(env * 9, 0, 1)
    fade_in, fade_out = int(1.0 * SR), int(1.8 * SR)
    bed[:fade_in] *= np.linspace(0, 1, fade_in)
    bed[-fade_out:] *= np.linspace(1, 0, fade_out)
    mix = vo + 0.14 * bed
    mix *= 0.95 / max(1e-9, np.abs(mix).max())
    pcm = (mix * 32767).astype(np.int16)
    path = os.path.join(ROOT, "final_audio.wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


# --- visuals ---------------------------------------------------------------
def make_fonts():
    src = os.path.join(ROOT, "Montserrat.ttf")
    xb, md = os.path.join(ROOT, "Montserrat-XB.ttf"), os.path.join(ROOT, "Montserrat-MD.ttf")
    instantiateVariableFont(TTFont(src), {"wght": 800}).save(xb)
    instantiateVariableFont(TTFont(src), {"wght": 500}).save(md)

    class F:
        def __init__(self):
            self.cache = {}

        def xb(self, s):
            return self.cache.setdefault(("xb", s), ImageFont.truetype(xb, s))

        def md(self, s):
            return self.cache.setdefault(("md", s), ImageFont.truetype(md, s))

        def fit(self, text, max_w, size):
            while size > 20 and self.xb(size).getlength(text) > max_w:
                size -= 4
            return self.xb(size)

    return F()


def make_static():
    y = np.linspace(0, 1, H)[:, None]
    grad = (np.array([5, 7, 13]) * (1 - y) + np.array([10, 14, 30]) * y)
    base = np.repeat(grad[:, :, None] * 0 + grad[:, None, :], W, axis=1).astype(np.uint8)
    base = Image.fromarray(np.broadcast_to(grad[:, None, :], (H, W, 3)).astype(np.uint8))
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(grid)
    step = 90
    for x in range(-H, W + H, step):
        d.line([(x, H), (x + H, 0)], fill=(120, 140, 220, 22), width=2)
    for yy in range(0, H, step):
        d.line([(0, yy), (W, yy)], fill=(120, 140, 220, 14), width=1)
    vig = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(vig)
    dv.ellipse([-W * 0.35, -H * 0.25, W * 1.35, H * 1.25], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(180))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return base, grid, vig, dark


def pop(t, t0, dur=0.38):
    if t < t0:
        return 0.0
    return 1 - (1 - min(1.0, (t - t0) / dur)) ** 3


def words(img, d, text, font, color, cx, y, t, t0, stagger=0.07):
    ws = text.split()
    space = font.getlength(" ")
    widths = [font.getlength(w) for w in ws]
    total = sum(widths) + space * (len(ws) - 1)
    x = cx - total / 2
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    for i, (w, ww) in enumerate(zip(ws, widths)):
        a = pop(t, t0 + i * stagger)
        if a <= 0:
            x += ww + space
            continue
        dy = (1 - a) * 55
        dl.text((x, y + dy), w, font=font, fill=color + (int(255 * a),))
        x += ww + space
    img.alpha_composite(layer)


def tile_text(img, text, font, color, cx, cy, scale, alpha=255):
    if scale <= 0.02 or alpha <= 2:
        return
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tile = Image.new("RGBA", (tw + 40, th + 40), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((20 - bbox[0], 20 - bbox[1]), text, font=font, fill=color + (255,))
    tw2, th2 = int(tile.width * scale), int(tile.height * scale)
    tile = tile.resize((max(1, tw2), max(1, th2)), Image.LANCZOS)
    tile.putalpha(tile.getchannel("A").point(lambda a: a * alpha // 255))
    img.alpha_composite(tile, (int(cx - tw2 / 2), int(cy - th2 / 2)))


def chip(img, d, text, cx, cy, t, t0, font, fg=WHITE, bg=RED):
    a = pop(t, t0)
    if a <= 0:
        return
    tw = font.getlength(text)
    pad = 26
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dl = ImageDraw.Draw(layer)
    dl.rounded_rectangle([cx - tw / 2 - pad, cy - 34 - (1 - a) * 30, cx + tw / 2 + pad, cy + 34],
                         radius=34, fill=bg + (int(230 * a),))
    dl.text((cx, cy - 2), text, font=font, fill=fg + (int(255 * a),), anchor="mm")
    img.alpha_composite(layer)


def breaking_bar(img, t):
    on = (math.sin(t * 7) > -0.2)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    bx, by = 70, 150
    f = FONTS.xb(46)
    tw = f.getlength("BREAKING")
    d.rounded_rectangle([bx, by, bx + tw + 130, by + 76], radius=14, fill=RED + (235,))
    d.text((bx + 32, by + 38), "BREAKING", font=f, fill=WHITE + (255,), anchor="lm")
    if on:
        d.ellipse([bx + tw + 58, by + 26, bx + tw + 96, by + 64], fill=WHITE + (255,))
    img.alpha_composite(layer)


def progress(img, frac):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([0, H - 14, W, H], radius=0, fill=(255, 255, 255, 28))
    d.rounded_rectangle([0, H - 14, int(W * frac), H], radius=0, fill=RED + (255,))
    img.alpha_composite(layer)


def scene_bg(img, t):
    img.paste(BASE)
    off = int((t * 22) % 90)
    img.alpha_composite(GRID, (-off, off))
    sweep = Image.new("RGBA", img.size, (0, 0, 0, 0))
    y = int((t * 140) % (H + 300)) - 150
    ImageDraw.Draw(sweep).rectangle([0, y, W, y + 90], fill=(90, 120, 255, 14))
    img.alpha_composite(sweep)
    img.paste(DARK, (0, 0), VIG)


def render_scene(img, idx, tt, dur):
    d = ImageDraw.Draw(img)
    s = SCENES[idx]
    hero_font = FONTS.fit(s.get("hero", "X") or "X", W - 140, 190) if s.get("hero") else None
    y0 = 620

    if "lines" in s:
        lf = FONTS.fit(" ".join(w for w, _ in s["lines"]), W - 120, 132)
        for i, (line, col) in enumerate(s["lines"]):
            words(img, d, line, FONTS.xb(120), col, W // 2, y0 + i * 165, tt, 0.15 + i * 0.12)
        y0 += len(s["lines"]) * 165 + 40
    if "bars" in s:
        bf = FONTS.xb(56)
        for i, (name, val, col) in enumerate(s["bars"]):
            yy = y0 + i * 210
            a = pop(tt, 0.3 + i * 0.35)
            bar_w = (W - 200) * a * (val / 6.36)
            d.rounded_rectangle([100, yy, 100 + (W - 200), yy + 74], radius=18, fill=(255, 255, 255, 26))
            if bar_w > 18:
                d.rounded_rectangle([100, yy, 100 + bar_w, yy + 74], radius=18, fill=col + (255,))
            d.text((100, yy - 14), name, font=bf, fill=WHITE + (int(255 * a),), anchor="lb")
            d.text((100 + W - 220, yy - 14), f"${val}B", font=bf, fill=col + (int(255 * a),), anchor="rb")
        y0 += len(s["bars"]) * 210 + 30
    if "chips" in s:
        cf = FONTS.xb(40)
        for i, c in enumerate(s["chips"]):
            chip(img, d, c, W // 2, y0 + 90 + i * 110, tt, 0.9 + i * 0.55, cf, bg=RED if i == 2 else (40, 48, 70))
        y0 += len(s["chips"]) * 110 + 60
    if s.get("hero"):
        a = pop(tt, 1.15)
        tile_text(img, s["hero"], hero_font, RED if s["hero"].startswith("$") or s["hero"].startswith("TRADER") or s["hero"].startswith("EIP") else WHITE,
                  W // 2, y0 + 150, 0.92 + 0.08 * a, alpha=int(255 * a))
        y0 += 300
    if s.get("sub"):
        words(img, d, s["sub"], FONTS.xb(64), AMBER, W // 2, y0 + 60, tt, 2.0)
        y0 += 140
    if s.get("chip"):
        chip(img, d, s["chip"], W // 2, y0 + 90, tt, 2.5, FONTS.xb(44), bg=(40, 48, 70))
    if s.get("stamp"):
        chip(img, d, s["stamp"], W // 2, y0 + 90, tt, 2.4, FONTS.xb(44), fg=WHITE, bg=(70, 40, 40))
    if s.get("sources"):
        sf = FONTS.xb(34)
        d.text((W // 2, y0 + 90), "SOURCES: REUTERS · AP · TRM LABS · BBC", font=sf, fill=GRAY + (int(255 * pop(tt, 0.8)),), anchor="mm")


def main():
    global FONTS, BASE, GRID, VIG, DARK
    FONTS = make_fonts()
    BASE, GRID, VIG, DARK = make_static()

    vo_files, durs = [], []
    for i, s in enumerate(SCENES):
        mp3 = os.path.join(ROOT, f"vo_{i}.mp3")
        wav = os.path.join(ROOT, f"vo_{i}.wav")
        sh(["venv/bin/edge-tts", "--voice", VOICE, f"--rate={RATE}", "--text", s["vo"], "--write-media", mp3])
        sh(["ffmpeg", "-y", "-i", mp3, "-ar", str(SR), "-ac", "1", wav])
        vo_files.append(wav)
        with wave.open(wav, "rb") as w:
            durs.append(w.getnframes() / SR)

    starts, total = [], 0.0
    for d in durs:
        starts.append(total)
        total += LEAD + d + TAIL
    print(f"total duration {total:.2f}s")

    audio = build_audio(vo_files, starts, durs, total)

    fdir = os.path.join(ROOT, "frames")
    os.makedirs(fdir, exist_ok=True)
    nframes = int(total * FPS)
    for n in range(nframes):
        t = n / FPS
        idx = max(i for i, s in enumerate(starts) if s <= t)
        img = Image.new("RGB", (W, H))
        scene_bg(img, t)
        breaking_bar(img, t)
        render_scene(img, idx, t - starts[idx], durs[idx] + LEAD + TAIL)
        progress(img, t / total)
        img.convert("RGB").save(os.path.join(fdir, f"f{n:05d}.jpg"), quality=90)

    out = os.path.join(ROOT, "binance_hack_short.mp4")
    sh(["ffmpeg", "-y", "-framerate", str(FPS), "-i", os.path.join(fdir, "f%05d.jpg"),
        "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", "-r", str(FPS), out])
    for f in os.listdir(fdir):
        os.remove(os.path.join(fdir, f))
    os.rmdir(fdir)
    print("wrote", out, os.path.getsize(out) / 1e6, "MB")


if __name__ == "__main__":
    main()

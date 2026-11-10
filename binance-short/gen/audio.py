"""Procedural soundtrack + sound design (dark techno bed, synced to scene cuts)."""
import math
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 48000
BPM = 100.0
BEAT = 60.0 / BPM


def _filt(x, c, kind, order=2):
    ny = SR / 2
    if kind == "band":
        hi = min(c[1], ny * 0.98)
        b, a = butter(order, [max(20, c[0]) / ny, hi / ny], btype="band")
    else:
        b, a = butter(order, min(c, ny * 0.98) / ny, kind)
    return lfilter(b, a, x)


def _env_exp(n, rate):
    return np.exp(-np.arange(n) / SR * rate)


def build(dur, out_path, log=print):
    N = int(dur * SR)
    mus = np.zeros((2, N))

    def put(sig, t, g=1.0, pan=0.0):
        i = int(t * SR)
        if i >= N:
            return
        n = min(len(sig), N - i)
        th = (pan + 1) * math.pi / 4
        mus[0][i : i + n] += sig[:n] * g * math.cos(th)
        mus[1][i : i + n] += sig[:n] * g * math.sin(th)

    rng = np.random.default_rng(7)

    def noise(n):
        return rng.standard_normal(n)

    def kick():
        n = int(0.30 * SR)
        t = np.arange(n) / SR
        f = 42 + 115 * np.exp(-t * 26)
        s = np.sin(np.cumsum(2 * np.pi * f / SR)) * _env_exp(n, 16)
        s += _filt(noise(n), 2800, "low") * _env_exp(n, 80) * 0.7
        return np.tanh(s * 1.8)

    def hat(open_=False):
        n = int((0.14 if open_ else 0.045) * SR)
        return _filt(noise(n), 8200, "high") * _env_exp(n, 28 if open_ else 170) * 0.8

    def snare():
        n = int(0.24 * SR)
        t = np.arange(n) / SR
        x = _filt(noise(n), (1600, 7200), "band") * _env_exp(n, 22)
        x += np.sin(2 * np.pi * 186 * t) * _env_exp(n, 30) * 0.7
        return np.tanh(x * 1.5)

    def bass(f, dur):
        n = int(dur * SR)
        t = np.arange(n) / SR
        s = 0.5 * ((f * t) % 1 * 2 - 1) + 0.5 * ((f * 1.007 * t) % 1 * 2 - 1)
        s += 0.7 * np.sin(2 * np.pi * f * t)
        e = np.minimum(1, t / 0.004) * np.exp(-np.maximum(0, t - dur * 0.7) * 18)
        return _filt(np.tanh(s * 1.3) * e, 520, "low")

    def pluck(f, dur=0.30):
        n = int(dur * SR)
        t = np.arange(n) / SR
        s = 0.55 * np.sign(np.sin(2 * np.pi * f * t)) + 0.45 * (
            4 * np.abs(((f * t) % 1) - 0.5) - 1
        )
        return _filt(s * _env_exp(n, 11), (500, 5200), "band")

    def pad(freqs, dur, bright=900):
        n = int(dur * SR)
        t = np.arange(n) / SR
        s = np.zeros(n)
        for f in freqs:
            for det in (0.996, 1.004):
                s += ((f * det * t) % 1) * 2 - 1
        s = _filt(np.tanh(s / max(1, len(freqs)) * 1.2), bright, "low")
        a = np.minimum(1, t / 0.9)
        r = np.minimum(1, np.maximum(0, dur - t) / 0.6)
        return s * a * r * 0.35

    def riser(dur, f0=220, f1=1500):
        n = int(dur * SR)
        t = np.arange(n) / SR
        f = f0 + (f1 - f0) * (t / dur) ** 2
        s = np.sin(np.cumsum(2 * np.pi * f / SR)) * 0.5
        s += _filt(noise(n), (300, 6000), "band") * 0.8
        return s * (t / dur) ** 1.8 * 0.5

    def impact():
        n = int(1.0 * SR)
        t = np.arange(n) / SR
        s = np.sin(np.cumsum(2 * np.pi * (46 + 30 * np.exp(-t * 12)) / SR)) * _env_exp(n, 6)
        s += _filt(noise(n), 380, "low") * _env_exp(n, 10) * 0.9
        return np.tanh(s * 1.6)

    def beeps(f=920, reps=3):
        out = np.zeros(int(reps * 0.24 * SR) + int(0.12 * SR))
        for k in range(reps):
            i = int(k * 0.24 * SR)
            n = int(0.09 * SR)
            t = np.arange(n) / SR
            out[i : i + n] += (
                np.sign(np.sin(2 * np.pi * f * t)) * 0.4 * np.minimum(1, t / 0.005)
            )
        return out

    def coin():
        n = int(0.09 * SR)
        t = np.arange(n) / SR
        f = 1700 + rng.uniform(-250, 350)
        return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 1.53 * t)) * _env_exp(n, 55)

    def click():
        n = int(0.022 * SR)
        return _filt(noise(n), 4600, "high") * _env_exp(n, 260)

    def zap():
        n = int(0.16 * SR)
        t = np.arange(n) / SR
        f = 2400 * np.exp(-t * 26) + 120
        return np.tanh(np.sign(np.sin(np.cumsum(2 * np.pi * f / SR))) * _env_exp(n, 22) * 1.5)

    def shatter():
        n = int(0.6 * SR)
        x = _filt(noise(n), (2400, 9000), "band") * _env_exp(n, 12)
        for k, f in enumerate((3800, 2900, 2100)):
            i = int(k * 0.09 * SR)
            m = int(0.12 * SR)
            t = np.arange(m) / SR
            x[i : i + m] += np.sin(2 * np.pi * f * t) * _env_exp(m, 34) * 0.5
        return x * 0.8

    def sting():
        n = int(1.6 * SR)
        t = np.arange(n) / SR
        s = np.zeros(n)
        for f in (130.8, 155.6, 196.0, 261.6, 311.1):
            s += ((f * t) % 1) * 2 - 1
        s = _filt(np.tanh(s / 5 * 1.5), 2200, "low") * np.exp(-t * 3.2)
        s += _filt(noise(n), 6000, "high") * np.exp(-t * 2.0) * 0.12
        return np.tanh(s * 1.4)

    def glitchb(seed):
        r = np.random.default_rng(seed)
        out = np.zeros(int(0.30 * SR))
        for _ in range(9):
            i = int(r.uniform(0, 0.2) * SR)
            m = int(r.uniform(0.015, 0.05) * SR)
            f = r.uniform(300, 3200)
            t = np.arange(m) / SR
            out[i : i + m] += np.sign(np.sin(2 * np.pi * f * t)) * r.uniform(0.3, 0.8)
        return out

    B = BEAT
    C2, Ab1, Bb1, Eb2 = 65.41, 51.91, 58.27, 77.78
    Cm = [130.81, 155.56, 196.00]
    Ab = [103.83, 130.81, 155.56]
    Eb = [155.56, 196.00, 233.08]
    Bb = [116.54, 146.83, 174.61]
    ARP = [261.63, 311.13, 392.00, 466.16, 523.25, 466.16, 392.00, 311.13]

    kicks = []
    t = 4.2
    while t < 33.8 - 1e-6:
        kicks.append(t)
        t += B
    t = 41.4
    while t < 46.9:
        kicks.append(t)
        t += B
    heart = [34.6, 35.8, 37.0, 38.2]
    for kt in kicks:
        put(kick(), kt, 0.9)
    for kt in heart:
        put(kick(), kt, 0.5)

    t = 4.8
    while t < 33.2:
        put(snare(), t, 0.75)
        t += 2 * B
    t = 42.6
    while t < 47.0:
        put(snare(), t, 0.7)
        t += 2 * B

    t = 10.6
    while t < 33.6:
        put(hat(), t, 0.32)
        if 19.2 <= t < 27.2:
            put(hat(), t + B / 4, 0.18)
        t += B / 2
    t = 41.4
    while t < 47.0:
        put(hat(), t, 0.3)
        t += B / 2

    bassbuf = np.zeros(N)
    arpbuf = np.zeros(N)
    padbuf = np.zeros(N)

    def pm(arr, sig, t0):
        i = int(t0 * SR)
        if i >= N:
            return
        n = min(len(sig), N - i)
        arr[i : i + n] += sig[:n]

    def bassline(t0, t1, notes, step, dur=None):
        t = t0
        i = 0
        while t < t1 - 1e-6:
            pm(bassbuf, bass(notes[i % len(notes)], dur or step * 0.92), t)
            t += step
            i += 1

    bassline(4.2, 19.2, [C2], B / 2)
    bassline(19.2, 27.2, [C2, C2, Bb1, G1 := 49.00], B / 2)
    bassline(27.2, 33.8, [C2, Ab1, Eb2, Bb1], B)
    bassline(41.4, 47.0, [C2, C2, Ab1, Bb1], B / 2)

    pm(padbuf, pad(Cm, 6.0), 5.0)
    pm(padbuf, pad(Cm, 4.6), 11.0)
    pm(padbuf, pad(Cm, 4.2), 19.2)
    pm(padbuf, pad(Bb, 4.0), 23.4)
    for t0, ch in ((27.2, Cm), (28.85, Ab), (30.5, Eb), (32.15, Bb)):
        pm(padbuf, pad(ch, 1.75), t0)
    pm(padbuf, pad(Cm, 3.8), 33.8)
    pm(padbuf, pad(Ab, 3.8), 37.6)
    pm(padbuf, pad(Cm, 2.9), 41.4)
    pm(padbuf, pad(Ab, 2.9), 44.3)

    def arpline(t0, t1, g, step=B / 4):
        t = t0
        i = 0
        while t < t1 - 1e-6:
            f = ARP[i % len(ARP)]
            pm(arpbuf, pluck(f), t)
            pm(arpbuf, pluck(f) * 0.35, t + 0.19)
            t += step
            i += 1

    arpline(10.6, 19.2, 0.3)
    arpline(19.2, 27.2, 0.45)
    arpline(27.2, 33.8, 0.3)
    arpline(41.4, 47.0, 0.4)

    # SFX / transitions
    for gt, g in ((0.28, 0.8), (1.05, 0.6), (1.92, 0.7), (3.86, 1.0)):
        put(glitchb(int(gt * 100)), gt, g)
    put(riser(1.5), 2.7, 0.55)
    put(riser(1.6), 9.0, 0.4)
    put(riser(1.7), 17.5, 0.5)
    put(riser(1.6), 39.8, 0.45)
    for it in (4.2, 10.6, 19.2, 27.2, 33.8, 41.4):
        put(impact(), it, 0.9)
    put(beeps(), 4.32, 0.5)
    tt = 10.8
    while tt < 17.2:
        put(click(), tt, 0.16)
        tt += 0.21
    put(zap(), 17.0, 0.7)
    put(zap(), 17.28, 0.5)
    r2 = np.random.default_rng(5)
    for _ in range(16):
        put(coin(), r2.uniform(20.2, 26.4), 0.22)
    put(shatter(), 34.0, 0.8)
    put(sting(), 41.5, 0.85)

    # intro drone
    put(pad([C2 / 2], 4.6, bright=420), 0.0, 0.8)
    n = int(4.6 * SR)
    tarr = np.arange(n) / SR
    sub = np.sin(2 * np.pi * 32.7 * tarr) * np.minimum(1, tarr / 0.5) * np.minimum(1, (4.4 - tarr) / 0.4)
    put(sub * 0.4, 0.0, 1.0)

    duck = np.zeros(N)
    for kt in kicks + heart:
        i = int(kt * SR)
        n = min(int(0.42 * SR), N - i)
        if n > 0:
            duck[i : i + n] += _env_exp(n, 9)
    duck = 1.0 - 0.55 * np.clip(duck, 0, 1)
    bassbuf *= duck
    arpbuf *= duck
    padbuf *= duck
    put(bassbuf, 0.0, 0.95, 0.0)
    put(arpbuf, 0.0, 0.75, 0.25)
    put(padbuf, 0.0, 0.85, -0.2)

    mus[0] = np.clip(mus[0], -4, 4)
    mus[1] = np.clip(mus[1], -4, 4)
    fi = int(0.08 * SR)
    mus[:, :fi] *= np.linspace(0, 1, fi)
    fo = int(1.8 * SR)
    mus[:, -fo:] *= np.linspace(1, 0, fo) ** 1.5
    x = np.tanh(mus * 1.15)
    x /= max(1e-9, np.abs(x).max())
    x *= 0.92
    data = (x.T * 32767).astype("<i2")
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(data.tobytes())
    log(f"audio written: {out_path} ({dur}s)")


if __name__ == "__main__":
    import sys

    build(48.0, sys.argv[1] if len(sys.argv) > 1 else "out/audio.wav")

"""CLI: preview stills or full MP4 render."""
import argparse
import os
import subprocess
import time

from PIL import Image

from . import audio as A
from . import core as C
from . import scenes as S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", default="")
    ap.add_argument("--scale", type=float, default=0.5)
    ap.add_argument("--render", default="")
    ap.add_argument("--audio-only", action="store_true")
    args = ap.parse_args()
    outdir = os.path.join(C.ROOT, "out")
    os.makedirs(outdir, exist_ok=True)
    if args.audio_only:
        A.build(C.DUR, os.path.join(outdir, "audio.wav"))
        return
    if args.stills:
        for ts in args.stills.split(","):
            t = float(ts)
            idx = int(round(t * C.FPS))
            t0 = time.time()
            img = S.frame(idx)
            dt = (time.time() - t0) * 1000
            if args.scale != 1.0:
                img = img.resize((int(C.W * args.scale), int(C.H * args.scale)),
                                 Image.Resampling.BILINEAR)
            p = os.path.join(outdir, "still_%04.1f.png" % t)
            img.save(p)
            print("t=%.1f  %5.0f ms/frame  %s" % (t, dt, p))
        return
    wav = os.path.join(outdir, "audio.wav")
    if not os.path.exists(wav):
        A.build(C.DUR, wav)
    out = args.render or os.path.join(outdir, "binance_short.mp4")
    n = int(C.DUR * C.FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (C.W, C.H), "-r", str(C.FPS), "-i", "pipe:0", "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "160k", "-shortest", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(n):
        proc.stdin.write(S.frame(i).tobytes())
        if i % 300 == 0:
            print("frame %d/%d  %.0fs" % (i, n, time.time() - t0), flush=True)
    proc.stdin.close()
    proc.wait()
    print("done: %s (%.1f MB, %.0fs)" % (out, os.path.getsize(out) / 1e6, time.time() - t0))


if __name__ == "__main__":
    main()

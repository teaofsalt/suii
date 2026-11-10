# Binance $6.3B Heist - Motion-Graphics YouTube Short

Fully procedural 1080x1920 / 30fps / 48s faceless news-explainer short about the
October 29, 2026 Binance breach (FBI attribution: TraderTraitor / Lazarus, DPRK).

- `gen/core.py` - theme, fonts, easing, image fx (grain, vignette, glitch)
- `gen/art.py` - hacker character, server-room environment, globe, vault props
- `gen/scenes.py` - seven scenes, timeline, transitions
- `gen/audio.py` - procedural soundtrack + sound design (numpy/scipy)
- `gen/render.py` - CLI for preview stills and the final MP4

## Setup

```bash
uv venv .venv && uv pip install --python .venv/bin/python pillow numpy scipy
mkdir -p fonts && cd fonts
curl -sL -O https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf
curl -sL -O https://raw.githubusercontent.com/google/fonts/main/ofl/bebasneue/BebasNeue-Regular.ttf
```

## Run

```bash
.venv/bin/python -m gen.render --stills 2,7,14,23,30,37,45   # preview frames
.venv/bin/python -m gen.render --audio-only                  # soundtrack
.venv/bin/python -m gen.render --render out/binance_short.mp4
```

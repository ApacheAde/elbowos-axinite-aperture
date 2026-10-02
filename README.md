# Axinite Aperture

Full-colour Python 3 neon iris arcade for [ElbowOS](https://x.com/ElbowOS).

Apricot motes dive at a crystal lens. Open the aperture to swallow them. Snap it shut so crimson shards shatter on the blades instead of scorching the core.

Not a Nintendo ROM, not an emulator, and not a clone of the pipe, crane, word-catch, or light-cycle packs.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 axinite_aperture.py --play
```

- Right / D / Up — open the iris
- Left / A / Down — close the iris
- Space — snap shut
- R — restart

## Record a 9:16 reel

```bash
python3 axinite_aperture.py --record
```

Writes a 15 second 1080x1920 h264 MP4 (dummy SDL driver, ffmpeg libx264 yuv420p CRF 20, +faststart).

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1c09puEmDPERzRb03VEwNgQXeWDu4vqJE/view?usp=drivesdk

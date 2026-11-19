"""Scene images: free SVG illustrations, your own photos, or AI images from fal.ai.

Every provider writes one PNG per shot at OUT_W x OUT_H (the 1080x1920 frame
plus headroom for camera moves) into build/images/<id>.png.
"""
import json
import os
import subprocess
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
HEADROOM = 1.2
OUT_W, OUT_H = int(1080 * HEADROOM), int(1920 * HEADROOM)

# Rough USD per image, used only for the pre-run estimate. Check fal.ai/pricing.
FAL_MODELS = {
    "fal-ai/flux/schnell": 0.003,
    "fal-ai/flux/dev": 0.025,
    "fal-ai/nano-banana": 0.039,
}


def render_svg(story_dir: Path, shots, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    todo = []
    for s in shots:
        src = story_dir / s["svg"]
        dst = out_dir / f"{s['id']}.png"
        if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
            todo.append((src, dst))
    defs = story_dir / "scenes" / "_defs.svg"
    defs_arg = str(defs) if defs.exists() else "-"
    if todo:
        # svg2png names output after the svg; render to a temp dir then rename to <id>.png
        tmp = out_dir / ".svg"
        subprocess.run(
            ["node", str(ROOT / "tools" / "svg2png.mjs"), str(tmp), str(HEADROOM), defs_arg]
            + [str(src) for src, _ in todo],
            check=True, stdout=subprocess.DEVNULL,
        )
        for src, dst in todo:
            (tmp / (src.stem + ".png")).replace(dst)
    return {s["id"]: out_dir / f"{s['id']}.png" for s in shots}


def fit_frame(im, shot):
    """Fit a photo or video frame to the OUT_W x OUT_H canvas (see render_photo for keys)."""
    if shot.get("fit", "cover") == "contain":
        bg = ImageOps.fit(im, (OUT_W, OUT_H), Image.LANCZOS)
        bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(60))).enhance(0.85)
        fg = ImageOps.contain(im, (OUT_W, OUT_H), Image.LANCZOS)
        bg.paste(fg, ((OUT_W - fg.width) // 2, (OUT_H - fg.height) // 2))
        return bg
    return ImageOps.fit(im, (OUT_W, OUT_H), Image.LANCZOS, centering=tuple(shot.get("focus", (0.5, 0.5))))


def render_photo(story_dir: Path, shots, out_dir: Path):
    """Real photos (JPG/PNG/WebP) as shots. Per-shot keys:
      photo   path relative to the story folder, e.g. "photos/01-bottle.jpg"
      fit     "cover" (default): crop to fill 9:16
              "contain": whole photo on a blurred copy of itself (for wide shots)
      focus   [x, y] crop centre as image fractions for "cover", default [0.5, 0.5]
    Phone EXIF rotation is applied, so portrait photos stay upright."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for s in shots:
        src = story_dir / s["photo"]
        dst = out_dir / f"{s['id']}.png"
        paths[s["id"]] = dst
        if dst.exists() and dst.stat().st_mtime >= max(src.stat().st_mtime, Path(__file__).stat().st_mtime):
            continue
        fit_frame(ImageOps.exif_transpose(Image.open(src)).convert("RGB"), s).save(dst)
    return paths


def render_clip(story_dir: Path, shot, length, out_dir: Path, fps=30):
    """Real video clip as a shot: decodes `length` seconds from shot["clip_start"] (default 0)
    into fitted JPG frames in out_dir/<id>/. Same "fit"/"focus" keys as photos; phone
    rotation is applied by FFmpeg. Returns (frame_dir, frame_count)."""
    src = story_dir / shot["clip"]
    d = out_dir / shot["id"]
    key = json.dumps({"src": str(src), "mtime": src.stat().st_mtime, "start": shot.get("clip_start", 0),
                      "len": round(length, 3), "fit": shot.get("fit"), "focus": shot.get("focus"),
                      "code": Path(__file__).stat().st_mtime, "fps": fps})
    meta = d / "meta.json"
    if meta.exists() and json.loads(meta.read_text()).get("key") == key:
        return d, json.loads(meta.read_text())["n"]
    if d.exists():
        for f in d.iterdir():
            f.unlink()
    d.mkdir(parents=True, exist_ok=True)
    long_side = 2400  # enough for the 1.2x headroom canvas, keeps 4K phone clips fast
    scale = (f"scale='if(gt(iw,ih),min(iw,{long_side}),-2)':'if(gt(iw,ih),-2,min(ih,{long_side}))'")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(shot.get("clip_start", 0)),
                    "-t", f"{length + 0.1:.3f}", "-i", str(src), "-vf", f"fps={fps},{scale}",
                    "-q:v", "2", str(d / "raw%05d.jpg")], check=True)
    raws = sorted(d.glob("raw*.jpg"))
    if not raws:
        raise SystemExit(f"clip {src} gave no frames (check clip_start)")
    for k, f in enumerate(raws):
        fit_frame(Image.open(f).convert("RGB"), shot).save(d / f"{k:05d}.jpg", quality=92)
        f.unlink()
    meta.write_text(json.dumps({"key": key, "n": len(raws)}))
    if len(raws) < length * fps - 1:
        print(f"   WARNING: clip {shot['clip']} is {len(raws) / fps:.1f}s but the shot is {length:.1f}s; "
              f"the last frame is held")
    return d, len(raws)


def clip_audio(story_dir: Path, shot, length, sr):
    """The clip's own sound (mono float) for the shot, or None if the clip has no audio."""
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(shot.get("clip_start", 0)),
                        "-t", f"{length:.3f}", "-i", str(story_dir / shot["clip"]), "-vn",
                        "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        return None
    import numpy as np
    return np.frombuffer(r.stdout, np.float32).astype(np.float64)


def fal_estimate(shots, model):
    return len(shots) * FAL_MODELS.get(model, 0.05)


def render_fal(story, shots, out_dir: Path, model="fal-ai/flux/dev"):
    """Text-to-image through fal.ai's synchronous endpoint. Needs FAL_KEY (or a
    network secret that injects the Authorization header for fal.run)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    key = os.environ.get("FAL_KEY", "proxy-injected")
    style = story.get("style", "")
    paths = {}
    for s in shots:
        dst = out_dir / f"{s['id']}.png"
        paths[s["id"]] = dst
        if dst.exists():
            continue
        body = {"prompt": f"{s['prompt']}. {style}", "num_images": 1}
        if "nano-banana" in model:
            body["aspect_ratio"] = "9:16"
        else:
            body["image_size"] = {"width": 1080, "height": 1920}
        req = urllib.request.Request(
            f"https://fal.run/{model}",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Key {key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=300) as r:
            url = json.load(r)["images"][0]["url"]
        raw = out_dir / f"{s['id']}.raw"
        urllib.request.urlretrieve(url, raw)
        ImageOps.fit(Image.open(raw).convert("RGB"), (OUT_W, OUT_H), Image.LANCZOS).save(dst)
        raw.unlink()
        print(f"  image {s['id']} done")
    return paths

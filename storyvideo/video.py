"""Timeline, word-by-word captions and frame rendering (camera moves, grain, vignette)."""
import math
import re
import subprocess
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
FONT = ROOT / "assets" / "fonts" / "poppins-latin-800-normal.woff"
CAPTION_Y = 1200        # vertical centre of the caption
HIGHLIGHT = (255, 214, 64)

# ----------------------------------------------------------------- captions
def chunk_words(text, max_words=3, max_chars=16):
    """Split narration into 1-3 word chunks; returns list of lists of (word, weight)."""
    words = text.split()
    chunks, cur = [], []
    for w in words:
        clean = re.sub(r"[^\w'€$%-]", "", w)
        weight = len(clean) + 2
        if w[-1] in ".!?":
            weight += 7
        elif w[-1] in ",;:":
            weight += 4
        if cur and (len(cur) >= max_words or sum(len(x) for x, _ in cur) + len(w) > max_chars):
            chunks.append(cur)
            cur = []
        cur.append((w, weight))
        if w[-1] in ".!?,;:":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def caption_events(text, v_start, v_dur, end):
    """[(t0, t1, words, active_index)] with word timing proportional to word length."""
    chunks = chunk_words(text)
    weights = [w for c in chunks for _, w in c]
    total = sum(weights)
    times, acc = [], 0
    for w in weights:
        times.append(v_start + acc / total * v_dur)
        acc += w
    times.append(v_start + v_dur)
    events, k = [], 0
    for ci, c in enumerate(chunks):
        words = [re.sub(r"[.,;:]$", "", w) for w, _ in c]
        chunk_end = times[k + len(c)] if ci < len(chunks) - 1 else end
        for j in range(len(c)):
            t1 = times[k + j + 1] if j < len(c) - 1 else chunk_end
            events.append((times[k + j], t1, words, j, times[k]))
        k += len(c)
    return events


_font_cache = {}


def caption_image(words, active):
    key = (tuple(words), active)
    if key in _font_cache:
        return _font_cache[key]
    font = ImageFont.truetype(str(FONT), 96)
    space = 26
    sizes = [font.getbbox(w, stroke_width=12) for w in words]
    widths = [b[2] - b[0] for b in sizes]
    total_w = sum(widths) + space * (len(words) - 1)
    lines = [list(range(len(words)))]
    if total_w > W - 120 and len(words) > 1:
        lines = [list(range(len(words) - 1)), [len(words) - 1]]
    line_h = 130
    img = Image.new("RGBA", (W, line_h * len(lines) + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for li, idxs in enumerate(lines):
        lw = sum(widths[i] for i in idxs) + space * (len(idxs) - 1)
        x = (W - lw) / 2
        y = 30 + li * line_h
        for i in idxs:
            fill = HIGHLIGHT if i == active else (255, 255, 255)
            d.text((x - sizes[i][0], y), words[i], font=font, fill=fill,
                   stroke_width=12, stroke_fill=(10, 10, 14))
            x += widths[i] + space
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow.putalpha(img.getchannel("A").point(lambda a: a * 0.55).filter(ImageFilter.GaussianBlur(10)))
    out = Image.alpha_composite(shadow, img)
    _font_cache[key] = out
    return out


# ----------------------------------------------------------------- camera
MOTIONS = {
    #            z0    z1    (cx0, cy0)   (cx1, cy1)  -- centres as fraction of image
    "push_in":  (1.00, 1.16, (0.5, 0.5), (0.5, 0.48)),
    "pull_out": (1.16, 1.00, (0.5, 0.48), (0.5, 0.5)),
    "pan_right": (1.14, 1.14, (0.40, 0.5), (0.60, 0.5)),
    "pan_left": (1.14, 1.14, (0.60, 0.5), (0.40, 0.5)),
    "pan_down": (1.12, 1.12, (0.5, 0.42), (0.5, 0.58)),
    "pan_up":   (1.12, 1.12, (0.5, 0.58), (0.5, 0.42)),
    "still":    (1.04, 1.06, (0.5, 0.5), (0.5, 0.5)),
}


def _ease(p):
    return 0.5 - 0.5 * math.cos(math.pi * p) if p < 1 else 1.0


def camera_box(img_w, img_h, motion, p, since_cut):
    z0, z1, c0, c1 = MOTIONS.get(motion, MOTIONS["still"])
    e = 0.35 * p + 0.65 * _ease(p)
    z = z0 + (z1 - z0) * e
    # punch-in on every cut: start 5% tighter and settle in 0.3 s
    if since_cut < 0.3:
        k = 1 - since_cut / 0.3
        z *= 1 + 0.05 * k * k
    cx = (c0[0] + (c1[0] - c0[0]) * e) * img_w
    cy = (c0[1] + (c1[1] - c0[1]) * e) * img_h
    bw, bh = img_w / z, img_h / z
    cx = min(max(cx, bw / 2), img_w - bw / 2)
    cy = min(max(cy, bh / 2), img_h - bh / 2)
    return (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)


# ----------------------------------------------------------------- frames
_G = {}


def _init(plan):
    _G["plan"] = plan
    _G["imgs"] = {sid: Image.open(p).convert("RGB") for sid, p in plan["images"].items()}
    # vignette
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = (np.clip((r - 0.55) / 0.75, 0, 1) ** 1.6 * 200).astype(np.uint8)
    vig = np.zeros((H, W, 4), np.uint8)
    vig[..., 3] = a
    _G["vig"] = Image.fromarray(vig, "RGBA")
    # film grain
    rng = np.random.default_rng(1)
    grains = []
    for _ in range(6):
        g = rng.integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
        g = Image.fromarray(g, "L").resize((W, H), Image.BILINEAR)
        rgba = Image.merge("RGBA", (g, g, g, Image.new("L", (W, H), 11)))
        grains.append(rgba)
    _G["grain"] = grains


def _frame(i):
    plan = _G["plan"]
    t = i / FPS
    shots = plan["shots"]
    s = next((x for x in shots if x["start"] <= t < x["end"]), shots[-1])
    img = _G["imgs"][s["id"]]
    p = min(1.0, (t - s["start"]) / (s["end"] - s["start"]))
    box = camera_box(img.width, img.height, s["motion"], p, t - s["start"])
    frame = img.resize((W, H), Image.BILINEAR, box=box).convert("RGBA")
    frame.alpha_composite(_G["grain"][(i // 2) % len(_G["grain"])])
    frame.alpha_composite(_G["vig"])

    for t0, t1, words, active, chunk_t0 in plan["captions"]:
        if t0 <= t < t1:
            cap = caption_image(words, active)
            age = t - chunk_t0
            if age < 0.14:  # pop in with a little overshoot
                k = age / 0.14
                sc = 0.7 + 0.3 * (1 + 2.2 * (k - 1) ** 3 + 1.2 * (k - 1) ** 2)
                cw, ch = max(1, int(cap.width * sc)), max(1, int(cap.height * sc))
                cap = cap.resize((cw, ch), Image.BILINEAR)
            frame.alpha_composite(cap, (int((W - cap.width) / 2), int(CAPTION_Y - cap.height / 2)))
            break

    # fade in / out
    fade = min(1.0, t / 0.25, (plan["total"] - t) / 0.7)
    out = frame.convert("RGB")
    if fade < 1:
        out = Image.blend(Image.new("RGB", (W, H)), out, max(0.0, fade))
    return out.tobytes()


def render(plan, audio_path: Path, out_path: Path, workers=4):
    n = int(plan["total"] * FPS)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(audio_path),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-tune", "grain", "-pix_fmt", "yuv420p",
        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", "-movflags", "+faststart", str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers, initializer=_init, initargs=(plan,)) as pool:
        for k, data in enumerate(pool.imap(_frame, range(n), chunksize=6)):
            proc.stdin.write(data)
            if k % (FPS * 5) == 0:
                print(f"  frame {k}/{n}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")

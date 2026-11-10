"""Timeline, word-by-word captions, overlays and frame rendering.

Per-shot options (all optional) used by the renderer:
  motion      preset name (see MOTIONS) or {"z0","z1","c0":[x,y],"c1":[x,y]} (centres as image fractions)
  punch       false to disable the small punch-in at the cut
  fx          list of "sway", "flicker", "rain"
  rain_box    [x0, y0, x1, y1] frame pixels to limit the rain to (e.g. a window)
  flashes     [{"at": s, "peak": 0.6, "attack": 0, "decay": 0.35}] white lightning flashes (shot-relative)
  overlays    [{"text", "y", "size", "color", "start", "end", "pop", "type": "text|label"}]
  countdown   {"at": s, "from": 3, "step": 1.0, "x": 150, "y": 330}
  caption_y   vertical centre for captions in this shot
"""
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
EMOJI_FONT = Path("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf")
if (ROOT / "assets" / "fonts" / "NotoColorEmoji.ttf").exists():
    EMOJI_FONT = ROOT / "assets" / "fonts" / "NotoColorEmoji.ttf"
CAPTION_Y = 1200        # default vertical centre of the caption
HIGHLIGHT = (255, 214, 64)
INK = (10, 10, 14)

# Text layout: centre x and max width. Stories can narrow these to keep text out of
# platform UI (right 12% / bottom 20%) via "text_cx" / "text_max_w".
LAYOUT = {"cx": W / 2, "max_w": W - 120}


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


def _snap_to_pauses(rel_times, samples, sr, window=0.12, min_word=0.07):
    """Move each internal word boundary to the quietest 10 ms frame nearby.

    rel_times: boundaries in seconds from the start of the line (first = 0, last = dur).
    Kokoro gives no word timestamps; this lines the estimate up with the real gaps
    and consonant dips in the audio."""
    hop = int(0.01 * sr)
    n = len(samples) // hop
    if n < 3:
        return rel_times
    rms = np.sqrt(np.mean(samples[: n * hop].reshape(n, hop) ** 2, axis=1))
    rms = np.convolve(rms, np.ones(3) / 3, mode="same")
    out = list(rel_times)
    for k in range(1, len(out) - 1):
        lo = max(out[k - 1] + min_word, out[k] - window)
        hi = min(rel_times[k + 1] - min_word, out[k] + window)
        if hi <= lo:
            continue
        a, b = int(lo * 100), min(n - 1, int(hi * 100))
        if b > a:
            out[k] = (a + int(np.argmin(rms[a:b + 1]))) / 100.0
    return out


def caption_events(text, v_start, v_dur, end, samples=None, sr=None, caption_y=None):
    """[(t0, t1, words, active_index, chunk_t0, caption_y)]."""
    chunks = chunk_words(text)
    weights = [w for c in chunks for _, w in c]
    total = sum(weights)
    rel, acc = [], 0
    for w in weights:
        rel.append(acc / total * v_dur)
        acc += w
    rel.append(v_dur)
    if samples is not None:
        rel = _snap_to_pauses(rel, samples, sr)
    times = [v_start + r for r in rel]
    events, k = [], 0
    for ci, c in enumerate(chunks):
        words = [re.sub(r"[.,;:]$", "", w) for w, _ in c]
        chunk_end = times[k + len(c)] if ci < len(chunks) - 1 else end
        for j in range(len(c)):
            t1 = times[k + j + 1] if j < len(c) - 1 else chunk_end
            events.append((times[k + j], t1, words, j, times[k], caption_y))
        k += len(c)
    return events


_cache = {}


def _is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF or 0x2B00 <= o <= 0x2BFF


def _emoji_glyph(ch, size):
    key = ("emoji", ch, size)
    if key not in _cache:
        f = ImageFont.truetype(str(EMOJI_FONT), 109)
        img = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((5, 5), ch, font=f, embedded_color=True)
        img = img.crop(img.getbbox() or (0, 0, 1, 1))
        s = size / max(img.height, 1) * 0.95
        _cache[key] = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)
    return _cache[key]


def text_image(text, size, color=(255, 255, 255), stroke=None, max_w=None):
    """Bold outlined text (Poppins ExtraBold) with colour-emoji support; wraps to max_w."""
    key = ("text", text, size, color, stroke, max_w)
    if key in _cache:
        return _cache[key]
    stroke = int(size * 0.12) if stroke is None else stroke
    font = ImageFont.truetype(str(FONT), size)
    max_w = max_w or LAYOUT["max_w"]
    space = int(size * 0.28)

    def word_img(word):
        parts, buf = [], ""
        for ch in word:
            if ch == "️":
                continue
            if _is_emoji(ch):
                if buf:
                    parts.append(("t", buf))
                    buf = ""
                parts.append(("e", ch))
            else:
                buf += ch
        if buf:
            parts.append(("t", buf))
        imgs = []
        for kind, val in parts:
            if kind == "e":
                imgs.append(_emoji_glyph(val, size))
            else:
                b = font.getbbox(val, stroke_width=stroke)
                im = Image.new("RGBA", (b[2] - b[0] + 4, int(size * 1.45)), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((2 - b[0], int(size * 0.18)), val, font=font, fill=color,
                                        stroke_width=stroke, stroke_fill=INK)
                imgs.append(im)
        w = sum(i.width for i in imgs) + 6 * (len(imgs) - 1)
        h = int(size * 1.45)
        out = Image.new("RGBA", (max(w, 1), h), (0, 0, 0, 0))
        x = 0
        for im in imgs:
            out.alpha_composite(im, (x, (h - im.height) // 2))
            x += im.width + 6
        return out

    words = [word_img(w) for w in text.split()]
    lines, cur, cur_w = [], [], 0
    for wi in words:
        add = wi.width + (space if cur else 0)
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [], 0
            add = wi.width
        cur.append(wi)
        cur_w += add
    lines.append(cur)
    line_h = int(size * 1.2)
    full_w = max(sum(i.width for i in l) + space * (len(l) - 1) for l in lines)
    img = Image.new("RGBA", (full_w + 40, line_h * len(lines) + int(size * 0.5)), (0, 0, 0, 0))
    for li, l in enumerate(lines):
        lw = sum(i.width for i in l) + space * (len(l) - 1)
        x = (img.width - lw) // 2
        for wi in l:
            img.alpha_composite(wi, (x, 10 + li * line_h))
            x += wi.width + space
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow.putalpha(img.getchannel("A").point(lambda a: a * 0.5).filter(ImageFilter.GaussianBlur(size / 9)))
    out = Image.alpha_composite(shadow, img)
    _cache[key] = out
    return out


def caption_image(words, active):
    key = ("cap", tuple(words), active, LAYOUT["max_w"])
    if key in _cache:
        return _cache[key]
    font = ImageFont.truetype(str(FONT), 96)
    space = 26
    sizes = [font.getbbox(w, stroke_width=12) for w in words]
    widths = [b[2] - b[0] for b in sizes]
    total_w = sum(widths) + space * (len(words) - 1)
    lines = [list(range(len(words)))]
    if total_w > LAYOUT["max_w"] and len(words) > 1:
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
            d.text((x - sizes[i][0], y), words[i], font=font, fill=fill, stroke_width=12, stroke_fill=INK)
            x += widths[i] + space
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow.putalpha(img.getchannel("A").point(lambda a: a * 0.55).filter(ImageFilter.GaussianBlur(10)))
    out = Image.alpha_composite(shadow, img)
    _cache[key] = out
    return out


def label_image(letter, size=190):
    key = ("label", letter, size)
    if key in _cache:
        return _cache[key]
    pad = 16
    img = Image.new("RGBA", (size + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((pad, pad + 8, pad + size, pad + size + 8), fill=(0, 0, 0, 120))
    d.ellipse((pad, pad, pad + size, pad + size), fill=(255, 214, 64), outline=INK, width=10)
    font = ImageFont.truetype(str(FONT), int(size * 0.62))
    b = font.getbbox(letter)
    d.text((pad + (size - (b[2] - b[0])) / 2 - b[0], pad + (size - (b[3] - b[1])) / 2 - b[1]),
           letter, font=font, fill=INK)
    _cache[key] = img
    return img


def countdown_image(n, size=170):
    key = ("count", n, size)
    if key in _cache:
        return _cache[key]
    pad = 14
    img = Image.new("RGBA", (size + 2 * pad, size + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((pad, pad, pad + size, pad + size), fill=(200, 16, 46), outline=(255, 255, 255), width=8)
    font = ImageFont.truetype(str(FONT), int(size * 0.6))
    s = str(n)
    b = font.getbbox(s)
    d.text((pad + (size - (b[2] - b[0])) / 2 - b[0], pad + (size - (b[3] - b[1])) / 2 - b[1]),
           s, font=font, fill=(255, 255, 255))
    _cache[key] = img
    return img


def _pop(img, age, dur=0.16):
    if age >= dur:
        return img
    k = age / dur
    sc = 0.6 + 0.4 * (1 + 2.70158 * (k - 1) ** 3 + 1.70158 * (k - 1) ** 2)
    return img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BILINEAR)


def _place(frame, img, cx, cy):
    frame.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


# ----------------------------------------------------------------- camera
MOTIONS = {
    #            z0    z1    (cx0, cy0)   (cx1, cy1)  -- centres as fraction of image
    "push_in":  (1.00, 1.16, (0.5, 0.5), (0.5, 0.48)),
    "fast_push": (1.00, 1.22, (0.5, 0.5), (0.5, 0.5)),
    "pull_out": (1.16, 1.00, (0.5, 0.48), (0.5, 0.5)),
    "pan_right": (1.14, 1.14, (0.40, 0.5), (0.60, 0.5)),
    "pan_left": (1.14, 1.14, (0.60, 0.5), (0.40, 0.5)),
    "pan_down": (1.12, 1.12, (0.5, 0.42), (0.5, 0.58)),
    "pan_up":   (1.12, 1.12, (0.5, 0.58), (0.5, 0.42)),
    "still":    (1.04, 1.06, (0.5, 0.5), (0.5, 0.5)),
    "slow_zoom": (1.00, 1.07, (0.5, 0.5), (0.5, 0.5)),
}


def _ease(p):
    return 0.5 - 0.5 * math.cos(math.pi * p) if p < 1 else 1.0


def camera_box(img_w, img_h, motion, p, since_cut, punch=True, ease="mix"):
    if isinstance(motion, dict):
        z0, z1 = motion["z0"], motion["z1"]
        c0, c1 = motion.get("c0", (0.5, 0.5)), motion.get("c1", (0.5, 0.5))
        ease = motion.get("ease", ease)
    else:
        z0, z1, c0, c1 = MOTIONS.get(motion, MOTIONS["still"])
    if ease == "out":       # fast start, gentle stop
        e = 1 - (1 - p) ** 2.2
    elif ease == "linear":
        e = p
    else:
        e = 0.35 * p + 0.65 * _ease(p)
    z = z0 + (z1 - z0) * e
    if punch and since_cut < 0.3:  # punch-in on the cut: start 5% tighter, settle in 0.3 s
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


def badge_image(text):
    font = ImageFont.truetype(str(FONT), 40)
    b = font.getbbox(text)
    w, h = b[2] - b[0] + 56, 76
    img = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), radius=38, fill=(200, 16, 46, 235))
    d.text((10 + 28 - b[0], 10 + (h - (b[3] - b[1])) / 2 - b[1]), text, font=font, fill=(255, 255, 255))
    return img


def _rain_layer():
    rng = np.random.default_rng(3)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(420):
        x, y = rng.uniform(-200, W), rng.uniform(0, H)
        ln = rng.uniform(40, 110)
        a = int(rng.uniform(50, 130))
        d.line((x, y, x + ln * 0.28, y + ln), fill=(210, 230, 255, a), width=int(rng.choice([2, 2, 3])))
    tall = Image.new("RGBA", (W, 2 * H), (0, 0, 0, 0))
    tall.alpha_composite(img, (0, 0))
    tall.alpha_composite(img, (0, H))
    return tall


def _snow_layer():
    rng = np.random.default_rng(9)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(520):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.choice([2, 3, 3, 4, 5, 6])
        a = int(rng.uniform(150, 240))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, a))
    tall = Image.new("RGBA", (W, 2 * H), (0, 0, 0, 0))
    tall.alpha_composite(img, (0, 0))
    tall.alpha_composite(img, (0, H))
    return tall


def _init(plan):
    _G["plan"] = plan
    LAYOUT.update(plan.get("layout", {}))
    _G["badge"] = badge_image(plan["badge"]) if plan.get("badge") else None
    _G["imgs"] = {sid: Image.open(p).convert("RGB") for sid, p in plan["images"].items()}
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    strength = plan.get("vignette", 200)
    a = (np.clip((r - 0.55) / 0.75, 0, 1) ** 1.6 * strength).astype(np.uint8)
    vig = np.zeros((H, W, 4), np.uint8)
    vig[..., 3] = a
    _G["vig"] = Image.fromarray(vig, "RGBA")
    rng = np.random.default_rng(1)
    grains = []
    for _ in range(6):
        g = rng.integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
        g = Image.fromarray(g, "L").resize((W, H), Image.BILINEAR)
        grains.append(Image.merge("RGBA", (g, g, g, Image.new("L", (W, H), 11))))
    _G["grain"] = grains
    if any("rain" in s.get("fx", []) for s in plan["shots"]):
        _G["rain"] = _rain_layer()
    if any("snow" in s.get("fx", []) for s in plan["shots"]):
        _G["snow"] = _snow_layer()


def _flash_value(flashes, st):
    v = 0.0
    for f in flashes:
        at, peak = f["at"], f.get("peak", 0.6)
        attack, decay = f.get("attack", 0.0), f.get("decay", 0.35)
        if attack > 0 and at - attack <= st < at:
            v = max(v, peak * (st - (at - attack)) / attack)
        elif at <= st < at + decay:
            v = max(v, peak * (1 - (st - at) / decay) ** 2)
    return v


def _flicker(t):
    v = 0.5 * math.sin(t * 13.1) + 0.3 * math.sin(t * 29.7 + 1.3) + 0.2 * math.sin(t * 61.3 + 0.4)
    dip = 1.0 if math.sin(t * 2.3) > 0.93 else 0.0  # occasional deeper dip
    return 0.06 + 0.05 * v + 0.12 * dip


def _frame(i):
    plan = _G["plan"]
    n = plan["frames"]
    t = i / FPS
    shots = plan["shots"]
    s = next((x for x in shots if x["start"] <= t < x["end"]), shots[-1])
    img = _G["imgs"][s["id"]]
    st = t - s["start"]
    span = max(1e-6, s["end"] - s["start"] - 1.0 / FPS)
    p = min(1.0, st / span)
    fx = s.get("fx", [])
    box = camera_box(img.width, img.height, s["motion"], p, st, s.get("punch", True))
    if "sway" in fx:
        k = img.width / W
        dx = (5 * math.sin(2 * math.pi * 0.7 * t) + 2 * math.sin(2 * math.pi * 2.1 * t)) * k
        dy = (4 * math.sin(2 * math.pi * 1.6 * t + 0.7)) * k
        box = (box[0] + dx, box[1] + dy, box[2] + dx, box[3] + dy)
        if box[0] < 0 or box[2] > img.width or box[1] < 0 or box[3] > img.height:
            box = (box[0] - dx, box[1] - dy, box[2] - dx, box[3] - dy)
    if "snow" in fx and s.get("snow_box"):
        # snow is drawn in picture space so it stays inside the window while the camera moves
        x0, y0, x1, y1 = s["snow_box"]
        k = img.width / W
        off = int((t * 130) % H)
        drift = int(25 * math.sin(t * 0.9))
        layer = _G["snow"].crop((-drift, H - off + y0, -drift + (x1 - x0), H - off + y1))
        layer = layer.resize((int((x1 - x0) * k), int((y1 - y0) * k)), Image.BILINEAR)
        img = img.copy()
        img.paste(layer, (int(x0 * k), int(y0 * k)), layer)
    frame = img.resize((W, H), Image.BILINEAR, box=box).convert("RGBA")

    if "rain" in fx:
        off = int((t * 1500) % H)
        layer = _G["rain"].crop((0, H - off, W, 2 * H - off))
        rb = s.get("rain_box")
        if rb:
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).rectangle(rb, fill=255)
            layer = Image.composite(layer, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
        frame.alpha_composite(layer)

    grain_idx = 0 if i in (0, n - 1) else (i // 2) % len(_G["grain"])
    frame.alpha_composite(_G["grain"][grain_idx])
    frame.alpha_composite(_G["vig"])

    if "flicker" in fx:
        a = int(255 * _flicker(t))
        frame.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, a)))

    flashes = [dict(f, at=span if f["at"] == "end" else f["at"]) for f in s.get("flashes", [])]
    fv = _flash_value(flashes, st)
    if fv > 0:
        frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * min(1, fv)))))

    if _G["badge"] is not None:
        frame.alpha_composite(_G["badge"], (40, 90))

    cx = LAYOUT["cx"]
    for o in s.get("overlays", []):
        if not (o.get("start", 0) <= st < o.get("end", 1e9)):
            continue
        if o.get("type") == "label":
            im = label_image(o["text"], o.get("size", 190))
        else:
            im = text_image(o["text"], o.get("size", 110), tuple(o.get("color", (255, 255, 255))),
                            max_w=o.get("max_w"))
        if o.get("pop", True):
            im = _pop(im, st - o.get("start", 0))
        _place(frame, im, o.get("x", cx), o["y"])

    cd = s.get("countdown")
    if cd and st >= cd["at"]:
        k = int((st - cd["at"]) / cd.get("step", 1.0))
        if k < cd.get("from", 3):
            num = cd.get("from", 3) - k
            age = st - cd["at"] - k * cd.get("step", 1.0)
            _place(frame, _pop(countdown_image(num), age, 0.12), cd.get("x", 150), cd.get("y", 330))

    for t0, t1, words, active, chunk_t0, cap_y in plan["captions"]:
        if t0 <= t < t1:
            full = caption_image(words, active)
            cap = _pop(full, t - chunk_t0, 0.14)
            cy = cap_y or s.get("caption_y", CAPTION_Y)
            cy -= (full.height - 190) / 2  # two-line captions grow upward, never into the bottom zone
            _place(frame, cap, cx, cy)
            break

    out = frame.convert("RGB")
    if plan.get("fade", True):
        fade = min(1.0, t / 0.25, (plan["total"] - t) / 0.7)
        if fade < 1:
            out = Image.blend(Image.new("RGB", (W, H)), out, max(0.0, fade))
    return out.tobytes()


def render_frame(plan, t):
    """Render a single frame (for covers and checks)."""
    _init(plan)
    return Image.frombytes("RGB", (W, H), _frame(int(round(t * FPS))))


def normalize_audio(src: Path, dst: Path, target=-14.0):
    """Two-pass EBU R128 loudness normalisation (more accurate than one pass on short clips)."""
    import json
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
                        f"loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"): r.stderr.rindex("}") + 1])
    af = (f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", af, "-ar", "48000", str(dst)],
                   check=True)


def render(plan, audio_path: Path, out_path: Path, workers=4):
    n = int(round(plan["total"] * FPS))
    plan["frames"] = n
    norm = audio_path.with_name(audio_path.stem + "-norm.wav")
    normalize_audio(audio_path, norm)
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(norm),
        "-map", "0:v", "-map", "1:a",
        "-vf", "setsar=1", "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-tune", "grain",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
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

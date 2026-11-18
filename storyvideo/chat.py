"""Text-message thriller renderer ("23%" series).

    python3 -m storyvideo.chat stories/23-percent/ep01 --out 23-percent/ep01/ep01-instagram.mp4

An episode is a folder with episode.json (see docs/chat-episodes.md). Everything is drawn
with Pillow: lock screen, chat screen, message bubbles (spring pop-in + scroll), typing
dots, photo messages with a lightbox, the battery bar and the choice screen.
"""
import argparse
import json
import math
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import audio, tts, video

ROOT = Path(__file__).resolve().parent.parent
W, H, FPS = 1080, 1920, 30
FONTS = ROOT / "assets" / "fonts"


def font(weight, size):
    name = {"regular": "Inter-Regular.otf", "medium": "Inter-Medium.otf", "semibold": "Inter-SemiBold.otf",
            "bold": "Inter-Bold.otf", "light": "Inter-Light.otf"}[weight]
    return ImageFont.truetype(str(FONTS / name), size)


# ------------------------------------------------------------------ theme (generic light UI)
BG = (244, 246, 250)
HEADER = (255, 255, 255)
HER = (230, 231, 237)
HER_TEXT = (20, 20, 26)
YOU = (47, 124, 246)
YOU_TEXT = (255, 255, 255)
MUTED = (120, 124, 134)
SAFE_RIGHT = 900          # keep content left of the right 15% (918px)
MSG_TOP, MSG_BOTTOM = 540, 1300
BUBBLE_FONT = 50
POP = 0.32                # bubble pop-in time
SCROLL = 0.28


def ease_out(p):
    p = min(max(p, 0.0), 1.0)
    return 1 - (1 - p) ** 3


def spring(p):
    """0..1 with a small overshoot, for bubbles popping in."""
    p = min(max(p, 0.0), 1.0)
    return 1 + 2.4 * (p - 1) ** 3 + 1.4 * (p - 1) ** 2


# ------------------------------------------------------------------ rich text (Inter + colour emoji)
def text_line(draw_img, xy, text, fnt, fill):
    """Draw a single line with colour emoji support. Returns width."""
    x, y = xy
    d = ImageDraw.Draw(draw_img)
    buf = ""
    size = fnt.size
    def flush(x):
        nonlocal buf
        if buf:
            d.text((x, y), buf, font=fnt, fill=fill)
            x += d.textlength(buf, font=fnt)
            buf = ""
        return x
    for ch in text:
        if ch == "️":
            continue
        if video._is_emoji(ch):
            x = flush(x)
            g = video._emoji_glyph(ch, int(size * 1.05))
            draw_img.alpha_composite(g, (int(x), int(y + size * 0.12)))
            x += g.width + 4
        else:
            buf += ch
    x = flush(x)
    return x - xy[0]


def measure(text, fnt):
    d = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = 0
    for ch in text:
        w += (fnt.size * 1.1) if video._is_emoji(ch) else d.textlength(ch, font=fnt)
    return w


def wrap(text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if cur and measure(test, fnt) > max_w:
            lines.append(cur)
            cur = wd
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ components
_cache = {}


def bubble(text, mine):
    key = ("b", text, mine)
    if key in _cache:
        return _cache[key]
    fnt = font("medium", BUBBLE_FONT)
    lines = wrap(text, fnt, 560)
    lh = int(BUBBLE_FONT * 1.28)
    tw = max(measure(l, fnt) for l in lines)
    pw, ph = 34, 24
    w, h = int(tw + 2 * pw), int(lh * len(lines) + 2 * ph)
    img = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = YOU if mine else HER
    d.rounded_rectangle((0, 0, w, h), radius=40, fill=col)
    # little tail
    if mine:
        d.polygon([(w - 30, h - 18), (w + 12, h + 6), (w - 6, h - 40)], fill=col)
    else:
        d.polygon([(30, h - 18), (-12, h + 6), (6, h - 40)], fill=col)
    for i, l in enumerate(lines):
        text_line(img, (pw, ph + i * lh - 4), l, fnt, YOU_TEXT if mine else HER_TEXT)
    _cache[key] = img
    return img


def typing_bubble(t):
    w, h = 170, 96
    img = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w, h), radius=40, fill=HER)
    d.polygon([(30, h - 18), (-12, h + 6), (6, h - 40)], fill=HER)
    for i in range(3):
        ph = t * 2 * math.pi * 1.6 - i * 0.9
        dy = -10 * max(0.0, math.sin(ph))
        shade = int(150 - 50 * max(0.0, math.sin(ph)))
        cx, cy = 48 + i * 37, h / 2 + dy
        d.ellipse((cx - 13, cy - 13, cx + 13, cy + 13), fill=(shade, shade, shade + 6))
    return img


def photo_bubble(photo, w=430):
    key = ("p", str(photo), w)
    if key in _cache:
        return _cache[key]
    im = Image.open(photo).convert("RGB")
    h = int(w * 5 / 4)
    im = im.resize((w, h), Image.LANCZOS) if abs(im.width / im.height - 0.8) < 0.02 else _cover(im, w, h)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=36, fill=255)
    out = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    _cache[key] = out
    return out


def _cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def battery_icon(pct, w=86, h=44):
    img = Image.new("RGBA", (w + 12, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w, h - 1), radius=10, outline=(30, 30, 36), width=5)
    d.rounded_rectangle((w + 1, h * 0.3, w + 10, h * 0.7), radius=3, fill=(30, 30, 36))
    fw = max(6, int((w - 14) * pct / 100))
    d.rounded_rectangle((7, 7, 7 + fw, h - 8), radius=5, fill=(226, 38, 52))
    return img


def battery_bar(cfg, t):
    pct, label = cfg.get("percent", 23), cfg.get("label", "HER BATTERY")
    age = t - cfg["show_from"]
    bw, bh = 640, 96
    img = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=48, fill=(255, 255, 255, 245), outline=(226, 38, 52), width=4)
    img.alpha_composite(battery_icon(pct), (34, 26))
    f = font("bold", 46)
    txt = f"{label} {pct}%"
    d.text((150, 22), txt, font=f, fill=(226, 38, 52))
    # pulse on appear (and a slow breathing pulse after)
    s = 1.0
    if age < 0.6:
        s = 0.6 + 0.4 * spring(age / 0.35) + 0.08 * math.sin(min(age / 0.6, 1) * math.pi)
    else:
        s = 1 + 0.02 * math.sin(age * 4.0)
    if abs(s - 1) > 1e-3:
        img = img.resize((max(1, int(bw * s)), max(1, int(bh * s))), Image.BILINEAR)
    return img


def status_bar(img, clock="2:47", dark=False):
    d = ImageDraw.Draw(img)
    col = (20, 20, 26) if not dark else (255, 255, 255)
    d.text((70, 28), clock, font=font("semibold", 40), fill=col)
    # generic signal + battery glyphs (phone's own battery: full, not the story battery)
    for i in range(4):
        d.rounded_rectangle((760 + i * 18, 62 - i * 10, 772 + i * 18, 70), radius=2, fill=col)
    d.rounded_rectangle((850, 36, 910, 68), radius=8, outline=col, width=4)
    d.rectangle((856, 42, 902, 62), fill=col)


def header(img, cfg):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 250), fill=HEADER)
    d.line((0, 250, W, 250), fill=(222, 224, 230), width=3)
    status_bar(img, cfg.get("clock", "2:47"))
    d.line((72, 170, 50, 148), fill=YOU, width=8)
    d.line((50, 148, 72, 126), fill=YOU, width=8)
    d.ellipse((110, 108, 190, 188), fill=(200, 204, 212))
    d.text((133, 118), "?", font=font("bold", 50), fill=(255, 255, 255))
    d.text((214, 108), cfg.get("contact", "Unknown"), font=font("semibold", 52), fill=(20, 20, 26))
    d.text((216, 170), cfg.get("subtitle", "mobile"), font=font("regular", 32), fill=MUTED)


def labels(img, cfg):
    d = ImageDraw.Draw(img)
    ep = cfg.get("ep_label", "EP 1")
    f = font("bold", 36)
    tw = d.textlength(ep, font=f)
    d.rounded_rectangle((60, 280, 60 + tw + 40, 336), radius=28, fill=(20, 20, 26))
    d.text((80, 285), ep, font=f, fill=(255, 255, 255))
    d.text((60 + tw + 60, 292), cfg.get("fiction_label", "Fiction"), font=font("medium", 30), fill=MUTED)


def input_bar(img):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 1740, W, H), fill=HEADER)
    d.rounded_rectangle((60, 1770, 860, 1860), radius=45, outline=(210, 212, 220), width=4, fill=(250, 250, 252))
    d.text((100, 1792), "Text message", font=font("regular", 38), fill=(160, 164, 172))
    d.ellipse((900, 1770, 990, 1860), fill=YOU)


def lock_screen(cfg, t):
    lk = cfg["lock"]
    img = Image.new("RGBA", (W, H))
    # soft pastel wallpaper
    top, bot = np.array([255, 214, 196]), np.array([206, 214, 255])
    grad = (top[None, :] + (bot - top)[None, :] * np.linspace(0, 1, H)[:, None]).astype(np.uint8)
    img = Image.fromarray(np.repeat(grad[:, None, :], W, axis=1), "RGB").convert("RGBA")
    status_bar(img, lk.get("time", "2:47"))
    d = ImageDraw.Draw(img)
    f = font("light", 300)
    tw = d.textlength(lk.get("time", "2:47"), font=f)
    d.text(((918 - tw) / 2, 330), lk.get("time", "2:47"), font=f, fill=(255, 255, 255), stroke_width=2, stroke_fill=(150, 140, 170))
    fd = font("medium", 52)
    dw = d.textlength(lk.get("date", ""), font=fd)
    d.text(((918 - dw) / 2, 680), lk.get("date", ""), font=fd, fill=(60, 56, 80))
    # notification banner: visible from frame 0, tiny settle animation
    n = lk["notification"]
    s = 0.97 + 0.03 * ease_out(t / 0.4)
    card = Image.new("RGBA", (820, 220), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle((0, 0, 819, 219), radius=44, fill=(255, 255, 255, 250))
    cd.rounded_rectangle((34, 34, 104, 104), radius=18, fill=(52, 199, 120))
    cd.ellipse((50, 50, 88, 82), fill=(255, 255, 255))
    cd.polygon([(56, 76), (52, 92), (70, 80)], fill=(255, 255, 255))
    cd.text((126, 36), n.get("from", "Unknown"), font=font("bold", 46), fill=(20, 20, 26))
    cd.text((700, 44), "now", font=font("regular", 34), fill=MUTED)
    text_line(card, (36, 124), n["text"], font("medium", 50), (20, 20, 26))
    if s != 1:
        card = card.resize((int(820 * s), int(220 * s)), Image.BILINEAR)
    img.alpha_composite(card, (int(459 - card.width / 2), int(860 - card.height / 2)))
    return img


# ------------------------------------------------------------------ chat layout
def items_at(cfg, t):
    """Visible chat items at time t with their current height share (for scrolling)."""
    out = []
    for m in cfg["messages"]:
        if t < m["t"]:
            continue
        if m.get("typing"):
            until = m["until"]
            if t >= until + SCROLL:
                continue
            grow = ease_out((t - m["t"]) / SCROLL)
            if t > until:
                grow = 1 - ease_out((t - until) / SCROLL)
            out.append(("typing", m, grow))
        elif m.get("photo"):
            out.append(("photo", m, ease_out((t - m["t"]) / SCROLL)))
        else:
            out.append(("text", m, ease_out((t - m["t"]) / SCROLL)))
    return out


def _fade_mask():
    if "fade" not in _cache:
        a = np.clip((np.arange(H) - (MSG_TOP - 110)) / 110.0, 0, 1)
        _cache["fade"] = Image.fromarray((np.repeat(a[:, None], W, axis=1) * 255).astype(np.uint8), "L")
    return _cache["fade"]


def chat_screen(cfg, t, story_dir):
    img = Image.new("RGBA", (W, H), BG + (255,))
    y = MSG_BOTTOM
    placed = []
    for kind, m, grow in reversed(items_at(cfg, t)):
        if kind == "typing":
            b = typing_bubble(t)
        elif kind == "photo":
            b = photo_bubble(story_dir / m["photo"])
        else:
            b = bubble(m["text"], m.get("from") == "you")
        h = b.height - 16
        y -= (h + 26) * grow
        placed.append((kind, m, b, y, grow))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for kind, m, b, by, grow in placed:
        if by + b.height < MSG_TOP - 120:
            continue
        mine = m.get("from") == "you"
        age = t - m["t"]
        s = spring(age / POP) if age < POP else 1.0
        if kind == "typing" and t > m["until"]:
            s = max(0.01, grow)
        bb = b
        if s != 1.0:
            bb = b.resize((max(1, int(b.width * s)), max(1, int(b.height * s))), Image.BILINEAR)
        x = (SAFE_RIGHT - bb.width) if mine else 60
        yy = by + (b.height - bb.height)
        layer.alpha_composite(bb, (int(x), int(max(yy, -bb.height + 1))) if yy >= 0 else (int(x), 0)) if yy >= 0 else layer.alpha_composite(bb.crop((0, int(-yy), bb.width, bb.height)), (int(x), 0))
    # older messages scroll up and fade out smoothly, row by row
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", (W, H), 0), _fade_mask()))
    img.alpha_composite(layer)
    header(img, cfg)
    labels(img, cfg)
    input_bar(img)
    if cfg.get("battery") and t >= cfg["battery"]["show_from"]:
        bar = battery_bar(cfg["battery"], t)
        img.alpha_composite(bar, (int(459 - bar.width / 2), int(410 - bar.height / 2)))
    return img


def lightbox(base, cfg, t, story_dir):
    for m in cfg["messages"]:
        if m.get("photo") and m.get("open") and m["open"][0] <= t < m["open"][1] + 0.25:
            o0, o1 = m["open"]
            a = ease_out((t - o0) / 0.3) if t < o1 else 1 - ease_out((t - o1) / 0.25)
            veil = Image.new("RGBA", (W, H), (250, 250, 252, int(215 * a)))
            base.alpha_composite(veil)
            im = Image.open(story_dir / m["photo"]).convert("RGB")
            pw, ph = 800, 1000
            z = 1.0 + 0.08 * min(1, (t - o0) / max(0.1, o1 - o0))
            cw, ch = im.width / z, im.height / z
            l, tp = (im.width - cw) / 2, (im.height - ch) / 2
            ph_img = _cover(im.crop((int(l), int(tp), int(l + cw), int(tp + ch))), pw, ph)
            s = 0.85 + 0.15 * spring((t - o0) / 0.35) if t < o1 else 1 - 0.1 * ease_out((t - o1) / 0.25)
            ph_img = ph_img.resize((int(pw * s), int(ph * s)), Image.BILINEAR).convert("RGBA")
            mask = Image.new("L", ph_img.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, ph_img.width - 1, ph_img.height - 1), radius=30, fill=int(255 * a))
            ph_img.putalpha(mask)
            base.alpha_composite(ph_img, (int(459 - ph_img.width / 2), int(880 - ph_img.height / 2)))
    return base


def choice_screen(base, cfg, t):
    c = cfg["choice"]
    age = t - c["t"]
    blur = base.convert("RGB").filter(ImageFilter.GaussianBlur(min(18, 4 + age * 30))).convert("RGBA")
    blur.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(90 * ease_out(age / 0.3)))))
    card = Image.new("RGBA", (840, 860), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, 839, 859), radius=48, fill=(255, 255, 255, 250), outline=(220, 222, 230), width=3)
    fq = font("bold", 60)
    for i, line in enumerate(wrap(c["question"], fq, 760)):
        lw = measure(line, fq)
        d.text(((840 - lw) / 2, 50 + i * 74), line, font=fq, fill=(20, 20, 26))
    def button(y, letter, text, col, tcol, delay):
        if age < delay:
            return
        s = spring((age - delay) / 0.3)
        b = Image.new("RGBA", (760, 170), (0, 0, 0, 0))
        bd = ImageDraw.Draw(b)
        bd.rounded_rectangle((0, 0, 759, 169), radius=40, fill=col)
        bd.ellipse((26, 37, 122, 133), fill=(255, 255, 255))
        bd.text((56, 50), letter, font=font("bold", 58), fill=col)
        fb = font("bold", 46)
        lines = wrap(text, fb, 600)
        for i, l in enumerate(lines):
            bd.text((150, 85 - 30 * len(lines) + i * 60), l, font=fb, fill=tcol)
        if s != 1:
            b = b.resize((max(1, int(760 * s)), max(1, int(170 * s))), Image.BILINEAR)
        card.alpha_composite(b, (int(420 - b.width / 2), int(y + 85 - b.height / 2)))
    button(220, "A", c["a"], YOU, (255, 255, 255), 0.25)
    button(420, "B", c["b"], (90, 96, 110), (255, 255, 255), 0.55)
    if age > 1.0 and c.get("note"):
        fn = font("semibold", 42)
        lw = measure(c["note"], fn)
        text_line(card, ((840 - lw) / 2, 640), c["note"], fn, (226, 38, 52))
    if c.get("send") and age > c.get("send_at", 4.0):
        fs = font("medium", 36)
        lw = measure(c["send"], fs)
        text_line(card, ((840 - lw) / 2, 730), c["send"], fs, MUTED)
    s = spring(age / 0.35)
    if s != 1:
        card = card.resize((max(1, int(840 * s)), max(1, int(860 * s))), Image.BILINEAR)
    blur.alpha_composite(card, (int(459 - card.width / 2), int(880 - card.height / 2)))
    return blur


# ------------------------------------------------------------------ frames
_G = {}


def _init(cfg, story_dir):
    _G["cfg"], _G["dir"] = cfg, Path(story_dir)


def frame_at(cfg, t, story_dir):
    lk = cfg.get("lock")
    if lk and t < lk["until"] + 0.35:
        if t < lk["until"]:
            img = lock_screen(cfg, t)
        else:  # lock screen slides up to reveal the chat
            p = ease_out((t - lk["until"]) / 0.35)
            img = chat_screen(cfg, t, story_dir)
            ls = lock_screen(cfg, lk["until"])
            img.alpha_composite(ls, (0, int(-H * p)))
    else:
        img = chat_screen(cfg, t, story_dir)
        img = lightbox(img, cfg, t, story_dir)
        if cfg.get("choice") and t >= cfg["choice"]["t"]:
            img = choice_screen(img, cfg, t)
    # gentle push-in + phone float (frame 0 stays exact for the cover)
    z = 1.0 + 0.035 * (t / cfg["duration"])
    fx, fy = 3 * math.sin(t * 1.3), 4 * math.sin(t * 0.9 + 0.5)
    if t > 0:
        bw, bh = W / z, H / z
        cx, cy = 459 + fx, 900 + fy
        x0 = min(max(cx - bw * 459 / W, 0), W - bw)
        y0 = min(max(cy - bh * 900 / H, 0), H - bh)
        img = img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + bw, y0 + bh))
    return img.convert("RGB")


def _frame(i):
    return frame_at(_G["cfg"], i / FPS, _G["dir"]).tobytes()


def build_audio(cfg, story_dir, build):
    total = cfg["duration"]
    sfx = [(e["at"], e["name"]) for e in cfg.get("sfx", [])]
    for m in cfg["messages"]:
        if m.get("typing"):
            continue
        sfx.append((m["t"], "shutter" if m.get("photo") else ("swoosh" if m.get("from") == "you" else "pop")))
    if cfg.get("battery"):
        sfx.append((cfg["battery"]["show_from"], "beep"))
    clips = []
    for v in cfg.get("vo", []):
        x, sr = tts.speak(v.get("say", v["text"]), v.get("voice", "am_michael"), v.get("speed", 1.0), build / "voice")
        clips.append((v["at"], x, sr))
    hb = None
    if cfg.get("heartbeat"):
        a, b = cfg["heartbeat"]
        hb = audio.heartbeat_track(total, a, b) * 0.22
    mix = audio.mix(total, clips, sfx, cfg.get("music", "drone"), cfg.get("music_volume", 0.6),
                    None, fades=False, drone_mute=cfg.get("silence"), extra=hb)
    wav = build / "mix.wav"
    sf.write(wav, mix, audio.SR)
    return wav


def main():
    ap = argparse.ArgumentParser(prog="storyvideo.chat")
    ap.add_argument("episode", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--still", type=float, help="only save the frame at this time as PNG to --out")
    args = ap.parse_args()
    d = args.episode.resolve()
    cfg = json.loads((d / "episode.json").read_text())
    if args.still is not None:
        frame_at(cfg, args.still, d).save(args.out)
        return
    build = d / "build"
    build.mkdir(exist_ok=True)
    wav = build_audio(cfg, d, build)
    norm = build / "mix-norm.wav"
    video.normalize_audio(wav, norm)
    n = int(round(cfg["duration"] * FPS))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    import subprocess
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", str(norm), "-map", "0:v", "-map", "1:a", "-vf", "setsar=1",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", str(args.out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(args.workers, initializer=_init, initargs=(cfg, str(d))) as pool:
        for k, data in enumerate(pool.imap(_frame, range(n), chunksize=6)):
            proc.stdin.write(data)
            if k % (FPS * 5) == 0:
                print(f"  frame {k}/{n}", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    print(f"done -> {args.out}")


if __name__ == "__main__":
    main()

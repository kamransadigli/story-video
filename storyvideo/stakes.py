"""STAKES BAR: a reusable on-screen meter for interactive story episodes.

    🚨 SUSPICION %   ·   🧾 EVIDENCE LEFT n   ·   🤝 PARTNER TRUST %

Configure it in story.json under "stakes" (see docs/stakes-bar.md):

    "stakes": {
      "y": 215,                       # vertical centre of the bar (px, keep below the top 8%)
      "show_from": 6.2,               # seconds: the bar slides in here
      "hide_from": 22.0,              # optional: the bar slides out here
      "start": {"suspicion": 0, "evidence": 3, "trust": 100},
      "changes": [                    # values animate (count up/down + pulse + tick sound)
        {"at": 19.0, "suspicion": 10},
        {"at": 13.0, "pulse": "evidence"},  # pulse without changing the value
        {"at": 15.0, "evidence": 3, "flash": [255, 60, 60]}  # optional colour while it pulses
      ]
    }
"""
import math

from PIL import Image, ImageDraw, ImageFont

FIELDS = [
    # key, emoji, label, suffix, colour
    ("suspicion", "🚨", "SUSPICION", "%", (255, 92, 92)),
    ("evidence", "🧾", "EVIDENCE", "", (255, 214, 64)),
    ("trust", "🤝", "TRUST", "%", (120, 220, 140)),
]
COUNT_TIME = 0.6    # seconds a value takes to count to its new number
PULSE_TIME = 0.45   # seconds of the pulse after a change
SLIDE_TIME = 0.35


def _ease(p):
    return 1 - (1 - min(max(p, 0), 1)) ** 3


def values_at(cfg, t):
    """Displayed value for each field at time t, plus how 'fresh' each change is (0..1 pulse)."""
    vals = dict(cfg.get("start", {}))
    pulse = {k: 0.0 for k, *_ in FIELDS}
    flash = {}
    for ch in sorted(cfg.get("changes", []), key=lambda c: c["at"]):
        if t < ch["at"]:
            break
        age = t - ch["at"]
        for k, *_ in FIELDS:
            if k in ch:
                old, new = vals.get(k, 0), ch[k]
                vals[k] = old + (new - old) * _ease(age / COUNT_TIME)
                if age < PULSE_TIME + COUNT_TIME:
                    pulse[k] = max(pulse[k], 1 - max(0, age - COUNT_TIME * 0.5) / PULSE_TIME)
                    if ch.get("flash"):
                        flash[k] = tuple(ch["flash"])
        if ch.get("pulse") and age < PULSE_TIME * 2:
            pulse[ch["pulse"]] = max(pulse[ch["pulse"]], 1 - age / (PULSE_TIME * 2))
    return vals, pulse, flash


def tick_times(cfg):
    """Times for tick sounds: a few ticks while each value counts, one for a pulse."""
    out = []
    for ch in cfg.get("changes", []):
        if any(k in ch for k, *_ in FIELDS):
            out += [ch["at"] + i * 0.12 for i in range(5)]
        elif ch.get("pulse"):
            out.append(ch["at"])
    return out


class StakesBar:
    def __init__(self, cfg, font_path, emoji_fn, width=1080, cx=459, max_w=880):
        self.cfg, self.font_path, self.emoji_fn = cfg, font_path, emoji_fn
        self.W, self.cx, self.max_w = width, cx, max_w
        self.f_val = ImageFont.truetype(str(font_path), 62)
        self.f_lab = ImageFont.truetype(str(font_path), 27)
        self._cache = {}

    def _cell(self, key, emoji, label, suffix, colour, value, pulse):
        txt = f"{int(round(value))}{suffix}"
        ck = (key, txt, round(pulse, 2), colour)
        if ck in self._cache:
            return self._cache[ck]
        w, h = 290, 140
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        em = self.emoji_fn(emoji, 52)
        img.alpha_composite(em, (6, (h - em.height) // 2 - 10))
        vb = self.f_val.getbbox(txt, stroke_width=6)
        x = 66
        d.text((x - vb[0], 14 - vb[1] + 4), txt, font=self.f_val, fill=colour, stroke_width=6, stroke_fill=(10, 10, 14))
        d.text((x, 92), label, font=self.f_lab, fill=(240, 232, 214), stroke_width=3, stroke_fill=(10, 10, 14))
        if pulse > 0:
            s = 1 + 0.22 * math.sin(min(pulse, 1) * math.pi / 2)
            img = img.resize((int(w * s), int(h * s)), Image.BILINEAR)
        self._cache[ck] = img
        return img

    def draw(self, frame, t):
        cfg = self.cfg
        t0 = cfg.get("show_from", 0)
        t1 = cfg.get("hide_from", 1e9)
        if t < t0 or t > t1 + SLIDE_TIME:
            return
        slide = _ease((t - t0) / SLIDE_TIME) if t < t1 else 1 - _ease((t - t1) / SLIDE_TIME)
        y = cfg.get("y", 215)
        y_now = int(y - (1 - slide) * 260)
        bar_w, bar_h = self.max_w, 146
        x0 = int(self.cx - bar_w / 2)
        panel = Image.new("RGBA", (bar_w, bar_h), (0, 0, 0, 0))
        ImageDraw.Draw(panel).rounded_rectangle((0, 0, bar_w - 1, bar_h - 1), radius=30,
                                                fill=(20, 16, 24, 205), outline=(255, 214, 64, 230), width=4)
        frame.alpha_composite(panel, (x0, y_now - bar_h // 2))
        vals, pulse, flash = values_at(cfg, t)
        cell_w = bar_w / 3
        for i, (key, emoji, label, suffix, colour) in enumerate(FIELDS):
            cell = self._cell(key, emoji, label, suffix, flash.get(key, colour), vals.get(key, 0), pulse[key])
            cx = x0 + cell_w * i + cell_w / 2 + 6
            frame.alpha_composite(cell, (int(cx - cell.width / 2), int(y_now - cell.height / 2)))

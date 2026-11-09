"""Synthesized noir music bed and sound effects (no samples, no licenses), plus the final mix."""
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(7)


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _lp(x, hz, order=2):
    b, a = signal.butter(order, hz / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def _hp(x, hz, order=2):
    b, a = signal.butter(order, hz / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def _bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def _norm(x, peak=1.0):
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def _note(f):
    return 440.0 * 2 ** ((f - 69) / 12)


# ---------------------------------------------------------------- sfx
def sfx_whoosh(dur=0.45):
    t = _t(dur)
    n = rng.standard_normal(len(t))
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    lo, hi = _lp(n, 600), _lp(n, 3500)
    mix = lo * (1 - t / dur) + hi * (t / dur)
    return _norm(mix * env, 0.5)


def sfx_hit(dur=2.2):
    t = _t(dur)
    f = 45 + 80 * np.exp(-t * 18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4)
    click = _hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 60) * 0.5
    tail = _lp(rng.standard_normal(len(t)), 400) * np.exp(-t * 1.8) * 0.6
    return _norm(boom + click + tail, 0.9)


def sfx_glass(dur=1.2):
    t = _t(dur)
    out = _hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 18) * 0.7
    for _ in range(14):
        start = rng.uniform(0, 0.35)
        f = rng.uniform(2500, 7500)
        tt = np.clip(t - start, 0, None)
        out += (t > start) * np.sin(2 * np.pi * f * tt) * np.exp(-tt * rng.uniform(10, 25)) * 0.25
    return _norm(out, 0.6)


def sfx_click(dur=0.25):
    t = _t(dur)
    c = _hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 120)
    c2 = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 80) * 0.4
    shift = np.roll(c * 0.7, int(0.06 * SR))
    return _norm(c + c2 + shift, 0.6)


def sfx_static(dur=0.9):
    t = _t(dur)
    n = _bp(rng.standard_normal(len(t)), 800, 6000)
    trem = 0.6 + 0.4 * (np.sin(2 * np.pi * 17 * t) > 0)
    env = np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.2)
    return _norm(n * trem * env, 0.35)


def sfx_riser(dur=2.0):
    t = _t(dur)
    f = 180 * (6 ** (t / dur))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    n = _bp(rng.standard_normal(len(t)), 500, 5000)
    env = (t / dur) ** 2
    return _norm((tone * 0.5 + n * 0.6) * env, 0.55)


def sfx_end(dur=3.5):
    t = _t(dur)
    hit = np.zeros(len(t))
    h = sfx_hit(2.2)
    hit[: len(h)] = h
    drone = sum(np.sin(2 * np.pi * _note(m) * t) for m in (38, 45, 50)) * np.exp(-t * 0.8) * 0.3
    return _norm(hit + drone, 0.9)


def sfx_tick(dur=2.4, rate=2.0):
    t = _t(dur)
    out = np.zeros(len(t))
    tl = int(0.03 * SR)
    tt = np.arange(tl) / SR
    tick = _hp(rng.standard_normal(tl), 2500) * np.exp(-tt * 250) + np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 300) * 0.5
    for k in range(int(dur * rate)):
        a = int(k / rate * SR)
        out[a:a + tl] += tick * (0.7 if k % 2 else 1.0)
    return _norm(out, 0.7)


SFX = {
    "tick": (sfx_tick, 0.5),
    "whoosh": (sfx_whoosh, 0.35),
    "hit": (sfx_hit, 0.55),
    "glass": (sfx_glass, 0.55),
    "click": (sfx_click, 0.45),
    "static": (sfx_static, 0.35),
    "riser": (sfx_riser, 0.35),
    "end": (sfx_end, 0.6),
}


# ---------------------------------------------------------------- music
def music_noir(dur, bpm=84):
    """Minor-key mystery bed: drone, slow pad, pizzicato motif, soft heartbeat."""
    t = _t(dur)
    beat = 60.0 / bpm
    bar = beat * 4
    out = np.zeros(len(t))

    # drone
    out += (np.sin(2 * np.pi * _note(38) * t) + 0.5 * np.sin(2 * np.pi * _note(45) * t)) * 0.18
    out += _lp(rng.standard_normal(len(t)), 300) * 0.05

    # pad: Dm - Bb - Gm - A, two bars each
    chords = [(50, 53, 57), (46, 50, 53), (43, 46, 50), (45, 49, 52)]
    pad = np.zeros(len(t))
    seg = 2 * bar
    for i in range(int(dur / seg) + 1):
        chord = chords[i % 4]
        a, b = int(i * seg * SR), int(min(dur, (i + 1) * seg) * SR)
        if a >= len(t):
            break
        tt = t[a:b] - i * seg
        env = np.minimum(1, tt / 0.8) * np.minimum(1, (seg - tt) / 0.8)
        for m in chord:
            for det in (-0.12, 0.12):
                f = _note(m) * 2 ** (det / 12)
                for h, amp in ((1, 1), (2, 0.35), (3, 0.15)):
                    pad[a:b] += np.sin(2 * np.pi * f * h * tt) * amp * env
    out += _lp(pad, 1400) * 0.05

    # pizzicato motif on eighth notes (sparse)
    motif = [62, None, 65, None, 69, 68, None, 65, 62, None, None, 60, 62, None, None, None]
    step = beat / 2
    pl = int(0.6 * SR)
    tp = np.arange(pl) / SR
    for i in range(int(dur / step)):
        m = motif[i % len(motif)]
        if m is None or i < 8:
            continue
        a = int(i * step * SR)
        f = _note(m)
        note = (np.sin(2 * np.pi * f * tp) + 0.3 * np.sin(4 * np.pi * f * tp)) * np.exp(-tp * 9)
        b = min(len(out), a + pl)
        out[a:b] += note[: b - a] * 0.11

    # heartbeat kick on beats 1 and 2-and
    kl = int(0.35 * SR)
    tk = np.arange(kl) / SR
    kick = np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 9)
    for i in range(int(dur / bar) + 1):
        for off, g in ((0, 0.3), (beat * 0.75, 0.18)):
            a = int((i * bar + off) * SR)
            if a >= len(out):
                continue
            b = min(len(out), a + kl)
            out[a:b] += kick[: b - a] * g

    fade = np.minimum(1, t / 1.0) * np.minimum(1, (dur - t) / 1.5)
    return out * fade


def resample(x, sr):
    if sr == SR:
        return x.astype(np.float64)
    from math import gcd
    g = gcd(SR, sr)
    return signal.resample_poly(x, SR // g, sr // g)


def mix(total, voice_clips, sfx_events, music="noir"):
    """voice_clips: [(start_s, samples, sr)]; sfx_events: [(start_s, name)]. Returns stereo float32."""
    n = int(total * SR) + SR
    voice = np.zeros(n)
    for start, x, sr in voice_clips:
        y = resample(x, sr)
        a = int(start * SR)
        voice[a: a + len(y)] += y[: n - a]
    voice = _norm(voice, 0.9)

    fx = np.zeros(n)
    for start, name in sfx_events:
        fn, gain = SFX[name]
        y = fn()
        a = int(start * SR)
        b = min(n, a + len(y))
        fx[a:b] += y[: b - a] * gain

    bed = np.zeros(n)
    if music:
        m = music_noir(total + 0.5)
        bed[: len(m)] = _norm(m, 0.5)
        # duck the music under the voice
        env = _lp(np.abs(voice), 8)
        env = np.clip(env / (np.max(env) or 1) * 4, 0, 1)
        bed *= 1 - 0.45 * env

    mono = voice + fx + bed * 0.55
    left = mono + 0.04 * np.roll(bed, 480)
    right = mono + 0.04 * np.roll(bed, -480)
    st = np.stack([left, right], axis=1)
    return (_norm(st, 0.95)).astype(np.float32)

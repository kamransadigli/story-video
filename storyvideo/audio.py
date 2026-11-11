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


def sfx_tick1(dur=0.3):
    t = _t(dur)
    c = _hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 200)
    tone = np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 60) * 0.6
    return _norm(c + tone, 0.8)


def sfx_thunder(dur=3.2):
    """Close lightning: sharp crack then a long rolling rumble."""
    t = _t(dur)
    crack = _hp(rng.standard_normal(len(t)), 1200) * np.exp(-t * 22)
    rumble_env = np.exp(-t * 1.1) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 1.7 * t + rng.uniform(0, 3))))
    rumble = _lp(rng.standard_normal(len(t)), 180, 4) * rumble_env * 3.0
    boom = np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-t * 8)) / SR) * np.exp(-t * 2.2) * 0.7
    att = np.minimum(1, t / 0.004)
    return _norm((crack * 0.8 + rumble + boom) * att, 0.95)


def ambience_rain_train(dur):
    """Rain on the windows + a train rolling on rails (rumble and clickety-clack)."""
    t = _t(dur)
    n = len(t)
    rain = _bp(rng.standard_normal(n), 900, 7000) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.23 * t))
    drops = np.zeros(n)
    for _ in range(int(dur * 25)):
        a = int(rng.uniform(0, dur) * SR)
        ln = int(0.012 * SR)
        if a + ln < n:
            drops[a:a + ln] += rng.standard_normal(ln) * np.exp(-np.arange(ln) / (0.002 * SR)) * rng.uniform(0.2, 0.6)
    rain = rain * 0.25 + _hp(drops, 2000) * 0.5
    rumble = _lp(rng.standard_normal(n), 120, 4) * 2.2 * (1 + 0.15 * np.sin(2 * np.pi * 0.9 * t))
    clack = np.zeros(n)
    cl = int(0.05 * SR)
    ct = np.arange(cl) / SR
    hit = _bp(rng.standard_normal(cl), 150, 1500) * np.exp(-ct * 60)
    period = 1.05
    k = 0
    while k * period < dur:
        for off, g in ((0.0, 1.0), (0.13, 0.8)):
            a = int((k * period + off) * SR)
            if a + cl < n:
                clack[a:a + cl] += hit * g
        k += 1
    return _norm(rain + rumble + clack * 0.9, 1.0)


def sfx_clink(dur=0.9):
    """Two glasses touching: bright inharmonic partials with a fast decay."""
    t = _t(dur)
    out = np.zeros(len(t))
    for start, g in ((0.0, 1.0), (0.11, 0.55)):
        tt = np.clip(t - start, 0, None)
        on = t >= start
        for f, d in ((2240, 7), (3190, 9), (4630, 12), (5870, 15), (7350, 18)):
            out += on * np.sin(2 * np.pi * f * tt) * np.exp(-tt * d) * g / (1 + f / 4000)
        out += on * _hp(rng.standard_normal(len(t)), 4000) * np.exp(-tt * 300) * 0.3 * g
    return _norm(out, 0.7)


def ambience_station_cold(dur):
    """Train idling at a frozen station: engine idle, muffled cold wind outside, heater hum inside."""
    t = _t(dur)
    n = len(t)
    idle = sum(np.sin(2 * np.pi * f * t + ph) * g for f, g, ph in ((41, 1.0, 0), (82, 0.5, 1.1), (123, 0.25, 2.3)))
    idle *= 1 + 0.08 * np.sin(2 * np.pi * 3.1 * t)
    idle = idle * 0.5 + _lp(rng.standard_normal(n), 140, 4) * 1.2
    gust = np.clip(0.5 + 0.5 * np.sin(2 * np.pi * 0.17 * t + 0.6) + 0.25 * np.sin(2 * np.pi * 0.41 * t), 0.15, 1.2)
    wind = _lp(_bp(rng.standard_normal(n), 150, 1400), 600, 2) * gust * 2.2
    heater = np.sin(2 * np.pi * 120 * t) * 0.12 + _bp(rng.standard_normal(n), 300, 2200) * 0.12
    return _norm(idle + wind + heater, 1.0)


def _harmonic(f_curve, n_harm=12, tilt=1.0):
    ph = 2 * np.pi * np.cumsum(f_curve) / SR
    return sum(np.sin(k * ph) / (k ** tilt) for k in range(1, n_harm + 1))


def sfx_growl(dur=1.5):
    """Small dog growl: low buzzy voice with rough amplitude flutter."""
    t = _t(dur)
    f = 95 + 12 * np.sin(2 * np.pi * 1.3 * t) + rng.normal(0, 4, len(t))
    f = _lp(f, 20)
    voice = _harmonic(f, 20, 0.8)
    rough = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 23 * t + 0.3 * np.sin(2 * np.pi * 3 * t)))
    breath = _bp(rng.standard_normal(len(t)), 300, 2500) * 0.35
    y = _bp(voice * rough + breath, 120, 1600)
    env = np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.25)
    return _norm(y * env, 0.8)


def sfx_bark(dur=0.75):
    """Two short yaps from a small terrier."""
    t = _t(dur)
    out = np.zeros(len(t))
    for start, g in ((0.0, 1.0), (0.32, 0.85)):
        tt = t - start
        on = (tt >= 0) & (tt < 0.2)
        tc = np.clip(tt, 0, 0.2)
        f = 620 - 900 * tc + 120 * np.exp(-tc * 60)
        y = _harmonic(f, 10, 1.1) + rng.standard_normal(len(t)) * 0.25 * np.exp(-tc * 25)
        env = np.minimum(1, tc / 0.008) * np.exp(-tc * 14)
        out += np.where(on, y * env * g, 0)
    out = _bp(out, 450, 3200)
    return _norm(out, 0.85)


def sfx_crackle(dur=0.6):
    """Lights failing: sharp electrical pops over a dying mains buzz."""
    t = _t(dur)
    buzz = (np.sin(2 * np.pi * 120 * t) + 0.5 * np.sin(2 * np.pi * 240 * t)) * np.exp(-t * 5) * 0.5
    pops = np.zeros(len(t))
    for _ in range(9):
        a = int(rng.uniform(0, dur * 0.7) * SR)
        ln = int(rng.uniform(0.004, 0.02) * SR)
        if a + ln < len(t):
            pops[a:a + ln] += rng.standard_normal(ln) * rng.uniform(0.5, 1.0)
    return _norm(buzz + _hp(pops, 1500), 0.8)


def sfx_hum_on(dur=0.9):
    """Lights coming back: relay click then a rising fluorescent hum."""
    t = _t(dur)
    click = _hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 150)
    hum = (np.sin(2 * np.pi * 120 * t) + 0.4 * np.sin(2 * np.pi * 360 * t)) * np.minimum(1, t / 0.15) * np.exp(-t * 2.5) * 0.4
    return _norm(click + hum, 0.7)


def sfx_clunk(dur=0.7):
    """Heavy little safe door: low metallic thud with a short ring."""
    t = _t(dur)
    thud = np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t * 12)
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((523, 9), (811, 12), (1290, 16))) * 0.25
    click = _hp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 120) * 0.6
    return _norm(thud + ring + click, 0.85)


SFX = {
    "clunk": (sfx_clunk, 0.55),
    "crackle": (sfx_crackle, 0.5),
    "hum_on": (sfx_hum_on, 0.4),
    "growl": (sfx_growl, 0.55),
    "bark": (sfx_bark, 0.6),
    "clink": (sfx_clink, 0.4),
    "tick": (sfx_tick, 0.5),
    "tick1": (sfx_tick1, 0.45),
    "thunder": (sfx_thunder, 0.85),
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


def make_babble(clips, total, seed=11):
    """Crowd murmur from TTS sentences: overlapped, muffled and smeared so no words are clear."""
    r = np.random.default_rng(seed)
    n = int(total * SR)
    out = np.zeros(n)
    pos = 0.0
    k = 0
    while pos < total:  # keep 3 overlapping talkers going for the whole video
        for lane in range(3):
            x, sr = clips[(k + lane) % len(clips)]
            y = resample(x, sr) * r.uniform(0.5, 1.0)
            a = int((pos + r.uniform(0, 1.2)) * SR) - int(r.uniform(0, 0.8) * len(y))
            a = max(a, 0)
            b = min(n, a + len(y))
            if b > a:
                out[a:b] += y[: b - a]
        pos += 1.6
        k += 3
    out = _lp(out, 1300, 4)
    out = _hp(out, 180)
    ir_t = np.arange(int(0.25 * SR)) / SR
    ir = r.standard_normal(len(ir_t)) * np.exp(-ir_t * 14)
    out = signal.fftconvolve(out, ir)[:n]
    return _norm(out, 1.0)


def mix(total, voice_clips, sfx_events, music="noir", music_volume=0.8, ambience=None, fades=True,
        babble=None, babble_volume=0.05, ambience_volume=0.16):
    """voice_clips: [(start_s, samples, sr)]; sfx_events: [(start_s, name)]. Returns stereo float32."""
    n = int(total * SR)
    voice = np.zeros(n)
    for start, x, sr in voice_clips:
        y = _norm(resample(x, sr), 0.9)  # level-match different voices
        a = int(start * SR)
        b = min(n, a + len(y))
        voice[a:b] += y[: b - a]
    voice = _norm(voice, 0.9)

    fx = np.zeros(n)
    for start, name in sfx_events:
        fn, gain = SFX[name]
        y = fn()
        a = int(start * SR)
        if a >= n:
            continue
        b = min(n, a + len(y))
        fx[a:b] += y[: b - a] * gain

    env = _lp(np.abs(voice), 8)
    env = np.clip(env / (np.max(env) or 1) * 4, 0, 1)
    bed = np.zeros(n)
    if music:
        m = music_noir(total + 0.5)
        if not fades:  # looping video: no fade-in/out, just a tiny edge ramp
            m = music_noir(total + 3.0)[int(1.5 * SR):]
        bed[:] = _norm(m, 0.5)[:n]
        bed *= 1 - 0.35 * env
    amb = np.zeros(n)
    if ambience == "rain_train":
        amb = ambience_rain_train(total) * ambience_volume * (1 - 0.3 * env)
    elif ambience == "station_cold":
        amb = ambience_station_cold(total) * ambience_volume * (1 - 0.3 * env)

    if babble is not None:
        amb = amb + babble[:n] * babble_volume * (1 - 0.4 * env)
    mono = voice + fx + bed * music_volume + amb
    left = mono + 0.04 * np.roll(bed, 480) + 0.03 * np.roll(amb, 240)
    right = mono + 0.04 * np.roll(bed, -480) - 0.03 * np.roll(amb, 240)
    st = np.stack([left, right], axis=1)
    if not fades:
        edge = int(0.01 * SR)
        st[:edge] *= np.linspace(0, 1, edge)[:, None]
        st[-edge:] *= np.linspace(1, 0, edge)[:, None]
    return (_norm(st, 0.95)).astype(np.float32)

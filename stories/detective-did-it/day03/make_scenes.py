"""Build Day 3 scenes + story.json.  Usage: python3 make_scenes.py [A|B] [detective name]
Only opening A is drawn for now (Day 2 winner)."""
import json, math, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERIES = HERE.parent
OPENING = (sys.argv[1] if len(sys.argv) > 1 else "A").upper()
NAME = sys.argv[2] if len(sys.argv) > 2 else "DET. R. COLE"
WITNESS = "@marckyy"
INK = "#15141f"

base = (SERIES.parent / "ice-doesnt-lie/scenes/_defs.svg").read_text().rstrip()[:-len("</defs>")]
chars = (SERIES / "characters.svg").read_text()
props = (SERIES / "series_props.svg").read_text()
def variant(src, old_id, new_id, repl):
    i = src.index(f'<symbol id="{old_id}"'); j = src.index('</symbol>', i) + 9
    blk = src[i:j].replace(f'id="{old_id}"', f'id="{new_id}"')
    for a, b in repl: blk = blk.replace(a, b)
    return blk
# detective with WIDE eyes for the extreme close-up
wide_eyes = ('<ellipse cx="258" cy="248" rx="30" ry="27" fill="#fff" stroke="#15141f" stroke-width="3"/><ellipse cx="342" cy="248" rx="30" ry="27" fill="#fff" stroke="#15141f" stroke-width="3"/>'
             '<circle cx="258" cy="250" r="7" fill="#3a2a1a"/><circle cx="342" cy="250" r="7" fill="#3a2a1a"/><circle cx="260" cy="247" r="2.4" fill="#fff"/><circle cx="344" cy="247" r="2.4" fill="#fff"/>'
             '<path d="M226 206 C242 194 268 194 284 204 M316 204 C332 194 358 194 374 206" fill="none" stroke="#2c2420" stroke-width="9" stroke-linecap="round"/>')
det = chars[chars.index('<symbol id="detective"'):chars.index('</symbol>', chars.index('<symbol id="detective"')) + 9]
eyes_start = det.index('<ellipse cx="258" cy="250" rx="24" ry="15"')
eyes_end = det.index('<path d="M270 336')
det_wide = det[:eyes_start] + wide_eyes + det[eyes_end:]
det_wide = det_wide.replace('id="detective"', 'id="detectiveWide"')
extra = f'''
  <symbol id="monitor" viewBox="0 0 700 520" overflow="visible">
    <rect x="0" y="0" width="700" height="440" rx="24" fill="#2a2d34" stroke="{INK}" stroke-width="8"/>
    <rect x="26" y="26" width="648" height="388" rx="10" fill="#eaf4ff"/>
    <rect x="300" y="440" width="100" height="50" fill="#3a3d44"/><rect x="220" y="488" width="260" height="24" rx="8" fill="#3a3d44" stroke="{INK}" stroke-width="4"/>
  </symbol>
  <symbol id="clockFace" viewBox="0 0 200 200" overflow="visible">
    <circle cx="100" cy="100" r="92" fill="#fbf7ef" stroke="{INK}" stroke-width="8"/>
    <g stroke="{INK}" stroke-width="6" stroke-linecap="round">{''.join(f'<line x1="{100+78*math.sin(a*math.pi/6):.1f}" y1="{100-78*math.cos(a*math.pi/6):.1f}" x2="{100+64*math.sin(a*math.pi/6):.1f}" y2="{100-64*math.cos(a*math.pi/6):.1f}"/>' for a in range(12))}</g>
  </symbol>
'''
(HERE / "scenes/_defs.svg").write_text(base + chars + det_wide + props + extra + "\n</defs>")

def svg(body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">\n{body}\n  <rect width="1080" height="1920" filter="url(#grit)"/>\n</svg>\n'
def clock(x, y, size, hour, minute):
    ha = (hour % 12 + minute / 60) * 30; ma = minute * 6; c = x + size / 2; d = y + size / 2; k = size / 200
    return (f'<use href="#clockFace" x="{x}" y="{y}" width="{size}" height="{size}"/>'
            f'<line x1="{c}" y1="{d}" x2="{c+46*k*math.sin(math.radians(ha)):.0f}" y2="{d-46*k*math.cos(math.radians(ha)):.0f}" stroke="{INK}" stroke-width="{12*k:.0f}" stroke-linecap="round"/>'
            f'<line x1="{c}" y1="{d}" x2="{c+70*k*math.sin(math.radians(ma)):.0f}" y2="{d-70*k*math.cos(math.radians(ma)):.0f}" stroke="{INK}" stroke-width="{7*k:.0f}" stroke-linecap="round"/>'
            f'<circle cx="{c}" cy="{d}" r="{8*k:.0f}" fill="#c8102e"/>')
office = f'''  <rect width="1080" height="1920" fill="#f4e6c8"/>
  <rect x="80" y="300" width="900" height="520" fill="url(#daySky)" stroke="{INK}" stroke-width="6"/>
  <rect x="520" y="300" width="16" height="520" fill="#c9a24a"/>
  <ellipse cx="540" cy="700" rx="700" ry="700" fill="#fff6dc" opacity="0.4" filter="url(#blur)"/>
  <rect x="0" y="1240" width="1080" height="680" fill="#a8743e"/>'''
S = HERE / "scenes"
# 01: face lit by a computer screen (cool glow on one side), bright office
S.joinpath("01-face.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#f2d6a8"/>
  <circle cx="120" cy="1300" r="360" fill="url(#lamp)" opacity="0.8"/>
  <rect x="0" y="1240" width="1080" height="680" fill="#a8743e"/>
  <use href="#detective" x="-420" y="150" width="1720" height="2179"/>
  <ellipse cx="1080" cy="820" rx="260" ry="700" fill="#bfe3ff" opacity="0.3" filter="url(#blur)"/>
  <ellipse cx="300" cy="860" rx="500" ry="600" fill="url(#lamp)" opacity="0.3"/>'''))
# 02: screen with the badge log (the 2:13 row is an overlay so it can vanish)
rows = [("23:58", "J. PATEL"), ("00:41", "M. ORTIZ"), ("", ""), ("06:30", "S. BRUNO")]
row_svg = "".join(f'<text x="150" y="{690+i*92}" font-family="Typewriter" font-size="40" fill="#3a3a44">{t}   {n}</text>' for i, (t, n) in enumerate(rows) if t)
S.joinpath("02-screen.svg").write_text(svg(f'''{office}
  <use href="#monitor" x="40" y="440" width="1000" height="743"/>
  <text x="130" y="600" font-family="Oswald" font-weight="700" font-size="48" fill="{INK}">BADGE LOG · EVIDENCE ROOM</text>
  <rect x="130" y="620" width="760" height="5" fill="{INK}"/>
  {row_svg}
  <!-- empty slot where the 2:13 row sits -->
  <rect x="130" y="806" width="760" height="70" fill="none" stroke="#c9d6e2" stroke-width="3" stroke-dasharray="10 8"/>
  <!-- DELETE button -->
  <rect x="640" y="960" width="230" height="74" rx="12" fill="#c8102e" stroke="{INK}" stroke-width="5"/>
  <text x="755" y="1012" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="40" fill="#fff">DELETE</text>
  <path d="M770 1010 L770 1070 L786 1056 L798 1082 L810 1076 L798 1050 L818 1048 Z" fill="#fff" stroke="{INK}" stroke-width="4"/>'''))
S.joinpath("03-mia-screen.svg").write_text(svg(f'''{office}
  <use href="#miaWorried" x="-80" y="380" width="760" height="963"/>
  <g transform="rotate(4 820 860)"><use href="#monitor" x="580" y="700" width="420" height="312"/></g>
  <text x="790" y="860" text-anchor="middle" font-family="Typewriter" font-size="30" fill="#c8102e" transform="rotate(4 820 860)">2:13 — DELETED</text>'''))
S.joinpath("04-lobby.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#e9eef0"/>
  <rect x="0" y="0" width="1080" height="130" fill="#2a4c7a"/>
  <text x="459" y="95" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="64" fill="#fff" letter-spacing="10">POLICE</text>
  <g fill="#ffffff" filter="url(#glow)"><rect x="140" y="160" width="300" height="22" rx="10"/><rect x="560" y="160" width="300" height="22" rx="10"/></g>
  <rect x="640" y="300" width="300" height="760" fill="url(#daySky)" stroke="{INK}" stroke-width="6"/>
  <rect x="784" y="300" width="12" height="760" fill="#9aa3a8"/>
  <rect x="0" y="1060" width="1080" height="860" fill="#c9b48a"/>
  <rect x="40" y="980" width="520" height="160" fill="#7a5a3a" stroke="{INK}" stroke-width="6"/>
  <use href="#marckyy" x="180" y="420" width="700" height="887"/>
  <!-- visitor badge, big and readable -->
  <g transform="rotate(-4 460 1020)">
    <rect x="300" y="940" width="330" height="170" rx="16" fill="#ffffff" stroke="{INK}" stroke-width="6"/>
    <rect x="300" y="940" width="330" height="54" rx="12" fill="#ffd640" stroke="{INK}" stroke-width="5"/>
    <text x="465" y="980" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="36" fill="{INK}">WITNESS:</text>
    <text x="465" y="1062" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="54" fill="#c8102e">{WITNESS}</text>
    <path d="M465 900 L465 940" stroke="{INK}" stroke-width="6"/>
  </g>'''))
lobby_bg = '''  <rect width="1080" height="1920" fill="#e9eef0"/>
  <rect x="640" y="300" width="300" height="760" fill="url(#daySky)" stroke="#15141f" stroke-width="6"/>
  <rect x="0" y="1060" width="1080" height="860" fill="#c9b48a"/>'''
S.joinpath("05-marc-close.svg").write_text(svg(f'''{lobby_bg}
  <ellipse cx="459" cy="900" rx="600" ry="700" fill="url(#lamp)" opacity="0.4"/>
  <use href="#marckyy" x="-360" y="260" width="1640" height="2077"/>'''))
S.joinpath("06-marc-point.svg").write_text(svg(f'''{lobby_bg}
  <use href="#marckyy" x="-120" y="380" width="900" height="1140"/>
  <path d="M600 1080 C700 980 800 900 880 860" stroke="{INK}" stroke-width="76" stroke-linecap="round"/>
  <path d="M600 1080 C700 980 800 900 880 860" stroke="#2f8a5a" stroke-width="62" stroke-linecap="round"/>
  <path d="M870 830 L960 800 C978 796 982 818 966 824 L896 870 Z" fill="#cf9670" stroke="{INK}" stroke-width="5"/>
  <circle cx="880" cy="860" r="34" fill="#cf9670" stroke="{INK}" stroke-width="5"/>
  <!-- edge of the detective's grey suit, right side -->
  <path d="M900 700 L1080 640 L1080 1920 L860 1920 Z" fill="#6e737c" stroke="{INK}" stroke-width="6"/>'''))
# 07a: extreme close-up of the eyes widening
S.joinpath("07a-eyes.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#d6a07a"/>
  <svg x="-200" y="560" width="1480" height="740" viewBox="200 196 200 100" preserveAspectRatio="xMidYMid slice"><use href="#detectiveWide" width="600" height="760"/></svg>
  <ellipse cx="459" cy="900" rx="700" ry="500" fill="url(#lamp)" opacity="0.25"/>'''))
# 07b: the two clocks
S.joinpath("07b-clocks.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#f2d6a8"/>
  <ellipse cx="459" cy="860" rx="620" ry="620" fill="url(#lamp)" opacity="0.5"/>
  {clock(60, 560, 380, 11, 30)}
  {clock(500, 560, 380, 12, 0)}
  <path d="M440 750 L500 750" stroke="#c8102e" stroke-width="10" stroke-dasharray="14 10"/>'''))
S.joinpath("08-choice.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#f2d6a8"/>
  <ellipse cx="460" cy="700" rx="600" ry="600" fill="url(#lamp)" opacity="0.4"/>
  <clipPath id="pA"><rect x="20" y="320" width="878" height="350" rx="30"/></clipPath>
  <clipPath id="pB"><rect x="20" y="700" width="878" height="350" rx="30"/></clipPath>
  <rect x="20" y="320" width="878" height="350" rx="30" fill="#f6c1a8"/>
  <g clip-path="url(#pA)">{clock(730, 380, 150, 11, 30)}<text x="805" y="590" text-anchor="middle" font-family="Marker" font-size="64" fill="#c8102e">?</text></g>
  <rect x="20" y="320" width="878" height="350" rx="30" fill="none" stroke="{INK}" stroke-width="6"/>
  <rect x="20" y="700" width="878" height="350" rx="30" fill="#bcd6ea"/>
  <g clip-path="url(#pB)" transform="rotate(6 800 880)">
    <rect x="720" y="740" width="160" height="210" fill="#fff" stroke="{INK}" stroke-width="4"/>
    <text x="800" y="780" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="22" fill="{INK}">STATEMENT</text>
    <g fill="#9aa3a8"><rect x="736" y="800" width="128" height="8"/><rect x="736" y="825" width="128" height="8"/><rect x="736" y="850" width="100" height="8"/></g>
    <path d="M720 740 L880 950 M880 740 L720 950" stroke="#c8102e" stroke-width="14" stroke-linecap="round"/>
  </g>
  <rect x="20" y="700" width="878" height="350" rx="30" fill="none" stroke="{INK}" stroke-width="6"/>'''))

choice = [
 {"type": "label", "text": "A", "x": 110, "y": 420, "size": 120},
 {"text": "FIND OUT WHAT", "x": 420, "y": 395, "size": 52, "max_w": 560, "start": 0.3},
 {"text": "HAPPENED AT 11:30", "x": 420, "y": 458, "size": 52, "max_w": 560, "start": 0.3},
 {"text": "🚨 +15%", "x": 420, "y": 555, "size": 56, "color": [255, 92, 92], "start": 0.6},
 {"text": "Mia might follow you", "x": 420, "y": 625, "size": 36, "color": [255, 214, 64], "start": 0.6},
 {"type": "label", "text": "B", "x": 110, "y": 800, "size": 120},
 {"text": "MAKE THE STATEMENT", "x": 470, "y": 780, "size": 44, "max_w": 600, "start": 2.0},
 {"text": "DISAPPEAR", "x": 470, "y": 838, "size": 44, "max_w": 600, "start": 2.0},
 {"text": "🚨 −20% · 🧾 +1", "x": 450, "y": 935, "size": 52, "color": [255, 92, 92], "start": 2.3},
 {"text": "(another crime)", "x": 450, "y": 1000, "size": 36, "color": [255, 214, 64], "start": 2.3},
 {"text": "Comment WITNESS", "y": 1225, "size": 56, "color": [255, 214, 64], "start": 6.0},
 {"text": "to appear in Day 4 👀", "y": 1292, "size": 42, "start": 6.0}]
log_row = [{"text": f"2:13 AM   {NAME}", "y": 841, "size": 46, "color": [200, 16, 46], "pop": False, "end": 1.55},
           {"text": "✔ DELETED", "y": 841, "size": 46, "color": [120, 200, 140], "start": 1.6}]
story = {
 "title": "The Detective Did It — Day 3", "voice": "am_michael", "speed": 1.08,
 "music": "noir", "music_volume": 0.7, "ambience": "rain_train", "ambience_volume": 0.07,
 "fade": False, "vignette": 90,
 "layout": {"cx": 459, "max_w": 820, "cap_chars": 14},
 "stakes": {"y": 228, "width": 880, "show_from": 2.2,
            "start": {"suspicion": 15, "evidence": 3, "trust": 100},
            "changes": [{"at": 3.7, "suspicion": 40}, {"at": 4.0, "evidence": 2},
                        {"at": 14.9, "suspicion": 60, "flash": [255, 60, 60]}]},
 "lines": [
  {"at": 0.05, "text": "You told me to break in. So I did.", "speed": 1.1, "caption_y": 1240},
  {"at": 2.4, "text": "One click. My name… gone.", "say": "One click. My name... gone.", "caption_y": 1160},
  {"at": 5.2, "text": "Someone deleted the 2:13 entry. Who does that?", "say": "Someone deleted the two thirteen entry. Who does that?", "voice": "af_bella", "speed": 1.0, "caption_y": 1150},
  {"at": 8.7, "text": "Then the witness walked in. The guy who called it in.", "caption_y": 1290},
  {"at": 11.7, "text": "I heard a crash at 11:30. Then around midnight, a man in a grey suit showed up.", "say": "I heard a crash at eleven thirty. Then around midnight, a man in a grey suit showed up.", "voice": "am_puck", "caption_y": 1240},
  {"at": 16.75, "text": "…Kinda like yours.", "say": "Kinda like yours.", "voice": "am_puck", "speed": 1.0, "caption_y": 1240},
  {"at": 18.2, "text": "11:30? I didn't get there until midnight. So what happened… before me?", "say": "Eleven thirty? I didn't get there until midnight. So what happened... before me?", "speed": 1.1, "caption_y": 1240},
  {"at": 22.8, "text": "A: find out what happened at 11:30. B: make his statement disappear. Comment A or B. Send this to the friend who notices everything.", "say": "A: find out what happened at eleven thirty. B: make his statement disappear. Comment A or B. Send this to the friend who notices everything.", "speed": 1.1, "caption_y": 1110}],
 "shots": [
  {"id": "01", "duration": 2.2, "svg": "scenes/01-face.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.45, 0.42], "c1": [0.45, 0.42], "ease": "linear"}, "punch": False,
   "overlays": [{"text": "DAY 3", "y": 250, "size": 72, "color": [255, 214, 64], "pop": False},
                {"text": "YOU TOLD ME", "y": 355, "size": 80, "pop": False},
                {"text": "TO BREAK IN.", "y": 455, "size": 96, "color": [255, 92, 92], "pop": False}], "sfx": "hit"},
  {"id": "02", "duration": 2.8, "svg": "scenes/02-screen.svg", "motion": {"z0": 1.0, "z1": 1.02, "c0": [0.5, 0.5], "c1": [0.5, 0.5], "ease": "linear"}, "punch": False,
   "overlays": log_row, "sfx": [{"name": "click", "at": 1.5}, {"name": "whoosh", "at": 0}]},
  {"id": "03", "duration": 3.6, "svg": "scenes/03-mia-screen.svg", "motion": {"z0": 1.0, "z1": 1.07, "c0": [0.45, 0.45], "c1": [0.45, 0.42]}, "fx": ["sway"], "sfx": "whoosh"},
  {"id": "04", "duration": 3.0, "svg": "scenes/04-lobby.svg", "motion": {"z0": 1.0, "z1": 1.06, "c0": [0.47, 0.5], "c1": [0.47, 0.5]}, "sfx": "whoosh"},
  {"id": "05", "duration": 5.0, "svg": "scenes/05-marc-close.svg", "motion": {"z0": 1.0, "z1": 1.04, "c0": [0.5, 0.5], "c1": [0.5, 0.5], "ease": "linear"}, "punch": False,
   "overlays": [{"text": "🕦 11:30", "x": 250, "y": 420, "size": 84, "color": [255, 214, 64], "start": 1.05},
                {"text": "🕛 MIDNIGHT", "x": 600, "y": 520, "size": 76, "color": [255, 92, 92], "start": 2.15}],
   "sfx": "whoosh"},
  {"id": "06", "duration": 1.4, "svg": "scenes/06-marc-point.svg", "motion": {"z0": 1.0, "z1": 1.1, "c0": [0.5, 0.5], "c1": [0.58, 0.48], "ease": "out"}, "sfx": "hit"},
  {"id": "07a", "duration": 1.4, "svg": "scenes/07a-eyes.svg", "motion": {"z0": 1.0, "z1": 1.15, "c0": [0.5, 0.47], "c1": [0.5, 0.47], "ease": "out"}, "punch": False,
   "flashes": [{"at": 0.0, "peak": 0.35, "decay": 0.25}], "sfx": "hit"},
  {"id": "07b", "duration": 3.2, "svg": "scenes/07b-clocks.svg", "motion": {"z0": 1.0, "z1": 1.06, "c0": [0.45, 0.42], "c1": [0.45, 0.42]},
   "overlays": [{"text": "11:30", "x": 250, "y": 1020, "size": 72, "color": [255, 214, 64], "start": 0.1},
                {"text": "12:00", "x": 690, "y": 1020, "size": 72, "color": [255, 92, 92], "start": 0.5}],
   "sfx": [{"name": "tick", "at": 0.1}]},
  {"id": "08", "duration": 10.4, "svg": "scenes/08-choice.svg", "motion": {"z0": 1.0, "z1": 1.03, "c0": [0.5, 0.5], "c1": [0.5, 0.5], "ease": "linear"}, "punch": False,
   "overlays": choice, "sfx": "hit"}]}
(HERE / "story.json").write_text(json.dumps(story, indent=2, ensure_ascii=False))
who = {"af_bella": "MIA", "am_puck": "@marckyy"}
(HERE / "transcript.txt").write_text("\n".join(f"[{ln['at']:05.2f}s] {who.get(ln.get('voice'), 'DETECTIVE (VO)')}: {ln['text']}" for ln in story["lines"]) + "\n")
print("built opening", OPENING, "name", NAME)

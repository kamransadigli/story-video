"""Build Day 2 scenes + story.json.  Usage: python3 make_scenes.py <X percent> <witness1> [witness2 ...]"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERIES = HERE.parent
X = sys.argv[1] if len(sys.argv) > 1 else "62"
WITNESSES = sys.argv[2:] or ["@witness1", "@witness2"]
INK = "#15141f"
NUM_WORDS = {str(n): w for n, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen".split())}
TENS = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty", 6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}
def spoken(n):
    n = int(n)
    if n < 20: return NUM_WORDS[str(n)]
    if n == 100: return "one hundred"
    t, o = divmod(n, 10)
    return TENS[t] + ("" if o == 0 else "-" + NUM_WORDS[str(o)])

base = (SERIES.parent / "ice-doesnt-lie/scenes/_defs.svg").read_text().rstrip()[:-len("</defs>")]
chars = (SERIES / "characters.svg").read_text()
props = (SERIES / "series_props.svg").read_text()
sweat = ''.join(f'<path d="M{x} {y} C{x+6} {y+14} {x+10} {y+22} {x+2} {y+28} C{x-6} {y+30} {x-10} {y+20} {x} {y} Z" fill="#9fdcff" stroke="#15141f" stroke-width="2.5"/>' for x, y in [(222, 170), (380, 164), (300, 140), (404, 230)])
det_sweat = chars[chars.index('<symbol id="detective"'):chars.index('</symbol>', chars.index('<symbol id="detective"')) + 9]
det_sweat = det_sweat.replace('id="detective"', 'id="detectiveSweat"').replace('</symbol>', sweat + '</symbol>')
new_props = f'''
  <symbol id="evBagEmpty" viewBox="0 0 300 380" overflow="visible">
    <rect x="10" y="10" width="280" height="360" rx="14" fill="#e8f2f8" fill-opacity="0.85" stroke="{INK}" stroke-width="6"/>
    <rect x="10" y="10" width="280" height="56" rx="10" fill="#c8102e" stroke="{INK}" stroke-width="5"/>
    <text x="150" y="50" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="32" fill="#fff">EVIDENCE</text>
    <rect x="40" y="300" width="220" height="44" fill="#fff" stroke="{INK}" stroke-width="3"/>
    <g fill="#9aa3a8"><rect x="54" y="312" width="140" height="6"/><rect x="54" y="326" width="100" height="6"/></g>
    <text x="150" y="200" text-anchor="middle" font-family="Marker" font-size="44" fill="#c8102e" transform="rotate(-8 150 190)">EMPTY</text>
  </symbol>
  <symbol id="wallclock" viewBox="0 0 200 200" overflow="visible">
    <circle cx="100" cy="100" r="92" fill="#fbf7ef" stroke="{INK}" stroke-width="8"/>
    <g stroke="{INK}" stroke-width="6" stroke-linecap="round">{''.join(f'<line x1="{100+78*__import__("math").sin(a*__import__("math").pi/6):.1f}" y1="{100-78*__import__("math").cos(a*__import__("math").pi/6):.1f}" x2="{100+66*__import__("math").sin(a*__import__("math").pi/6):.1f}" y2="{100-66*__import__("math").cos(a*__import__("math").pi/6):.1f}"/>' for a in range(12))}</g>
  </symbol>
  <symbol id="cork" viewBox="0 0 1080 1920"><rect width="1080" height="1920" fill="url(#cork)"/></symbol>
'''
def clock(x, y, size, hour, minute):
    import math
    ha = (hour % 12 + minute / 60) * 30; ma = minute * 6
    c = x + size / 2; d = y + size / 2; k = size / 200
    hx = c + 46 * k * math.sin(math.radians(ha)); hy = d - 46 * k * math.cos(math.radians(ha))
    mx = c + 70 * k * math.sin(math.radians(ma)); my = d - 70 * k * math.cos(math.radians(ma))
    return (f'<use href="#wallclock" x="{x}" y="{y}" width="{size}" height="{size}"/>'
            f'<line x1="{c}" y1="{d}" x2="{hx:.0f}" y2="{hy:.0f}" stroke="{INK}" stroke-width="{12*k:.0f}" stroke-linecap="round"/>'
            f'<line x1="{c}" y1="{d}" x2="{mx:.0f}" y2="{my:.0f}" stroke="{INK}" stroke-width="{7*k:.0f}" stroke-linecap="round"/>'
            f'<circle cx="{c}" cy="{d}" r="{8*k:.0f}" fill="#c8102e"/>')
(HERE / "scenes/_defs.svg").write_text(base + chars + det_sweat + props + new_props + "\n</defs>")

def svg(body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">\n{body}\n  <rect width="1080" height="1920" filter="url(#grit)"/>\n</svg>\n'
S = HERE / "scenes"
S.joinpath("01-face.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#f2d6a8"/>
  <circle cx="120" cy="1300" r="360" fill="url(#lamp)" opacity="0.8"/>
  <circle cx="900" cy="500" r="300" fill="url(#lamp)" opacity="0.6"/>
  <use href="#detective" x="-420" y="150" width="1720" height="2179"/>
  <ellipse cx="380" cy="860" rx="560" ry="640" fill="url(#lamp)" opacity="0.4"/>'''))
# evidence room, bright fluorescent lights, 2:00 AM clock, hand slides bag into coat pocket
shelves = ''.join(f'<rect x="{x}" y="{y}" width="150" height="110" rx="6" fill="{c}" stroke="{INK}" stroke-width="4"/><rect x="{x+40}" y="{y+40}" width="70" height="28" fill="#fbf7ef" stroke="{INK}" stroke-width="2"/>'
                  for (x, y), c in zip([(60,420),(230,420),(400,420),(60,620),(230,620),(400,620),(60,820),(230,820)], ["#c9a676","#b8955e","#d4b483","#b8955e","#c9a676","#d4b483","#c9a676","#b8955e"]))
S.joinpath("02-evroom.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#e8eef0"/>
  <rect x="0" y="0" width="1080" height="120" fill="#c8d2d6"/>
  <g fill="#ffffff" filter="url(#glow)"><rect x="120" y="40" width="340" height="30" rx="10"/><rect x="620" y="40" width="340" height="30" rx="10"/></g>
  <rect x="40" y="380" width="560" height="660" fill="#7a848e" stroke="{INK}" stroke-width="6"/>
  <g stroke="{INK}" stroke-width="6"><line x1="40" y1="540" x2="600" y2="540"/><line x1="40" y1="740" x2="600" y2="740"/><line x1="40" y1="940" x2="600" y2="940"/></g>
  {shelves}
  {clock(660, 360, 230, 2, 0)}
  <text x="775" y="640" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="54" fill="#c8102e">2:00 AM</text>
  <rect x="0" y="1060" width="1080" height="860" fill="#b9c3c8"/>
  <!-- coat with pocket, hand sliding the evidence bag in -->
  <path d="M120 1920 L180 1100 C300 1040 700 1040 820 1100 L880 1920 Z" fill="#6e737c" stroke="{INK}" stroke-width="6"/>
  <path d="M300 1250 L640 1250 L620 1420 L320 1420 Z" fill="#5c6068" stroke="{INK}" stroke-width="6"/>
  <g transform="rotate(-14 470 1180)"><use href="#evBag" x="370" y="930" width="220" height="279"/></g>
  <path d="M296 1252 L644 1252" stroke="{INK}" stroke-width="9"/>
  <path d="M560 1090 C640 1060 700 1080 720 1130 C700 1170 640 1180 590 1160 Z" fill="#d6a07a" stroke="{INK}" stroke-width="5"/>
  <path d="M700 1100 L900 960" stroke="{INK}" stroke-width="80" stroke-linecap="round"/><path d="M700 1100 L900 960" stroke="#6e737c" stroke-width="66" stroke-linecap="round"/>'''))
office_bg = f'''  <rect width="1080" height="1920" fill="#f4e6c8"/>
  <rect x="80" y="300" width="900" height="560" fill="url(#daySky)" stroke="{INK}" stroke-width="6"/>
  <rect x="520" y="300" width="16" height="560" fill="#c9a24a"/>
  <circle cx="820" cy="420" r="70" fill="#fff6c4"/>
  <ellipse cx="540" cy="700" rx="700" ry="700" fill="#fff6dc" opacity="0.4" filter="url(#blur)"/>
  <rect x="0" y="1240" width="1080" height="680" fill="#a8743e"/>'''
S.joinpath("03-mia-empty.svg").write_text(svg(f'''{office_bg}
  <use href="#miaWorried" x="-60" y="420" width="760" height="963"/>
  <g transform="rotate(6 600 820)"><use href="#evBagEmpty" x="440" y="600" width="320" height="405"/></g>
  <circle cx="520" cy="1000" r="40" fill="#e0b08a" stroke="{INK}" stroke-width="5"/>'''))
log_rows = [("21:47", "BADGE SWIPE", False), ("23:02", "BADGE SWIPE", False), ("", "BADGE SWIPE — 2:13 AM", True), ("06:30", "BADGE SWIPE", False)]
rows = ""
for i, (tm, lab, hi) in enumerate(log_rows):
    y = 700 + i * 120
    if hi:
        rows += f'<rect x="150" y="{y-62}" width="720" height="92" rx="8" fill="#ffe14a" opacity="0.95"/>'
        rows += f'<text x="510" y="{y}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="64" fill="#c8102e">{lab}</text>'
    else:
        rows += f'<text x="190" y="{y}" font-family="Typewriter" font-size="44" fill="#4a4a52">{tm}   {lab}</text>'
S.joinpath("04-log.svg").write_text(svg(f'''{office_bg}
  <use href="#mia" x="-250" y="200" width="700" height="887"/>
  <g transform="rotate(-2 510 820)">
    <rect x="120" y="480" width="780" height="660" rx="10" fill="#ffffff" stroke="{INK}" stroke-width="6" filter="url(#shadow)"/>
    <text x="510" y="560" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="46" fill="{INK}">DOOR LOG · EVIDENCE ROOM</text>
    <rect x="160" y="580" width="700" height="4" fill="{INK}"/>
    {rows}
  </g>
  <!-- Mia's pointing hand -->
  <path d="M-20 1200 C20 1080 60 980 90 930" stroke="{INK}" stroke-width="66" stroke-linecap="round"/><path d="M-20 1200 C20 1080 60 980 90 930" stroke="#c9a676" stroke-width="54" stroke-linecap="round"/>
  <path d="M90 900 L150 905 C166 906 166 926 150 928 L96 932 Z" fill="#e0b08a" stroke="{INK}" stroke-width="5"/>
  <circle cx="92" cy="925" r="32" fill="#e0b08a" stroke="{INK}" stroke-width="5"/>'''))
# case board with witness cards
cards = ""
n = len(WITNESSES)
for i, w in enumerate(WITNESSES[:3]):
    cx = [300, 640, 470][i] if n > 1 else 470
    cy = [700, 760, 1010][i] if n > 1 else 760
    rot = [-4, 5, -2][i]
    cards += f'''<g transform="rotate({rot} {cx} {cy})" filter="url(#shadowSm)">
      <rect x="{cx-170}" y="{cy-180}" width="340" height="360" fill="#fbf7ef" stroke="{INK}" stroke-width="5"/>
      <rect x="{cx-140}" y="{cy-150}" width="280" height="210" fill="#9aa3a8"/>
      <circle cx="{cx}" cy="{cy-75}" r="50" fill="#2b2833"/><path d="M{cx-90} {cy+60} C{cx-90} {cy-10} {cx+90} {cy-10} {cx+90} {cy+60} Z" fill="#2b2833"/>
      <text x="{cx}" y="{cy-60}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="80" fill="#ffd640">?</text>
      <text x="{cx}" y="{cy+108}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="40" fill="#c8102e">WITNESS:</text>
      <text x="{cx}" y="{cy+160}" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="{min(56, int(560 / max(len(w), 1)))}" fill="{INK}">{w}</text>
    </g><use href="#pin" x="{cx-20}" y="{cy-205}" width="40" height="46"/>'''
S.joinpath("05-board.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#f4e6c8"/>
  <rect x="40" y="380" width="880" height="900" rx="12" fill="url(#wood)" stroke="{INK}" stroke-width="6"/>
  <rect x="66" y="406" width="828" height="848" fill="url(#cork)"/>
  <ellipse cx="470" cy="800" rx="560" ry="600" fill="url(#lamp)" opacity="0.5"/>
  <g stroke="#d0142f" stroke-width="5"><line x1="300" y1="520" x2="640" y2="580"/><line x1="300" y1="520" x2="470" y2="830"/></g>
  {cards}
  <rect x="0" y="1290" width="1080" height="630" fill="#a8743e"/>'''))
S.joinpath("06-sweat.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#f2d6a8"/>
  {clock(640, 330, 260, 9, 15)}
  <circle cx="120" cy="1300" r="360" fill="url(#lamp)" opacity="0.8"/>
  <use href="#detectiveSweat" x="-300" y="300" width="1400" height="1773"/>
  <ellipse cx="380" cy="860" rx="560" ry="640" fill="url(#lamp)" opacity="0.35"/>'''))
S.joinpath("07-choice.svg").write_text(svg(f'''  <rect width="1080" height="1920" fill="#f2d6a8"/>
  <ellipse cx="460" cy="700" rx="600" ry="600" fill="url(#lamp)" opacity="0.4"/>
  <clipPath id="pA"><rect x="20" y="320" width="878" height="350" rx="30"/></clipPath>
  <clipPath id="pB"><rect x="20" y="700" width="878" height="350" rx="30"/></clipPath>
  <rect x="20" y="320" width="878" height="350" rx="30" fill="#f6c1a8"/>
  <g clip-path="url(#pA)" transform="rotate(6 800 500)">
    <rect x="720" y="360" width="160" height="210" fill="#fff" stroke="{INK}" stroke-width="4"/>
    <g fill="#9aa3a8"><rect x="736" y="390" width="128" height="8"/><rect x="736" y="420" width="128" height="8"/><rect x="736" y="480" width="128" height="8"/></g>
    <rect x="732" y="440" width="136" height="24" fill="#ffe14a"/>
    <path d="M720 360 L880 570 M880 360 L720 570" stroke="#c8102e" stroke-width="16" stroke-linecap="round"/>
  </g>
  <rect x="20" y="320" width="878" height="350" rx="30" fill="none" stroke="{INK}" stroke-width="6"/>
  <rect x="20" y="700" width="878" height="350" rx="30" fill="#bcd6ea"/>
  <g clip-path="url(#pB)"><use href="#mia" x="680" y="720" width="230" height="291"/></g>
  <rect x="20" y="700" width="878" height="350" rx="30" fill="none" stroke="{INK}" stroke-width="6"/>'''))

blinkless = []
story = {
 "title": "The Detective Did It — Day 2", "voice": "am_michael", "speed": 1.08,
 "music": "noir", "music_volume": 0.7, "ambience": "rain_train", "ambience_volume": 0.07,
 "fade": False, "vignette": 90,
 "layout": {"cx": 459, "max_w": 820, "cap_chars": 14},
 "stakes": {"y": 228, "width": 880, "show_from": 3.0,
            "start": {"suspicion": 0, "evidence": 3, "trust": 100},
            "changes": [{"at": 4.6, "suspicion": 15}, {"at": 5.4, "evidence": 2},
                        {"at": 12.9, "evidence": 3, "flash": [255, 60, 60]}]},
 "lines": [
  {"at": 0.05, "text": f"{X} percent of you said steal it. So I did.", "say": f"{spoken(X)} percent of you said steal it. So I did.", "speed": 1.12, "caption_y": 1240},
  {"at": 3.0, "text": "Two a.m. Evidence room. In and out in ninety seconds.", "caption_y": 1150},
  {"at": 7.2, "text": "The cufflink is gone. Someone took it from evidence.", "voice": "af_bella", "speed": 1.0, "caption_y": 1150},
  {"at": 10.8, "text": "One badge swiped in at 2:13. I'm pulling the name tonight.", "say": "One badge swiped in at two thirteen. I'm pulling the name tonight.", "voice": "af_bella", "speed": 1.0, "caption_y": 1250},
  {"at": 14.8, "text": "If she sees that name… it's mine.", "say": "If she sees that name... it's mine.", "caption_y": 1250},
  {"at": 17.4, "text": "And now… there are witnesses.", "say": "And now... there are witnesses.", "caption_y": 1150},
  {"at": 20.6, "text": "I have until tonight.", "caption_y": 1150},
  {"at": 23.9, "text": "A: break in and erase the log. B: lie to Mia's face. Comment A or B. Send this to the friend who'd lie for you.", "caption_y": 1110}],
 "shots": [
  {"id": "01", "duration": 2.9, "svg": "scenes/01-face.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.45, 0.42], "c1": [0.45, 0.42], "ease": "linear"}, "punch": False,
   "overlays": [{"text": "DAY 2", "y": 255, "size": 72, "color": [255, 214, 64], "pop": False},
                {"text": f"{X}% OF YOU SAID:", "y": 360, "size": 64, "pop": False},
                {"text": "STEAL IT", "y": 470, "size": 110, "color": [255, 92, 92], "pop": False}], "sfx": "hit"},
  {"id": "02", "duration": 4.1, "svg": "scenes/02-evroom.svg", "motion": {"z0": 1.0, "z1": 1.08, "c0": [0.47, 0.55], "c1": [0.47, 0.6]}, "fx": ["flicker"], "sfx": "whoosh"},
  {"id": "03", "duration": 3.6, "svg": "scenes/03-mia-empty.svg", "motion": {"z0": 1.0, "z1": 1.08, "c0": [0.5, 0.45], "c1": [0.52, 0.42]}, "fx": ["sway"], "sfx": "whoosh"},
  {"id": "04", "duration": 6.6, "svg": "scenes/04-log.svg", "motion": {"z0": 1.0, "z1": 1.12, "c0": [0.47, 0.42], "c1": [0.47, 0.44]}, "sfx": [{"name": "whoosh", "at": 0}, {"name": "hit", "at": 2.3}]},
  {"id": "05", "duration": 3.2, "svg": "scenes/05-board.svg", "motion": {"z0": 1.0, "z1": 1.08, "c0": [0.45, 0.43], "c1": [0.45, 0.43]}, "fx": ["sway"], "sfx": "whoosh"},
  {"id": "06", "duration": 3.2, "svg": "scenes/06-sweat.svg", "motion": {"z0": 1.0, "z1": 1.08, "c0": [0.45, 0.45], "c1": [0.45, 0.42]}, "sfx": [{"name": "tick", "at": 0.2}]},
  {"id": "07", "duration": 9.4, "svg": "scenes/07-choice.svg", "motion": {"z0": 1.0, "z1": 1.03, "c0": [0.5, 0.5], "c1": [0.5, 0.5], "ease": "linear"}, "punch": False,
   "overlays": [
     {"type": "label", "text": "A", "x": 110, "y": 420, "size": 120},
     {"text": "ERASE THE LOG", "x": 430, "y": 395, "size": 54, "max_w": 560, "start": 0.3},
     {"text": "TONIGHT", "x": 430, "y": 460, "size": 54, "max_w": 560, "start": 0.3},
     {"text": "🚨 +25%", "x": 430, "y": 555, "size": 58, "color": [255, 92, 92], "start": 0.6},
     {"text": "if caught, it's over", "x": 430, "y": 625, "size": 36, "color": [255, 214, 64], "start": 0.6},
     {"type": "label", "text": "B", "x": 110, "y": 800, "size": 120},
     {"text": "LIE TO", "x": 430, "y": 790, "size": 54, "max_w": 560, "start": 1.6},
     {"text": "MIA'S FACE", "x": 430, "y": 855, "size": 54, "max_w": 560, "start": 1.6},
     {"text": "🤝 −30%", "x": 430, "y": 955, "size": 58, "color": [120, 220, 140], "start": 1.9},
     {"text": "Comment WITNESS", "y": 1225, "size": 56, "color": [255, 214, 64], "start": 5.0},
     {"text": "to appear in Day 3 👀", "y": 1292, "size": 42, "start": 5.0}],
   "sfx": "hit"}]}
(HERE / "story.json").write_text(json.dumps(story, indent=2, ensure_ascii=False))
(HERE / "transcript.txt").write_text("\n".join(
    f"[{ln['at']:05.2f}s] {'MIA' if ln.get('voice') == 'af_bella' else 'DETECTIVE (VO)'}: {ln['text']}" for ln in story["lines"]) + "\n")
print("built for", X, WITNESSES)

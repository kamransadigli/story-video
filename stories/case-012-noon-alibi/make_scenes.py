"""Case #012 The Noon Alibi: scenes + two story files (Instagram / YouTube endings)."""
import json, math, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = "012"
INK = "#15141f"
base = (HERE.parent / "ice-doesnt-lie/scenes/_defs.svg").read_text().rstrip()[:-len("</defs>")]
random.seed(12)

def face(skin, skin_d, hair_back, hair_front, eyes, mouth, extra=""):
    return f'''{hair_back}
    <rect x="178" y="200" width="44" height="50" fill="{skin_d}"/>
    <ellipse cx="200" cy="140" rx="80" ry="94" fill="{skin}" stroke="{INK}" stroke-width="5"/>
    <ellipse cx="121" cy="150" rx="13" ry="22" fill="{skin}" stroke="{INK}" stroke-width="4"/><ellipse cx="279" cy="150" rx="13" ry="22" fill="{skin}" stroke="{INK}" stroke-width="4"/>
    {hair_front}{eyes}
    <path d="M200 146 C194 170 193 180 202 183" fill="none" stroke="{skin_d}" stroke-width="4" stroke-linecap="round"/>
    {mouth}{extra}'''

EYES = '<ellipse cx="170" cy="146" rx="15" ry="12" fill="#fff" stroke="#15141f" stroke-width="3"/><ellipse cx="230" cy="146" rx="15" ry="12" fill="#fff" stroke="#15141f" stroke-width="3"/><circle cx="171" cy="147" r="7" fill="#3a2a1a"/><circle cx="231" cy="147" r="7" fill="#3a2a1a"/><circle cx="174" cy="143" r="2.5" fill="#fff"/><circle cx="234" cy="143" r="2.5" fill="#fff"/>'
HAT = f'''<path d="M70 96 C110 80 290 80 330 96 C320 112 80 112 70 96 Z" fill="#e8c86a" stroke="{INK}" stroke-width="4"/>
    <path d="M128 92 C128 40 160 24 200 24 C240 24 272 40 272 92 Z" fill="#f0d47a" stroke="{INK}" stroke-width="4"/>
    <rect x="128" y="74" width="144" height="16" fill="#c8102e"/>'''
faceA = face("#e0a87c", "#c88e64", "", HAT, EYES.replace('cy="146" rx="15" ry="12"', 'cy="146" rx="15" ry="9"'),
    '<path d="M164 194 C182 222 218 222 236 194 Z" fill="#fff" stroke="#15141f" stroke-width="4"/>',
    '<ellipse cx="150" cy="176" rx="14" ry="8" fill="#e8806a" opacity="0.4"/><ellipse cx="250" cy="176" rx="14" ry="8" fill="#e8806a" opacity="0.4"/>')
sweat = "".join(f'<path d="M{x} {y} C{x+5} {y+12} {x+8} {y+18} {x+2} {y+23} C{x-5} {y+24} {x-8} {y+16} {x} {y} Z" fill="#9fdcff" stroke="#15141f" stroke-width="2"/>' for x, y in [(128, 104), (272, 110), (250, 70)])
faceB = face("#d8a27c", "#c08a62", "",
    '<path d="M124 120 C112 50 160 30 204 32 C256 34 292 60 280 122 C266 88 236 78 200 80 C168 80 140 92 124 120 Z" fill="#2a1a12" stroke="#15141f" stroke-width="4"/>',
    '<ellipse cx="170" cy="146" rx="19" ry="17" fill="#fff" stroke="#15141f" stroke-width="3"/><ellipse cx="230" cy="146" rx="19" ry="17" fill="#fff" stroke="#15141f" stroke-width="3"/><circle cx="174" cy="148" r="6" fill="#3a2a1a"/><circle cx="234" cy="148" r="6" fill="#3a2a1a"/><path d="M148 120 C160 112 180 112 190 118 M210 118 C220 112 240 112 252 120" fill="none" stroke="#2a1a12" stroke-width="6" stroke-linecap="round"/>',
    '<path d="M176 206 C186 198 194 210 202 202 C210 196 218 208 226 202" fill="none" stroke="#15141f" stroke-width="5" stroke-linecap="round"/>', sweat)
shadesC = f'<path d="M132 128 L194 128 C196 156 184 170 162 170 C140 170 128 154 132 128 Z" fill="#1a1418" stroke="{INK}" stroke-width="4"/><path d="M206 128 L268 128 C272 154 260 170 238 170 C216 170 204 156 206 128 Z" fill="#1a1418" stroke="{INK}" stroke-width="4"/><path d="M194 134 L206 134" stroke="{INK}" stroke-width="5"/><path d="M142 138 L170 138 M216 138 L244 138" stroke="#6a6a7a" stroke-width="5" stroke-linecap="round"/>'
faceC = face("#f0c49b", "#dcab82",
    '<path d="M104 170 C88 60 150 26 206 28 C264 30 314 66 296 170 C310 230 296 270 266 282 L136 282 C106 270 92 230 104 170 Z" fill="#b8402a" stroke="#15141f" stroke-width="5"/>',
    '<path d="M124 128 C120 60 170 42 212 44 C256 46 284 72 278 128 C264 94 236 84 208 86 C182 102 150 110 124 128 Z" fill="#b8402a" stroke="#15141f" stroke-width="4"/>',
    shadesC, '<path d="M178 206 L222 206" stroke="#a8465a" stroke-width="6" stroke-linecap="round"/>')

def bust(id_, fc, shirt, collar=""):
    return f'''
  <symbol id="{id_}" viewBox="0 0 400 700" overflow="visible">
    <path d="M40 760 C40 360 110 262 168 248 L232 248 C290 262 360 360 360 760 Z" fill="{shirt}" stroke="{INK}" stroke-width="5"/>
    {collar}{fc}
  </symbol>'''
hawaii = "".join(f'<circle cx="{x}" cy="{y}" r="16" fill="#ffd34a" stroke="#c8102e" stroke-width="5"/>' for x, y in [(90, 380), (150, 470), (250, 400), (320, 500), (110, 580), (290, 620), (200, 560)])
bustA = bust("holdA", faceA, "#2fa3a8", f'<path d="M168 248 L200 320 L232 248" fill="#f4f1ea" stroke="{INK}" stroke-width="4"/>{hawaii}')
bustB = bust("holdB", faceB, "#2c3a5a", f'<path d="M168 248 L200 340 L232 248 Z" fill="#f4f1ea" stroke="{INK}" stroke-width="4"/><path d="M192 262 L208 262 L214 340 L200 360 L186 340 Z" fill="#c8102e" stroke="{INK}" stroke-width="3"/><path d="M168 248 L200 420 L130 320 Z M232 248 L200 420 L270 320 Z" fill="#34446a" stroke="{INK}" stroke-width="4"/>')
bustC = bust("holdC", faceC, "#f0e6d2", f'<path d="M168 248 C180 290 220 290 232 248" fill="#f0c49b" stroke="{INK}" stroke-width="4"/>')
headB = f'''
  <symbol id="headB" viewBox="0 0 400 420" overflow="visible">
    <path d="M88 300 C88 268 128 250 168 248 L232 248 C272 250 312 268 312 300 L330 420 L70 420 Z" fill="#2c3a5a" stroke="{INK}" stroke-width="5"/>
    <path d="M168 248 L200 330 L232 248 Z" fill="#f4f1ea" stroke="{INK}" stroke-width="4"/><path d="M192 262 L208 262 L212 330 L200 345 L188 330 Z" fill="#c8102e"/>
    {faceB}
  </symbol>'''

# ---------- small full-body person used inside photos (viewBox 200x500, feet at y=490) ----------
def person(skin, shirt, pants, head_extra, mouth, arm_up=False, hair=""):
    arm = (f'<path d="M140 150 C170 120 180 90 176 60" fill="none" stroke="{INK}" stroke-width="22" stroke-linecap="round"/><path d="M140 150 C170 120 180 90 176 60" fill="none" stroke="{skin}" stroke-width="14" stroke-linecap="round"/>'
           f'<circle cx="176" cy="54" r="13" fill="{skin}" stroke="{INK}" stroke-width="3"/><path d="M176 42 L176 22" stroke="{INK}" stroke-width="9" stroke-linecap="round"/><path d="M176 42 L176 24" stroke="{skin}" stroke-width="5" stroke-linecap="round"/>') if arm_up else \
          f'<path d="M140 150 C152 200 150 240 146 270" fill="none" stroke="{INK}" stroke-width="22" stroke-linecap="round"/><path d="M140 150 C152 200 150 240 146 270" fill="none" stroke="{shirt}" stroke-width="14" stroke-linecap="round"/>'
    return f'''<path d="M74 300 L70 486 L96 486 L100 310 Z M126 300 L130 486 L104 486 L100 310 Z" fill="{pants}" stroke="{INK}" stroke-width="3"/>
      <ellipse cx="82" cy="488" rx="18" ry="7" fill="{INK}"/><ellipse cx="118" cy="488" rx="18" ry="7" fill="{INK}"/>
      <path d="M60 150 C60 130 80 120 100 120 C120 120 140 130 140 150 L144 310 L56 310 Z" fill="{shirt}" stroke="{INK}" stroke-width="3"/>
      <path d="M60 150 C48 200 50 240 54 270" fill="none" stroke="{INK}" stroke-width="22" stroke-linecap="round"/><path d="M60 150 C48 200 50 240 54 270" fill="none" stroke="{shirt}" stroke-width="14" stroke-linecap="round"/>
      {arm}{hair}
      <ellipse cx="100" cy="80" rx="36" ry="42" fill="{skin}" stroke="{INK}" stroke-width="3"/>
      {head_extra}{mouth}'''

def photo_frame(id_, inner, caption=""):
    return f'''
  <symbol id="{id_}" viewBox="0 0 800 1000" overflow="visible">
    <rect x="6" y="10" width="800" height="1000" fill="#000" opacity="0.25"/>
    <rect x="0" y="0" width="800" height="1000" fill="#fbf9f4" stroke="#c9c4b8" stroke-width="3"/>
    <svg x="40" y="40" width="720" height="820" viewBox="0 0 720 820" overflow="hidden">{inner}</svg>
    <rect x="40" y="40" width="720" height="820" fill="none" stroke="#d8d2c4" stroke-width="2"/>
    {caption}
  </symbol>'''

# A: beach, perfect, big smile + thumbs up, very LONG shadow stretching to the side
pA = person("#e0a87c", "#2fa3a8", "#e8d8b0",
    '<path d="M50 52 C70 44 130 44 150 52 C144 60 56 60 50 52 Z" fill="#e8c86a" stroke="#15141f" stroke-width="2"/><path d="M72 50 C72 22 86 14 100 14 C114 14 128 22 128 50 Z" fill="#f0d47a" stroke="#15141f" stroke-width="2"/>'
    '<circle cx="88" cy="80" r="4" fill="#15141f"/><circle cx="112" cy="80" r="4" fill="#15141f"/>',
    '<path d="M84 98 C92 110 108 110 116 98 Z" fill="#fff" stroke="#15141f" stroke-width="2"/>', arm_up=True)
photoA_inner = f'''
    <rect width="720" height="820" fill="#bfe6fa"/>
    <circle cx="610" cy="110" r="70" fill="#fff6c8" opacity="0.6"/>
    <rect x="0" y="300" width="720" height="140" fill="#3aa0c8"/>
    <g stroke="#e8f6ff" stroke-width="4" opacity="0.7"><path d="M40 340 L120 340 M300 380 L420 380 M520 330 L640 330"/></g>
    <path d="M0 420 C200 400 520 410 720 430 L720 820 L0 820 Z" fill="#f2dca8"/>
    <g fill="#e0c48a" opacity="0.7"><ellipse cx="120" cy="560" rx="30" ry="6"/><ellipse cx="560" cy="720" rx="40" ry="7"/><ellipse cx="320" cy="780" rx="30" ry="5"/></g>
    <!-- LONG late-afternoon shadow: stretches far to the right, ~2.5x his height -->
    <path d="M218 748 L720 676 L720 712 L232 772 Z" fill="#5a4220" opacity="0.72"/>
    <g transform="translate(150 280) scale(0.98)">{pA}</g>
    <g transform="translate(560 470)"><path d="M0 120 L60 0 L120 120 Z" fill="#c8102e" stroke="#15141f" stroke-width="3"/><rect x="56" y="0" width="8" height="200" fill="#5a3a24"/></g>'''

# B: cafe, BLURRY + tilted, half face cut off, waiter's arm blocking; clock at 12:00 on the wall
pB = person("#d8a27c", "#2c3a5a", "#2c3a5a",
    '<circle cx="88" cy="80" r="5" fill="#15141f"/><circle cx="112" cy="80" r="5" fill="#15141f"/>',
    '<path d="M86 104 L114 104" stroke="#15141f" stroke-width="3"/>', hair='<path d="M66 70 C62 40 84 30 100 30 C120 30 138 40 134 70 C128 52 116 48 100 48 C84 48 72 52 66 70 Z" fill="#2a1a12"/>')
clock = f'''<g transform="translate(470 120)">
      <circle r="78" fill="#fbf7ef" stroke="{INK}" stroke-width="8"/>
      <g stroke="{INK}" stroke-width="6" stroke-linecap="round">{"".join(f'<line x1="{64*math.sin(a*math.pi/6):.1f}" y1="{-64*math.cos(a*math.pi/6):.1f}" x2="{54*math.sin(a*math.pi/6):.1f}" y2="{-54*math.cos(a*math.pi/6):.1f}"/>' for a in range(12))}</g>
      <text x="0" y="-30" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="22" fill="{INK}">12</text>
      <line x1="0" y1="0" x2="0" y2="-38" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>
      <line x1="0" y1="0" x2="0" y2="-58" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
      <circle r="6" fill="#c8102e"/></g>'''
photoB_inner = f'''
    <defs><filter id="camBlur"><feGaussianBlur stdDeviation="3.2"/></filter><filter id="camBlurSoft"><feGaussianBlur stdDeviation="1.6"/></filter></defs>
    <g transform="rotate(-9 360 410)">
      <g filter="url(#camBlur)">
        <rect x="-100" y="-100" width="920" height="1020" fill="#e8c89a"/>
        <rect x="-100" y="520" width="920" height="400" fill="#8a5a34"/>
        <rect x="40" y="250" width="260" height="200" fill="#bfe6fa" stroke="#7a4a2a" stroke-width="10"/>
        <g fill="#f4f1ea"><circle cx="560" cy="600" r="60"/></g>
        <rect x="380" y="560" width="300" height="30" fill="#6a4224"/>
        <g transform="translate(-62 220) scale(1.15)">{pB}</g>
      </g>
      <g filter="url(#camBlurSoft)">{clock}</g>
      <!-- waiter's arm + tray blocking part of the shot -->
      <g filter="url(#camBlur)">
        <path d="M820 300 C640 360 560 420 520 470" stroke="{INK}" stroke-width="96" stroke-linecap="round" fill="none"/>
        <path d="M820 300 C640 360 560 420 520 470" stroke="#f4f1ea" stroke-width="82" stroke-linecap="round" fill="none"/>
        <ellipse cx="500" cy="470" rx="44" ry="34" fill="#c88e64" stroke="{INK}" stroke-width="4"/>
        <ellipse cx="470" cy="430" rx="150" ry="22" fill="#b8bcc4" stroke="{INK}" stroke-width="4"/>
        <rect x="420" y="370" width="50" height="60" rx="6" fill="#fff" stroke="{INK}" stroke-width="3"/>
      </g>
    </g>'''

# C: sunny park, not smiling, dog photobombing, SHORT shadow pool right under her feet (noon)
pC = person("#f0c49b", "#f0e6d2", "#3a4a6a",
    shadesC.replace('M132 128', 'M132 128') and
    '<path d="M70 72 L98 72 C98 88 92 94 84 94 C74 94 70 86 70 72 Z M102 72 L130 72 C130 86 126 94 116 94 C108 94 102 88 102 72 Z" fill="#1a1418" stroke="#15141f" stroke-width="2"/>',
    '<path d="M88 106 L112 106" stroke="#a8465a" stroke-width="3"/>',
    hair='<path d="M60 90 C52 40 78 30 100 30 C124 30 150 40 140 90 C146 120 140 140 128 146 L72 146 C60 140 54 120 60 90 Z" fill="#b8402a"/>')
dog = f'''<g transform="translate(540 600)">
      <ellipse cx="80" cy="150" rx="70" ry="10" fill="#2e5a2a" opacity="0.6"/>
      <path d="M10 80 C10 40 60 30 100 40 C140 50 150 90 140 120 L130 150 L110 150 L110 120 L50 120 L46 150 L26 150 L24 116 C12 108 10 96 10 80 Z" fill="#e8b46a" stroke="{INK}" stroke-width="4"/>
      <circle cx="40" cy="40" r="36" fill="#e8b46a" stroke="{INK}" stroke-width="4"/>
      <path d="M8 18 L18 -20 L40 12 Z M48 8 L76 -16 L74 26 Z" fill="#c8843a" stroke="{INK}" stroke-width="4"/>
      <circle cx="28" cy="36" r="6" fill="{INK}"/><circle cx="52" cy="36" r="6" fill="{INK}"/><ellipse cx="40" cy="54" rx="9" ry="7" fill="{INK}"/>
      <path d="M34 66 C38 84 48 84 50 66 Z" fill="#f07a8a" stroke="{INK}" stroke-width="3"/>
      <path d="M140 80 C170 60 176 40 168 20" fill="none" stroke="{INK}" stroke-width="12" stroke-linecap="round"/><path d="M140 80 C170 60 176 40 168 20" fill="none" stroke="#e8b46a" stroke-width="6" stroke-linecap="round"/>
    </g>'''
photoC_inner = f'''
    <rect width="720" height="820" fill="#bfe6fa"/>
    <path d="M0 300 L720 300 L720 820 L0 820 Z" fill="#7ac26a"/>
    <g fill="#3a8a4a"><circle cx="90" cy="220" r="90"/><circle cx="200" cy="180" r="80"/><circle cx="600" cy="210" r="100"/></g>
    <g fill="#6a4224"><rect x="80" y="260" width="20" height="80"/><rect x="590" y="270" width="24" height="90"/></g>
    <path d="M0 520 C200 500 500 520 720 500 L720 560 C500 580 200 560 0 580 Z" fill="#e8d8b0"/>
    <g fill="#ffd34a"><circle cx="140" cy="700" r="8"/><circle cx="420" cy="760" r="7"/><circle cx="660" cy="680" r="6"/></g>
    <!-- SHORT noon shadow: small dark pool right under her feet -->
    <ellipse cx="330" cy="754" rx="62" ry="18" fill="#1e4a1e" opacity="0.8"/>
    <g transform="translate(230 262) scale(0.98)">{pC}</g>
    {dog}'''
photos = photo_frame("photoA", photoA_inner) + photo_frame("photoB", photoB_inner) + photo_frame("photoC", photoC_inner)

museum = f'''
  <linearGradient id="marble" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4efe4"/><stop offset="1" stop-color="#e0d8c6"/></linearGradient>
  <symbol id="museum" viewBox="0 0 1080 1920">
    <rect width="1080" height="1920" fill="url(#marble)"/>
    <g fill="#e8e0ce" stroke="#c9bfa8" stroke-width="4">{"".join(f'<rect x="{x}" y="160" width="90" height="1100"/>' for x in (40, 950))}</g>
    <rect x="0" y="1260" width="1080" height="660" fill="#c9a676"/>
    <g stroke="#b08a5a" stroke-width="4">{"".join(f'<line x1="{x}" y1="1260" x2="{x - 120}" y2="1920"/>' for x in range(80, 1200, 160))}</g>
    <ellipse cx="540" cy="700" rx="700" ry="760" fill="#fff6dc" opacity="0.5" filter="url(#blur)"/>
    <g fill="#ffffff" filter="url(#glow)"><rect x="260" y="100" width="560" height="24" rx="12"/></g>
  </symbol>'''
(HERE / "scenes/_defs.svg").write_text(base + bustA + bustB + bustC + headB + photos + museum + "\n</defs>")

def svg(body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">\n{body}\n  <rect width="1080" height="1920" filter="url(#grit)"/>\n</svg>\n'
S = HERE / "scenes"
S.joinpath("01-face.svg").write_text(svg('''  <use href="#museum" width="1080" height="1920"/>
  <use href="#headB" x="-430" y="80" width="1940" height="2037"/>
  <ellipse cx="420" cy="760" rx="560" ry="640" fill="url(#lamp)" opacity="0.35"/>'''))
clockBig = clock.replace('translate(470 120)', 'translate(740 640) scale(1.5)')
S.joinpath("02-setup.svg").write_text(svg(f'''  <use href="#museum" width="1080" height="1920"/>
  {clockBig}
  <rect x="200" y="760" width="520" height="520" fill="#dfe9ef" fill-opacity="0.55" stroke="{INK}" stroke-width="6"/>
  <rect x="180" y="1270" width="560" height="120" fill="#7a5a3a" stroke="{INK}" stroke-width="6"/>
  <path d="M360 1270 L360 1150 C360 1110 560 1110 560 1150 L560 1270 Z" fill="#c8102e" stroke="{INK}" stroke-width="5"/>
  <ellipse cx="460" cy="1150" rx="70" ry="18" fill="#7a0a1c"/>
  <path d="M220 790 L300 790 L230 900" stroke="#ffffff" stroke-width="8" opacity="0.6" fill="none"/>'''))
def holding(bust_id, photo_id):
    return svg(f'''  <use href="#museum" width="1080" height="1920"/>
  <use href="#{bust_id}" x="90" y="230" width="720" height="1260"/>
  <g transform="rotate(-4 460 1000)">
    <use href="#{photo_id}" x="270" y="760" width="400" height="500"/>
    <ellipse cx="282" cy="1090" rx="34" ry="44" fill="#d8a27c" stroke="{INK}" stroke-width="5"/>
    <ellipse cx="658" cy="1090" rx="34" ry="44" fill="#d8a27c" stroke="{INK}" stroke-width="5"/>
  </g>''')
S.joinpath("03-a-hold.svg").write_text(holding("holdA", "photoA"))
S.joinpath("05-b-hold.svg").write_text(holding("holdB", "photoB"))
S.joinpath("07-c-hold.svg").write_text(holding("holdC", "photoC"))
def big(photo_id):
    return svg(f'''  <use href="#museum" width="1080" height="1920"/>
  <rect width="1080" height="1920" fill="#3a2a1e" opacity="0.18"/>
  <use href="#{photo_id}" x="100" y="300" width="720" height="900"/>''')
S.joinpath("04-a-photo.svg").write_text(big("photoA"))
S.joinpath("06-b-photo.svg").write_text(big("photoB"))
S.joinpath("08-c-photo.svg").write_text(big("photoC"))
S.joinpath("09-lineup.svg").write_text(svg('''  <use href="#museum" width="1080" height="1920"/>
  <use href="#photoA" x="30" y="560" width="290" height="362"/>
  <use href="#photoB" x="325" y="560" width="290" height="362"/>
  <use href="#photoC" x="620" y="560" width="290" height="362"/>'''))

def story(ending_line, ending_text):
    top = [{"text": f"CASE #{CASE}", "x": 175, "y": 190, "size": 46, "color": [255, 214, 64], "pop": False}]
    abc = {"text": "A, B or C? 👇", "x": 205, "y": 255, "size": 52, "pop": False}
    hook = {"text": "ONE OF THEM IS LYING", "y": 345, "size": 100, "pop": False}
    def lab(L, x=150, y=420, size=110): return {"type": "label", "text": L, "x": x, "y": y, "size": size}
    push = {"z0": 1.0, "z1": 1.06, "c0": [0.425, 0.39], "c1": [0.425, 0.39], "ease": "linear"}
    hold = {"z0": 1.0, "z1": 1.05, "c0": [0.45, 0.5], "c1": [0.45, 0.52]}
    return {
     "title": f"Case #{CASE}: The Noon Alibi", "voice": "am_michael", "speed": 1.18,
     "music": "noir", "music_volume": 0.6, "ambience": "museum", "ambience_volume": 0.12,
     "fade": False, "vignette": 70,
     "layout": {"cx": 470, "max_w": 880, "cap_chars": 14},
     "lines": [
      {"at": 0.05, "text": "One of them is lying. Almost nobody gets this right.", "caption_y": 1230},
      {"at": 3.0, "text": "A gold coin was stolen at exactly noon. All three have a photo proving they were somewhere else.", "caption_y": 1250},
      {"at": 10.85, "text": f"Whose photo is fake? Send this to someone who'll get it wrong. {ending_line}", "caption_y": 1250}],
     "shots": [
      {"id": "01", "duration": 2.0, "svg": "scenes/01-face.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.454, 0.42], "c1": [0.454, 0.42], "ease": "linear"}, "punch": False,
       "overlays": top + [hook], "sfx": "hit"},
      {"id": "02", "duration": 1.0, "svg": "scenes/02-setup.svg", "motion": {"z0": 1.0, "z1": 1.08, "c0": [0.45, 0.45], "c1": [0.45, 0.47], "ease": "out"}, "punch": False,
       "overlays": top + [{"text": "Stolen at exactly", "y": 300, "size": 78}, {"text": "12:00 noon ☀️", "y": 395, "size": 90, "color": [255, 214, 64]}]},
      {"id": "03", "duration": 1.0, "svg": "scenes/03-a-hold.svg", "motion": hold, "fx": ["sway"], "overlays": top + [abc, lab("A")], "sfx": "whoosh"},
      {"id": "04", "duration": 2.0, "svg": "scenes/04-a-photo.svg", "motion": push, "punch": False, "overlays": top + [abc, lab("A", 120, 360, 100)], "sfx": "shutter"},
      {"id": "05", "duration": 1.0, "svg": "scenes/05-b-hold.svg", "motion": hold, "fx": ["sway"], "overlays": top + [abc, lab("B")], "sfx": "whoosh"},
      {"id": "06", "duration": 2.0, "svg": "scenes/06-b-photo.svg", "motion": push, "punch": False, "overlays": top + [abc, lab("B", 120, 360, 100)], "sfx": "shutter"},
      {"id": "07", "duration": 1.0, "svg": "scenes/07-c-hold.svg", "motion": hold, "fx": ["sway"], "overlays": top + [abc, lab("C")], "sfx": "whoosh"},
      {"id": "08", "duration": 2.0, "svg": "scenes/08-c-photo.svg", "motion": push, "punch": False, "overlays": top + [abc, lab("C", 120, 360, 100)], "sfx": "shutter"},
      {"id": "09", "duration": 2.0, "svg": "scenes/09-lineup.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.45, 0.4], "c1": [0.45, 0.4], "ease": "linear"}, "punch": False,
       "overlays": top + [{"text": "Whose photo is fake? 👇", "y": 360, "size": 60, "pop": False},
                          lab("A", 175, 480, 90), lab("B", 470, 480, 90), lab("C", 765, 480, 90)], "sfx": "hit"},
      {"id": "10", "duration": 2.0, "image_of": "01", "motion": {"z0": 1.05, "z1": 1.0, "c0": [0.454, 0.42], "c1": [0.454, 0.42], "ease": "linear"}, "punch": False,
       "overlays": top + [{"text": "Send this to someone", "y": 290, "size": 70, "end": 1.7},
                          {"text": "who'll get it wrong 😈", "y": 375, "size": 70, "color": [255, 214, 64], "end": 1.7},
                          {"text": ending_text[0], "y": 480, "size": 60, "start": 0.3, "end": 1.7},
                          {"text": ending_text[1], "y": 555, "size": 60, "start": 0.3, "end": 1.7},
                          dict(hook, start=1.7)], "sfx": "whoosh"}]}
(HERE / "story.json").write_text(json.dumps(story("Answer in my Story tomorrow.", ["✅ Answer in my Story", "tomorrow"]), indent=2, ensure_ascii=False))
(HERE / "story-youtube.json").write_text(json.dumps(story("Answer in the comments tomorrow.", ["✅ Answer in the", "comments tomorrow"]), indent=2, ensure_ascii=False))
print("ok")

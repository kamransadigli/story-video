"""Case #011 The Dry Spot: scenes + two story files (Instagram / YouTube endings)."""
import json, math, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = "011"
INK = "#15141f"
base = (HERE.parent / "ice-doesnt-lie/scenes/_defs.svg").read_text().rstrip()[:-len("</defs>")]
random.seed(11)

def face(skin, skin_d, hair_back, hair_front, eyes, mouth, extra=""):
    return f'''{hair_back}
    <rect x="178" y="200" width="44" height="50" fill="{skin_d}"/>
    <ellipse cx="200" cy="140" rx="80" ry="94" fill="{skin}" stroke="{INK}" stroke-width="5"/>
    <ellipse cx="121" cy="150" rx="13" ry="22" fill="{skin}" stroke="{INK}" stroke-width="4"/><ellipse cx="279" cy="150" rx="13" ry="22" fill="{skin}" stroke="{INK}" stroke-width="4"/>
    {hair_front}{eyes}
    <path d="M200 146 C194 170 193 180 202 183" fill="none" stroke="{skin_d}" stroke-width="4" stroke-linecap="round"/>
    {mouth}{extra}'''

def shoe(x, flip, color):
    s = -1 if flip else 1
    return f'''<g transform="translate({x} 1170) scale({s} 1)">
      <path d="M-24 -40 L20 -40 C54 -34 80 -22 84 -6 L84 0 L-26 0 Z" fill="{color}" stroke="{INK}" stroke-width="5"/>
      <rect x="-28" y="-8" width="116" height="14" rx="4" fill="#1a1a1e" stroke="{INK}" stroke-width="3"/></g>'''

def figure(id_, fc, torso, legs, shoes, front=""):
    return f'''
  <symbol id="{id_}" viewBox="0 0 400 1200" overflow="visible">
    <ellipse cx="200" cy="1176" rx="140" ry="14" fill="#000" opacity="0.25"/>
    {legs}{shoes}{torso}{fc}{front}
  </symbol>'''

def arm(path, color):
    return f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="56" stroke-linecap="round"/><path d="{path}" fill="none" stroke="{color}" stroke-width="46" stroke-linecap="round"/>'

# ---------- A (thief): ordinary man, beige jacket, paper coffee cup ----------
faceA = face("#d9a87e", "#c08e66", "",
    '<path d="M124 118 C114 52 160 32 204 34 C254 36 290 60 278 120 C266 88 238 78 202 80 C172 80 142 92 124 118 Z" fill="#5a3a24" stroke="#15141f" stroke-width="4"/>',
    '<ellipse cx="170" cy="146" rx="15" ry="11" fill="#fff" stroke="#15141f" stroke-width="3"/><ellipse cx="230" cy="146" rx="15" ry="11" fill="#fff" stroke="#15141f" stroke-width="3"/><circle cx="171" cy="147" r="6" fill="#3a2a1a"/><circle cx="231" cy="147" r="6" fill="#3a2a1a"/><path d="M152 126 L188 124 M212 124 L248 126" stroke="#3a2414" stroke-width="7" stroke-linecap="round"/>',
    '<path d="M180 204 C192 208 208 208 220 204" fill="none" stroke="#15141f" stroke-width="5" stroke-linecap="round"/>')
torsoA = f'''<path d="M92 300 C92 258 130 240 168 238 L232 238 C270 240 308 258 308 300 L320 720 L80 720 Z" fill="#d6c09a" stroke="{INK}" stroke-width="5"/>
    <path d="M168 238 L200 310 L232 238 Z" fill="#f4f1ea" stroke="{INK}" stroke-width="4"/>
    <path d="M200 310 L200 720" stroke="{INK}" stroke-width="4"/>
    {arm("M94 300 C70 420 72 540 86 640", "#d6c09a")}<circle cx="86" cy="660" r="24" fill="#d9a87e" stroke="{INK}" stroke-width="4"/>
    {arm("M306 300 C330 380 320 440 262 470", "#d6c09a")}'''
cupA = f'''<g><path d="M224 420 L276 420 L270 500 L230 500 Z" fill="#f4f1ea" stroke="{INK}" stroke-width="4"/>
    <rect x="220" y="410" width="60" height="14" rx="4" fill="#5a3a24" stroke="{INK}" stroke-width="3"/>
    <rect x="228" y="448" width="44" height="22" fill="#c8102e"/>
    <circle cx="262" cy="476" r="22" fill="#d9a87e" stroke="{INK}" stroke-width="4"/></g>'''
legsA = f'<path d="M132 710 L140 1130 L190 1130 L198 730 Z M268 710 L260 1130 L210 1130 L202 730 Z" fill="#3a4a62" stroke="{INK}" stroke-width="5"/>'
figA = figure("figA", faceA, torsoA, legsA, shoe(168, True, "#e8e8ea") + shoe(232, False, "#e8e8ea"), front=cupA)

# ---------- B (red herring): shady, sunglasses with rain drops, leather jacket, gold chain ----------
drops = "".join(f'<ellipse cx="{x}" cy="{y}" rx="4" ry="6" fill="#dff4ff" stroke="#9ac4dc" stroke-width="1.5"/>' for x, y in [(158, 140), (176, 152), (226, 136), (244, 154), (164, 160), (236, 146)])
shades = (f'<path d="M136 128 L192 128 C194 150 184 166 164 166 C144 166 134 150 136 128 Z" fill="#141418" stroke="{INK}" stroke-width="4"/>'
          f'<path d="M208 128 L264 128 C266 150 256 166 236 166 C216 166 206 150 208 128 Z" fill="#141418" stroke="{INK}" stroke-width="4"/>'
          f'<path d="M192 134 L208 134" stroke="{INK}" stroke-width="5"/><path d="M146 136 L170 136" stroke="#5a6a80" stroke-width="5" stroke-linecap="round"/><path d="M218 136 L242 136" stroke="#5a6a80" stroke-width="5" stroke-linecap="round"/>{drops}')
stubble = '<g fill="#3a2a1a" opacity="0.5">' + "".join(f'<circle cx="{x}" cy="{y}" r="2.4"/>' for x, y in [(150, 190), (162, 204), (176, 214), (190, 220), (210, 220), (224, 214), (238, 204), (250, 190), (200, 226), (168, 196), (232, 196)]) + "</g>"
faceB = face("#c99068", "#b07a52", "",
    '<path d="M122 112 C118 44 168 26 210 30 C262 34 292 64 278 118 C260 82 228 70 196 74 C166 76 140 90 122 112 Z" fill="#141216" stroke="#15141f" stroke-width="4"/><path d="M150 52 C186 38 236 40 262 60" fill="none" stroke="#4a4a58" stroke-width="6" stroke-linecap="round"/>',
    shades,
    '<path d="M174 204 C192 210 212 206 230 194" fill="none" stroke="#15141f" stroke-width="5" stroke-linecap="round"/>', stubble)
chain = f'<path d="M160 250 C180 300 220 300 240 250" fill="none" stroke="#e3b04b" stroke-width="9"/><path d="M160 250 C180 300 220 300 240 250" fill="none" stroke="#8a6a1a" stroke-width="9" stroke-dasharray="3 9"/><circle cx="200" cy="296" r="12" fill="#e3b04b" stroke="{INK}" stroke-width="3"/>'
torsoB = f'''<path d="M88 300 C88 258 128 240 168 238 L232 238 C272 240 312 258 312 300 L322 720 L78 720 Z" fill="#1e1c22" stroke="{INK}" stroke-width="5"/>
    <path d="M168 238 L200 330 L232 238 Z" fill="#c99068" stroke="{INK}" stroke-width="4"/>
    <path d="M168 238 L200 400 L130 300 Z M232 238 L200 400 L270 300 Z" fill="#2c2a32" stroke="{INK}" stroke-width="4"/>
    <path d="M120 330 C110 420 120 520 130 600" stroke="#4a4852" stroke-width="5" fill="none"/>
    {arm("M92 300 C70 420 70 540 84 640", "#1e1c22")}{arm("M308 300 C330 420 330 540 316 640", "#1e1c22")}
    <circle cx="84" cy="660" r="24" fill="#c99068" stroke="{INK}" stroke-width="4"/><circle cx="316" cy="660" r="24" fill="#c99068" stroke="{INK}" stroke-width="4"/>{chain}'''
legsB = f'<path d="M132 710 L140 1130 L190 1130 L198 730 Z M268 710 L260 1130 L210 1130 L202 730 Z" fill="#2a3442" stroke="{INK}" stroke-width="5"/>'
figB = figure("figB", faceB, torsoB, legsB, shoe(168, True, "#3a2a1e") + shoe(232, False, "#3a2a1e"))

# ---------- C: woman with a RED umbrella ----------
faceC = face("#f0c49b", "#dcab82",
    '<path d="M110 170 C96 66 150 32 204 32 C260 34 308 66 292 170 C302 220 288 250 264 258 L140 258 C114 250 100 220 110 170 Z" fill="#2a1a12" stroke="#15141f" stroke-width="5"/>',
    '<path d="M126 132 C122 64 170 46 212 48 C254 50 282 74 276 132 C264 98 238 86 210 88 C186 104 152 112 126 132 Z" fill="#2a1a12" stroke="#15141f" stroke-width="4"/>',
    '<ellipse cx="170" cy="148" rx="15" ry="12" fill="#fff" stroke="#15141f" stroke-width="3"/><ellipse cx="230" cy="148" rx="15" ry="12" fill="#fff" stroke="#15141f" stroke-width="3"/><circle cx="171" cy="149" r="7" fill="#3a2a1a"/><circle cx="231" cy="149" r="7" fill="#3a2a1a"/><circle cx="174" cy="145" r="2.5" fill="#fff"/><circle cx="234" cy="145" r="2.5" fill="#fff"/>',
    '<path d="M178 200 C192 210 208 210 222 200" fill="none" stroke="#a8465a" stroke-width="5" stroke-linecap="round"/>')
umbrella = f'''<path d="M300 380 L300 -120" stroke="{INK}" stroke-width="10"/>
    <path d="M40 -60 C80 -220 520 -220 560 -60 C520 -84 480 -84 440 -60 C400 -84 340 -84 300 -60 C260 -84 200 -84 160 -60 C120 -84 80 -84 40 -60 Z" fill="#d0142f" stroke="{INK}" stroke-width="6"/>
    <path d="M160 -60 C200 -160 260 -190 300 -196 M440 -60 C400 -160 340 -190 300 -196" fill="none" stroke="#8c0f22" stroke-width="5"/>
    <path d="M120 -110 C180 -170 260 -186 300 -188" fill="none" stroke="#ff6a7a" stroke-width="8" stroke-linecap="round" opacity="0.7"/>
    <circle cx="300" cy="-200" r="9" fill="#e3b04b" stroke="{INK}" stroke-width="3"/>'''
torsoC = f'''<path d="M100 300 C100 258 136 240 170 238 L230 238 C264 240 300 258 300 300 L320 760 L80 760 Z" fill="#2a4c7a" stroke="{INK}" stroke-width="5"/>
    <g fill="#e3b04b"><circle cx="200" cy="400" r="7"/><circle cx="200" cy="500" r="7"/><circle cx="200" cy="600" r="7"/></g>
    {arm("M96 300 C72 420 74 540 88 640", "#2a4c7a")}<circle cx="88" cy="660" r="22" fill="#f0c49b" stroke="{INK}" stroke-width="4"/>
    {arm("M304 300 C330 340 330 380 300 400", "#2a4c7a")}<circle cx="300" cy="396" r="22" fill="#f0c49b" stroke="{INK}" stroke-width="4"/>'''
legsC = f'<path d="M150 750 L158 1130 L188 1130 L192 750 Z M250 750 L242 1130 L212 1130 L208 750 Z" fill="#f0c49b" stroke="{INK}" stroke-width="4"/>'
figC = figure("figC", faceC, torsoC, legsC, shoe(172, True, "#2a1a12") + shoe(228, False, "#2a1a12"), front=umbrella)

headB = f'''
  <symbol id="headB" viewBox="0 0 400 420" overflow="visible">
    <path d="M88 300 C88 268 128 250 168 248 L232 248 C272 250 312 268 312 300 L330 420 L70 420 Z" fill="#1e1c22" stroke="{INK}" stroke-width="5"/>
    <path d="M168 248 L200 330 L232 248 Z" fill="#c99068" stroke="{INK}" stroke-width="4"/>
    {faceB}{chain}
  </symbol>'''

# ---------- cars (side view, 600x300, tyres touch y=290) ----------
def raindots(x0, x1, y0, y1, n=16):
    return "".join(f'<circle cx="{random.uniform(x0, x1):.0f}" cy="{random.uniform(y0, y1):.0f}" r="3" fill="#e8f6ff" opacity="0.9"/>' for _ in range(n))
cars = f'''
  <symbol id="carBlue" viewBox="0 0 600 300" overflow="visible">
    <path d="M40 250 L40 170 C40 150 60 140 90 136 L170 70 C186 58 210 52 240 52 L400 52 C430 52 450 66 466 90 L500 136 C540 142 570 156 570 190 L570 250 Z" fill="#2f6fc8" stroke="{INK}" stroke-width="6"/>
    <path d="M190 80 L250 72 L250 132 L130 132 Z M270 72 L392 72 C412 72 426 84 438 104 L456 132 L270 132 Z" fill="#cfe6f6" stroke="{INK}" stroke-width="4"/>
    <path d="M70 160 L540 160" stroke="#1f4e90" stroke-width="5"/>{raindots(60, 560, 60, 240)}
    <circle cx="150" cy="250" r="44" fill="#1a1a1e" stroke="{INK}" stroke-width="5"/><circle cx="150" cy="250" r="18" fill="#9aa3a8"/>
    <circle cx="470" cy="250" r="44" fill="#1a1a1e" stroke="{INK}" stroke-width="5"/><circle cx="470" cy="250" r="18" fill="#9aa3a8"/>
  </symbol>
  <symbol id="vanOld" viewBox="0 0 600 300" overflow="visible">
    <path d="M30 250 L30 70 C30 50 44 40 70 40 L430 40 C470 40 500 60 520 100 L560 160 C574 172 578 190 578 210 L578 250 Z" fill="#b8a47a" stroke="{INK}" stroke-width="6"/>
    <path d="M440 64 L490 64 C504 64 512 74 520 90 L548 150 L440 150 Z" fill="#cfe6f6" stroke="{INK}" stroke-width="4"/>
    <path d="M60 160 L570 160" stroke="#8a7650" stroke-width="5"/>
    <path d="M150 90 C170 110 190 100 200 120 M300 180 C320 170 330 196 350 186" fill="none" stroke="#6a5a3a" stroke-width="4"/>
    <g fill="#a8622a" opacity="0.75"><ellipse cx="80" cy="220" rx="26" ry="12"/><ellipse cx="380" cy="230" rx="22" ry="10"/><ellipse cx="520" cy="200" rx="14" ry="8"/></g>
    {raindots(50, 560, 50, 240, 18)}
    <circle cx="140" cy="250" r="46" fill="#1a1a1e" stroke="{INK}" stroke-width="5"/><circle cx="140" cy="250" r="18" fill="#7a8288"/>
    <circle cx="470" cy="250" r="46" fill="#1a1a1e" stroke="{INK}" stroke-width="5"/><circle cx="470" cy="250" r="18" fill="#7a8288"/>
  </symbol>
  <symbol id="carRed" viewBox="0 0 600 300" overflow="visible">
    <path d="M30 250 L30 190 C30 166 52 154 90 150 L180 96 C200 84 226 78 260 78 L380 78 C410 78 432 90 454 110 L500 150 C548 156 578 170 578 200 L578 250 Z" fill="#d0142f" stroke="{INK}" stroke-width="6"/>
    <path d="M200 104 L262 98 L262 148 L136 148 Z M282 98 L376 98 C396 98 412 108 428 124 L446 148 L282 148 Z" fill="#cfe6f6" stroke="{INK}" stroke-width="4"/>
    <path d="M90 168 C200 160 400 160 540 172" stroke="#ff8a96" stroke-width="10" stroke-linecap="round" opacity="0.8"/>
    {raindots(60, 560, 90, 240)}
    <circle cx="150" cy="250" r="44" fill="#1a1a1e" stroke="{INK}" stroke-width="5"/><circle cx="150" cy="250" r="18" fill="#c9ced6"/>
    <circle cx="470" cy="250" r="44" fill="#1a1a1e" stroke="{INK}" stroke-width="5"/><circle cx="470" cy="250" r="18" fill="#c9ced6"/>
  </symbol>'''

def lot_bg():
    puddles = "".join(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx*0.22:.0f}" fill="#7f8a96" opacity="0.8"/><ellipse cx="{x}" cy="{y}" rx="{rx*0.5:.0f}" ry="{rx*0.11:.0f}" fill="none" stroke="#c9d6e2" stroke-width="3" opacity="0.8"/>'
                      for x, y, rx in [(140, 1360, 110), (720, 1420, 140), (420, 1560, 120), (860, 1640, 90), (220, 1720, 130)])
    shine = "".join(f'<path d="M{x} {y} L{x+random.uniform(-6, 6):.0f} {y+random.uniform(60, 140):.0f}" stroke="{c}" stroke-width="{random.choice([4, 6, 8])}" opacity="0.45" stroke-linecap="round"/>'
                    for x, y, c in [(random.uniform(40, 1040), random.uniform(1000, 1800), random.choice(["#ff5a4a", "#ffd34a", "#e8f0f6", "#e8f0f6"])) for _ in range(26)])
    return f'''
  <linearGradient id="greySky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6ecf2"/><stop offset="1" stop-color="#cdd6de"/></linearGradient>
  <linearGradient id="wetAsphalt" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5c6670"/><stop offset="1" stop-color="#46505a"/></linearGradient>
  <symbol id="lot" viewBox="0 0 1080 1920">
    <rect width="1080" height="1920" fill="url(#greySky)"/>
    <!-- diner building with warm windows -->
    <rect x="-20" y="560" width="1120" height="400" fill="#e8e0cc" stroke="{INK}" stroke-width="5"/>
    <rect x="-20" y="540" width="1120" height="40" fill="#c8102e"/>
    <g fill="#ffe2a6" stroke="{INK}" stroke-width="4">{"".join(f'<rect x="{x}" y="640" width="170" height="150" rx="8"/>' for x in (40, 260, 480, 700))}</g>
    <ellipse cx="540" cy="720" rx="640" ry="200" fill="#ffd58a" opacity="0.25" filter="url(#blur)"/>
    <rect x="890" y="650" width="120" height="300" fill="#7a4a2a" stroke="{INK}" stroke-width="4"/>
    <!-- wet asphalt lot -->
    <rect x="0" y="960" width="1080" height="960" fill="url(#wetAsphalt)"/>
    <g stroke="#f4f1ea" stroke-width="10" opacity="0.7">{"".join(f'<line x1="{x}" y1="1000" x2="{x - 40}" y2="1300"/>' for x in (320, 640, 960))}</g>
    {shine}{puddles}
  </symbol>'''

(HERE / "scenes/_defs.svg").write_text(base + figA + figB + figC + headB + cars + lot_bg() + "\n</defs>")

def svg(body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">\n{body}\n  <rect width="1080" height="1920" filter="url(#grit)"/>\n</svg>\n'

def dry(x0, x1, y):
    """Lighter, matte DRY rectangle of asphalt under a car parked before the rain."""
    return f'<rect x="{x0}" y="{y - 14}" width="{x1 - x0}" height="62" rx="14" fill="#9ea4aa"/><rect x="{x0 + 10}" y="{y - 8}" width="{x1 - x0 - 20}" height="8" fill="#b4b9be"/>'

def car_with_ground(car, x, y_ground, w, dry_spot, reflect_col):
    h = w / 2
    y = y_ground - 290 * h / 300
    ground = dry(x + 0.04 * w, x + 0.96 * w, y_ground) if dry_spot else (
        f'<g opacity="0.35" transform="translate(0 {2 * y_ground}) scale(1 -1)"><use href="#{car}" x="{x}" y="{y}" width="{w}" height="{h}"/></g>'
        f'<rect x="{x + 0.04 * w}" y="{y_ground - 14}" width="{0.92 * w}" height="62" fill="{reflect_col}" opacity="0.25"/>'
        f'<path d="M{x + 0.1 * w} {y_ground + 20} L{x + 0.9 * w} {y_ground + 24}" stroke="#e8f0f6" stroke-width="5" opacity="0.6"/>')
    return ground + f'<use href="#{car}" x="{x}" y="{y}" width="{w}" height="{h}"/>'

def place(h, feet): return feet - 1170 * h / 1200

S = HERE / "scenes"
S.joinpath("01-face.svg").write_text(svg('''  <use href="#lot" width="1080" height="1920"/>
  <circle cx="900" cy="420" r="360" fill="#ff5a3a" opacity="0.22" filter="url(#blur)"/>
  <circle cx="120" cy="560" r="300" fill="#ffd34a" opacity="0.22" filter="url(#blur)"/>
  <rect width="1080" height="1920" fill="#f6e8d0" opacity="0.25"/>
  <use href="#headB" x="-430" y="80" width="1940" height="2037"/>
  <ellipse cx="420" cy="760" rx="560" ry="640" fill="url(#lamp)" opacity="0.35"/>'''))
S.joinpath("02-sign.svg").write_text(svg(f'''  <use href="#lot" width="1080" height="1920"/>
  <rect x="440" y="480" width="40" height="760" fill="#5a5f66" stroke="{INK}" stroke-width="4"/>
  <g filter="url(#glow)">
    <rect x="160" y="420" width="600" height="230" rx="30" fill="#c8102e" stroke="#ffd34a" stroke-width="12"/>
    <text x="460" y="590" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="150" fill="#ffe14a" letter-spacing="10">DINER</text>
  </g>
  <circle cx="460" cy="535" r="420" fill="#ff5a3a" opacity="0.12" filter="url(#blur)"/>'''))

def solo(fig, car, dry_spot, refl):
    fh = 660
    w = 400 * fh / 1200
    return svg(f'''  <use href="#lot" width="1080" height="1920"/>
  {car_with_ground(car, 240, 1030, 670, dry_spot, refl)}
  <use href="#{fig}" x="{175 - w/2:.0f}" y="{place(fh, 1052):.0f}" width="{w:.0f}" height="{fh}"/>''')
S.joinpath("03-a.svg").write_text(solo("figA", "carBlue", False, "#2f6fc8"))
S.joinpath("04-b.svg").write_text(solo("figB", "vanOld", True, "#b8a47a"))
S.joinpath("05-c.svg").write_text(solo("figC", "carRed", True, "#d0142f"))
L = ['  <use href="#lot" width="1080" height="1920"/>']
for (fig, car, d, refl), cx in zip([("figA", "carBlue", False, "#2f6fc8"), ("figB", "vanOld", True, "#b8a47a"), ("figC", "carRed", True, "#d0142f")], (160, 450, 740)):
    L.append(car_with_ground(car, cx - 100, 1030, 260, d, refl))
    fh = 340; w = 400 * fh / 1200
    L.append(f'<use href="#{fig}" x="{cx - 100 - w/2:.0f}" y="{place(fh, 1042):.0f}" width="{w:.0f}" height="{fh}"/>')
S.joinpath("06-lineup.svg").write_text(svg("\n".join(L)))

def story(ending_line, ending_text):
    top = [{"text": f"CASE #{CASE}", "x": 175, "y": 190, "size": 46, "color": [255, 214, 64], "pop": False}]
    abc = {"text": "A, B or C? 👇", "x": 205, "y": 255, "size": 52, "pop": False}
    hook = {"text": "ONE OF THEM IS LYING", "y": 345, "size": 100, "pop": False}
    rain = {"fx": ["rain"]}
    return {
     "title": f"Case #{CASE}: The Dry Spot", "voice": "am_michael", "speed": 1.18,
     "music": "noir", "music_volume": 0.6, "ambience": "rain_lot", "ambience_volume": 0.14,
     "fade": False, "vignette": 70,
     "layout": {"cx": 470, "max_w": 880, "cap_chars": 14},
     "lines": [
      {"at": 0.05, "text": "One of them is lying. Most people get this wrong.", "caption_y": 1230},
      {"at": 2.62, "text": "It's been raining for an hour. Ten minutes ago, the diner was robbed. All three say they parked here this morning.", "caption_y": 1250},
      {"at": 9.1, "text": f"Who's lying? Send this to someone who'll get it wrong. {ending_line}", "caption_y": 1230}],
     "shots": [
      {"id": "01", "duration": 2.0, "svg": "scenes/01-face.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.454, 0.42], "c1": [0.454, 0.42], "ease": "linear"}, "punch": False,
       "overlays": top + [hook], "sfx": "hit", **rain},
      {"id": "02", "duration": 1.0, "svg": "scenes/02-sign.svg", "motion": {"z0": 1.0, "z1": 1.08, "c0": [0.44, 0.4], "c1": [0.44, 0.4], "ease": "out"}, "punch": False,
       "overlays": top + [{"text": "Raining for 1 hour", "y": 760, "size": 72, "color": [255, 255, 255]},
                          {"text": "Robbed 10 min ago", "y": 850, "size": 72, "color": [255, 214, 64], "start": 0.15}],
       "sfx": [{"name": "bell", "at": 0.0}], **rain},
      {"id": "03", "duration": 2.0, "svg": "scenes/03-a.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.47, 0.5], "c1": [0.47, 0.52]}, "punch": False,
       "overlays": top + [abc, {"type": "label", "text": "A", "x": 560, "y": 560}], "sfx": "whoosh", **rain},
      {"id": "04", "duration": 2.0, "svg": "scenes/04-b.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.47, 0.5], "c1": [0.47, 0.52]}, "punch": False,
       "overlays": top + [abc, {"type": "label", "text": "B", "x": 560, "y": 560}], "sfx": "whoosh", **rain},
      {"id": "05", "duration": 2.0, "svg": "scenes/05-c.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.47, 0.5], "c1": [0.47, 0.52]}, "punch": False,
       "overlays": top + [abc, {"type": "label", "text": "C", "x": 560, "y": 560}], "sfx": "whoosh", **rain},
      {"id": "06", "duration": 2.0, "svg": "scenes/06-lineup.svg", "motion": {"z0": 1.0, "z1": 1.04, "c0": [0.46, 0.55], "c1": [0.46, 0.56], "ease": "linear"}, "punch": False,
       "overlays": top + [abc, {"text": "Who's lying? 👇", "y": 350, "size": 84, "pop": False},
                          {"type": "label", "text": "A", "x": 160, "y": 600, "size": 90},
                          {"type": "label", "text": "B", "x": 450, "y": 600, "size": 90},
                          {"type": "label", "text": "C", "x": 740, "y": 600, "size": 90}], "sfx": "hit", **rain},
      {"id": "07", "duration": 3.0, "image_of": "01", "motion": {"z0": 1.05, "z1": 1.0, "c0": [0.454, 0.42], "c1": [0.454, 0.42], "ease": "linear"}, "punch": False,
       "overlays": top + [{"text": "Send this to someone", "y": 290, "size": 70, "end": 2.7},
                          {"text": "who'll get it wrong 😈", "y": 375, "size": 70, "color": [255, 214, 64], "end": 2.7},
                          {"text": ending_text[0], "y": 480, "size": 60, "start": 0.6, "end": 2.7},
                          {"text": ending_text[1], "y": 555, "size": 60, "start": 0.6, "end": 2.7},
                          dict(hook, start=2.7)], "sfx": "whoosh", **rain}]}
(HERE / "story.json").write_text(json.dumps(story("Answer in my Story tomorrow.", ["✅ Answer in my Story", "tomorrow"]), indent=2, ensure_ascii=False))
(HERE / "story-youtube.json").write_text(json.dumps(story("Answer in the comments tomorrow.", ["✅ Answer in the", "comments tomorrow"]), indent=2, ensure_ascii=False))
print("ok")

"""Case #010 The Melted Chocolate: scenes + two story files (Instagram / YouTube endings)."""
import json, math, random
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASE = "010"
INK = "#15141f"
base = (HERE.parent / "ice-doesnt-lie/scenes/_defs.svg").read_text().rstrip()[:-len("</defs>")]
random.seed(10)

def face(skin, skin_d, hair_back, hair_front, eyes, mouth, extra=""):
    return f'''{hair_back}
    <rect x="178" y="200" width="44" height="50" fill="{skin_d}"/>
    <ellipse cx="200" cy="140" rx="80" ry="94" fill="{skin}" stroke="{INK}" stroke-width="5"/>
    <ellipse cx="121" cy="150" rx="13" ry="22" fill="{skin}" stroke="{INK}" stroke-width="4"/><ellipse cx="279" cy="150" rx="13" ry="22" fill="{skin}" stroke="{INK}" stroke-width="4"/>
    {hair_front}{eyes}
    <path d="M200 146 C194 170 193 180 202 183" fill="none" stroke="{skin_d}" stroke-width="4" stroke-linecap="round"/>
    {mouth}{extra}'''

def snow_clumps(points, rmin=7, rmax=15):
    return "".join(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{random.uniform(rmin, rmax):.0f}" ry="{random.uniform(rmin*0.6, rmax*0.7):.0f}" fill="#ffffff" stroke="#b8d4e8" stroke-width="2"/>' for x, y in points)

def frost(points):
    return "".join(f'<path d="M{x} {y-7} L{x} {y+7} M{x-7} {y} L{x+7} {y} M{x-5} {y-5} L{x+5} {y+5} M{x+5} {y-5} L{x-5} {y+5}" stroke="#ffffff" stroke-width="2.6" stroke-linecap="round"/>' for x, y in points)

def boot(x, flip, color="#3a2a1e", snow=False):
    s = -1 if flip else 1
    sn = ""
    if snow:
        sn = ('<path d="M-30 -2 C-24 -22 -6 -20 4 -26 C20 -32 46 -24 66 -18 C84 -12 92 -4 90 4 L-32 6 Z" fill="#ffffff" stroke="#b8d4e8" stroke-width="2.5"/>'
              '<path d="M-28 -92 C-14 -100 6 -100 24 -92 L22 -84 L-26 -84 Z" fill="#ffffff" stroke="#b8d4e8" stroke-width="2.5"/>'
              '<g fill="#ffffff"><circle cx="40" cy="-30" r="5"/><circle cx="-10" cy="-50" r="4"/><circle cx="10" cy="-64" r="4"/></g>')
    return f'''<g transform="translate({x} 1170) scale({s} 1)">
      <path d="M-26 -90 L22 -90 L24 -34 C60 -32 86 -22 90 -6 L90 0 L-30 0 Z" fill="{color}" stroke="{INK}" stroke-width="5"/>
      <rect x="-32" y="-8" width="126" height="16" rx="4" fill="#1a120c" stroke="{INK}" stroke-width="4"/>{sn}
    </g>'''

def figure(id_, fc, torso, legs, shoes, front=""):
    return f'''
  <symbol id="{id_}" viewBox="0 0 400 1200" overflow="visible">
    <ellipse cx="200" cy="1176" rx="150" ry="16" fill="#000" opacity="0.25"/>
    {legs}{shoes}{torso}{fc}{front}
  </symbol>'''

def arms(color, hand, lx=84, rx=316, ly=640):
    return (f'<path d="M92 300 C70 420 70 540 {lx} {ly}" fill="none" stroke="{INK}" stroke-width="56" stroke-linecap="round"/><path d="M92 300 C70 420 70 540 {lx} {ly}" fill="none" stroke="{color}" stroke-width="46" stroke-linecap="round"/>'
            f'<path d="M308 300 C330 420 330 540 {rx} {ly}" fill="none" stroke="{INK}" stroke-width="56" stroke-linecap="round"/><path d="M308 300 C330 420 330 540 {rx} {ly}" fill="none" stroke="{color}" stroke-width="46" stroke-linecap="round"/>'
            f'<circle cx="{lx}" cy="{ly+20}" r="24" fill="{hand}" stroke="{INK}" stroke-width="4"/><circle cx="{rx}" cy="{ly+20}" r="24" fill="{hand}" stroke="{INK}" stroke-width="4"/>')

# ---------- A: rough man, thick beard, scowl, SNOW on shoulders + boots, red cold cheeks ----------
beard = '<path d="M126 176 C130 222 156 246 200 250 C244 246 270 222 274 176 C258 194 240 200 228 198 C218 210 182 210 172 198 C160 200 142 194 126 176 Z" fill="#3a2414" stroke="#15141f" stroke-width="4"/><path d="M170 192 C184 184 216 184 230 192" fill="none" stroke="#3a2414" stroke-width="12" stroke-linecap="round"/>'
faceA = face("#d6a07a", "#bd8660", "",
    '<path d="M122 120 C112 46 160 26 204 28 C256 30 292 58 280 122 C268 90 238 76 200 78 C170 78 140 90 122 120 Z" fill="#3a2414" stroke="#15141f" stroke-width="4"/>',
    '<ellipse cx="170" cy="140" rx="17" ry="12" fill="#fff" stroke="#15141f" stroke-width="3"/><ellipse cx="230" cy="140" rx="17" ry="12" fill="#fff" stroke="#15141f" stroke-width="3"/><circle cx="170" cy="141" r="7" fill="#2a1a10"/><circle cx="230" cy="141" r="7" fill="#2a1a10"/><path d="M146 120 L190 130 M210 130 L254 120" stroke="#2a180c" stroke-width="10" stroke-linecap="round"/>',
    beard + '<path d="M176 204 C190 196 210 196 224 204" fill="none" stroke="#15141f" stroke-width="5" stroke-linecap="round"/>',
    '<ellipse cx="150" cy="172" rx="16" ry="9" fill="#e8505a" opacity="0.55"/><ellipse cx="250" cy="172" rx="16" ry="9" fill="#e8505a" opacity="0.55"/>')
def shoulder_snow(side):
    """Irregular fresh-snow clumps piled on the shoulder line, plus loose flakes."""
    pts = []
    for i in range(7):
        u = i / 6 + random.uniform(-0.04, 0.04)
        x = 170 - 82 * u if side < 0 else 230 + 82 * u
        y = 244 + 56 * max(u, 0) ** 1.3 + random.uniform(-4, 3)
        r = random.uniform(9, 19)
        bumps = " ".join(f"{x + r*math.cos(a)*random.uniform(0.75,1.15):.0f},{y - 3 + r*0.62*math.sin(a)*random.uniform(0.75,1.2):.0f}" for a in [k*math.pi/5 for k in range(10)])
        pts.append(f'<polygon points="{bumps}" fill="#ffffff" stroke="#a8c8e0" stroke-width="2" stroke-linejoin="round"/>')
    for _ in range(6):
        fx = (random.uniform(100, 170) if side < 0 else random.uniform(230, 300)); fy = random.uniform(300, 420)
        pts.append(f'<circle cx="{fx:.0f}" cy="{fy:.0f}" r="{random.uniform(2.5, 4.5):.1f}" fill="#ffffff"/>')
    return "".join(pts)
snowA = shoulder_snow(-1) + shoulder_snow(1) + '<g fill="#ffffff"><circle cx="120" cy="340" r="4"/><circle cx="286" cy="352" r="4"/><circle cx="140" cy="380" r="3"/><circle cx="262" cy="396" r="3"/></g>'
torsoA = f'''<path d="M88 300 C88 258 128 240 168 238 L232 238 C272 240 312 258 312 300 L326 760 L74 760 Z" fill="#5a3a26" stroke="{INK}" stroke-width="5"/>
    <path d="M168 238 L200 320 L232 238 Z" fill="#8a7a64" stroke="{INK}" stroke-width="4"/>
    <path d="M200 320 L200 760" stroke="{INK}" stroke-width="4"/>
    <g fill="#c9a24a"><circle cx="214" cy="420" r="7"/><circle cx="214" cy="520" r="7"/><circle cx="214" cy="620" r="7"/></g>
    {arms("#5a3a26", "#d6a07a")}'''
legsA = f'<path d="M130 740 L140 1090 L190 1090 L198 760 Z M270 740 L260 1090 L210 1090 L202 760 Z" fill="#2c3440" stroke="{INK}" stroke-width="5"/>'
figA = figure("figA", faceA, torsoA, legsA, boot(168, True, snow=True) + boot(232, False, snow=True), front=snowA)

# ---------- B: sweet smiling woman, cream coat, dry; holds a MELTED chocolate bar dripping onto her glove ----------
faceB = face("#f0c49b", "#dcab82",
    '<path d="M108 170 C92 60 150 28 204 28 C262 30 312 64 294 170 C306 230 290 270 262 280 L140 280 C112 270 96 230 108 170 Z" fill="#7a4424" stroke="#15141f" stroke-width="5"/>',
    '<path d="M124 132 C120 62 168 44 212 46 C254 48 284 72 278 132 C266 98 240 86 210 88 C186 104 150 112 124 132 Z" fill="#7a4424" stroke="#15141f" stroke-width="4"/>',
    '<path d="M152 148 C162 136 182 136 192 148" fill="none" stroke="#15141f" stroke-width="6" stroke-linecap="round"/><path d="M208 148 C218 136 238 136 248 148" fill="none" stroke="#15141f" stroke-width="6" stroke-linecap="round"/>',
    '<path d="M168 196 C186 220 214 220 232 196" fill="#ffffff" stroke="#15141f" stroke-width="4"/><path d="M168 196 C186 206 214 206 232 196" fill="none" stroke="#15141f" stroke-width="3"/>',
    '<ellipse cx="148" cy="178" rx="16" ry="9" fill="#e88a8a" opacity="0.35"/><ellipse cx="252" cy="178" rx="16" ry="9" fill="#e88a8a" opacity="0.35"/>')
torsoB = f'''<path d="M96 300 C96 258 134 240 170 238 L230 238 C266 240 304 258 304 300 L330 820 L70 820 Z" fill="#efe3c8" stroke="{INK}" stroke-width="5"/>
    <path d="M170 238 L200 330 L230 238 Z" fill="#c8102e" stroke="{INK}" stroke-width="4"/>
    <g fill="#c9a24a"><circle cx="200" cy="420" r="8"/><circle cx="200" cy="520" r="8"/><circle cx="200" cy="620" r="8"/><circle cx="200" cy="720" r="8"/></g>
    <path d="M308 300 C330 420 330 540 316 640" fill="none" stroke="{INK}" stroke-width="56" stroke-linecap="round"/><path d="M308 300 C330 420 330 540 316 640" fill="none" stroke="#efe3c8" stroke-width="46" stroke-linecap="round"/>
    <circle cx="316" cy="660" r="24" fill="#a8744a" stroke="{INK}" stroke-width="4"/>
    <!-- left arm bent up: gloved hand at chest height holding the chocolate -->
    <path d="M92 300 C60 400 70 470 120 480" fill="none" stroke="{INK}" stroke-width="56" stroke-linecap="round"/><path d="M92 300 C60 400 70 470 120 480" fill="none" stroke="#efe3c8" stroke-width="46" stroke-linecap="round"/>'''
chocolate = f'''<!-- MELTED chocolate bar: bigger, squares visible on the top half, bent + dripping onto the glove -->
    <g transform="translate(124 488) scale(1.18) translate(-124 -488)">
      <path d="M96 470 L152 410 C164 398 184 404 186 420 C188 436 176 452 168 470 C158 494 150 514 146 536 L128 532 C126 508 110 488 96 470 Z" fill="#5a3218" stroke="{INK}" stroke-width="4"/>
      <g stroke="#3a1e0c" stroke-width="3"><path d="M132 432 L150 450 M146 418 L164 436 M118 448 L136 466"/></g>
      <g fill="#7a4a28"><rect x="140" y="424" width="12" height="10" transform="rotate(-45 146 429)"/><rect x="154" y="412" width="12" height="10" transform="rotate(-45 160 417)"/><rect x="126" y="440" width="12" height="10" transform="rotate(-45 132 445)"/></g>
      <!-- torn wrapper: silver foil + red label -->
      <path d="M92 476 L132 520 L112 540 L74 500 Z" fill="#c9ced6" stroke="{INK}" stroke-width="3"/>
      <path d="M74 500 L112 540 L96 556 L58 518 Z" fill="#c8102e" stroke="{INK}" stroke-width="3"/>
      <ellipse cx="118" cy="496" rx="30" ry="26" fill="#a8744a" stroke="{INK}" stroke-width="4"/>
      <path d="M138 506 C140 524 136 538 140 554 C144 562 152 560 152 548 C152 534 148 520 150 508 Z" fill="#5a3218" stroke="#3a1e0c" stroke-width="2"/>
      <path d="M110 504 C108 518 112 528 108 540 C106 548 118 550 120 540 C122 528 118 516 120 506 Z" fill="#5a3218" stroke="#3a1e0c" stroke-width="2"/>
      <ellipse cx="124" cy="504" rx="18" ry="7" fill="#5a3218"/>
      <circle cx="146" cy="574" r="5" fill="#5a3218"/><circle cx="114" cy="562" r="4" fill="#5a3218"/>
    </g>'''
legsB = f'<path d="M150 810 L158 1100 L190 1100 L194 810 Z M250 810 L242 1100 L210 1100 L206 810 Z" fill="#3a3440" stroke="{INK}" stroke-width="4"/>'
figB = figure("figB", faceB, torsoB, legsB, boot(172, True, "#6a4426") + boot(228, False, "#6a4426"), front=chocolate)

# ---------- C: calm old man, FROST on scarf + hat, pink cold nose, rubbing hands ----------
faceC = face("#e8b494", "#d0987a", "",
    '<path d="M118 120 C120 92 140 84 150 92 L150 126 Z M282 120 C280 92 260 84 250 92 L250 126 Z" fill="#d8d8d8" stroke="#15141f" stroke-width="3"/>',
    '<ellipse cx="170" cy="146" rx="15" ry="11" fill="#fff" stroke="#15141f" stroke-width="3"/><ellipse cx="230" cy="146" rx="15" ry="11" fill="#fff" stroke="#15141f" stroke-width="3"/><circle cx="170" cy="147" r="6" fill="#3a2a1a"/><circle cx="230" cy="147" r="6" fill="#3a2a1a"/><path d="M150 126 L188 124 M212 124 L250 126" stroke="#bdbdbd" stroke-width="8" stroke-linecap="round"/>',
    '<path d="M174 204 C190 214 210 214 226 204" fill="none" stroke="#15141f" stroke-width="5" stroke-linecap="round"/>',
    '<ellipse cx="201" cy="170" rx="13" ry="11" fill="#f07a8a" stroke="#15141f" stroke-width="2"/><g stroke="#c9a08a" stroke-width="3" fill="none" opacity="0.8"><path d="M150 112 l16 4 M234 116 l16 -4"/></g>')
hatC = f'''<path d="M118 92 C118 30 160 8 200 8 C240 8 282 30 282 92 Z" fill="#2a5c8c" stroke="{INK}" stroke-width="5"/>
    <rect x="110" y="80" width="180" height="30" rx="12" fill="#1f4a72" stroke="{INK}" stroke-width="4"/>
    <path d="M112 108 L288 108" stroke="#eaf6ff" stroke-width="7" stroke-linecap="round"/>
    <circle cx="200" cy="10" r="16" fill="#efe3c8" stroke="{INK}" stroke-width="3"/>
    <path d="M118 40 C150 22 250 22 282 40" stroke="#ffffff" stroke-width="5" opacity="0.8" fill="none"/>
    {frost([(130, 70), (160, 50), (200, 40), (240, 50), (270, 70), (150, 96), (190, 96), (230, 96), (270, 94)])}'''
scarfC = f'''<path d="M130 240 C160 270 240 270 270 240 L280 280 C240 304 160 304 120 280 Z" fill="#c8102e" stroke="{INK}" stroke-width="4"/>
    <path d="M220 280 L236 420 L200 424 L196 290 Z" fill="#c8102e" stroke="{INK}" stroke-width="4"/>
    <g stroke="#7a0d1e" stroke-width="4"><path d="M150 262 L156 286 M190 270 L192 296 M230 268 L228 294 M214 350 L232 348"/></g>
    <path d="M120 280 C160 304 240 304 280 280" fill="none" stroke="#eaf6ff" stroke-width="7" stroke-linecap="round"/>
    <path d="M130 240 C160 270 240 270 270 240" fill="none" stroke="#eaf6ff" stroke-width="6" stroke-linecap="round"/>
    <path d="M200 424 L236 420" stroke="#eaf6ff" stroke-width="7" stroke-linecap="round"/>
    {frost([(140, 262), (170, 274), (205, 278), (240, 272), (264, 258), (214, 320), (226, 380), (206, 404)])}'''
torsoC = f'''<path d="M96 300 C96 258 132 240 170 238 L230 238 C268 240 304 258 304 300 L318 780 L82 780 Z" fill="#6a6f7a" stroke="{INK}" stroke-width="5"/>
    <path d="M200 300 L200 780" stroke="{INK}" stroke-width="4"/>
    <!-- arms meeting in front: rubbing hands -->
    <path d="M98 300 C70 400 100 470 180 500" fill="none" stroke="{INK}" stroke-width="54" stroke-linecap="round"/><path d="M98 300 C70 400 100 470 180 500" fill="none" stroke="#6a6f7a" stroke-width="44" stroke-linecap="round"/>
    <path d="M302 300 C330 400 300 470 220 500" fill="none" stroke="{INK}" stroke-width="54" stroke-linecap="round"/><path d="M302 300 C330 400 300 470 220 500" fill="none" stroke="#6a6f7a" stroke-width="44" stroke-linecap="round"/>
    <ellipse cx="186" cy="500" rx="26" ry="22" fill="#e8b494" stroke="{INK}" stroke-width="4"/><ellipse cx="214" cy="496" rx="26" ry="22" fill="#e8b494" stroke="{INK}" stroke-width="4"/>
    <g stroke="#ffffff" stroke-width="4" stroke-linecap="round" opacity="0.9"><path d="M160 470 l-14 -8 M240 468 l14 -8 M156 520 l-14 6 M246 516 l14 6"/></g>'''
legsC = f'<path d="M134 770 L142 1090 L190 1090 L198 790 Z M266 770 L258 1090 L210 1090 L202 790 Z" fill="#4a4a52" stroke="{INK}" stroke-width="5"/>'
figC = figure("figC", faceC, torsoC, legsC, boot(168, True, "#2a2420") + boot(232, False, "#2a2420"), front=scarfC + hatC)

headA = f'''
  <symbol id="headA" viewBox="0 0 400 420" overflow="visible">
    <path d="M88 300 C88 268 128 250 168 248 L232 248 C272 250 312 268 312 300 L330 420 L70 420 Z" fill="#5a3a26" stroke="{INK}" stroke-width="5"/>
    <path d="M168 248 L200 320 L232 248 Z" fill="#8a7a64" stroke="{INK}" stroke-width="4"/>
    {faceA}
    {shoulder_snow(-1)}{shoulder_snow(1)}
  </symbol>'''

lodge = f'''
  <linearGradient id="planks" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c88a52"/><stop offset="1" stop-color="#b07440"/></linearGradient>
  <linearGradient id="snowSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfe0ee"/><stop offset="1" stop-color="#f4f8fc"/></linearGradient>
  <radialGradient id="fireGlow"><stop offset="0" stop-color="#ffb04a" stop-opacity="0.9"/><stop offset="1" stop-color="#ff7a1a" stop-opacity="0"/></radialGradient>
  <symbol id="lodge" viewBox="0 0 1080 1920">
    <rect width="1080" height="1920" fill="url(#planks)"/>
    <g stroke="#8a5a30" stroke-width="5" opacity="0.6">{''.join(f'<line x1="0" y1="{y}" x2="1080" y2="{y}"/>' for y in range(120, 1300, 90))}</g>
    <!-- big snowy window -->
    <rect x="40" y="240" width="560" height="760" rx="20" fill="#7a4a2a" stroke="{INK}" stroke-width="6"/>
    <rect x="66" y="266" width="508" height="708" fill="url(#snowSky)"/>
    <path d="M66 820 L200 760 L340 800 L460 740 L574 790 L574 974 L66 974 Z" fill="#ffffff"/>
    <g fill="#5a7a6a"><path d="M150 800 L190 680 L230 800 Z"/><path d="M420 780 L470 640 L520 780 Z"/></g>
    <g fill="#ffffff"><path d="M174 730 L190 680 L206 730 Z"/><path d="M450 690 L470 640 L490 690 Z"/></g>
    <g fill="#ffffff" opacity="0.95">{''.join(f'<circle cx="{random.uniform(80, 560):.0f}" cy="{random.uniform(280, 960):.0f}" r="{random.choice([3, 4, 5, 6])}"/>' for _ in range(70))}</g>
    <rect x="310" y="266" width="16" height="708" fill="#7a4a2a"/><rect x="66" y="610" width="508" height="16" fill="#7a4a2a"/>
    <!-- fireplace glowing (right) -->
    <rect x="660" y="620" width="380" height="560" fill="#8a7a6a" stroke="{INK}" stroke-width="6"/>
    <rect x="720" y="820" width="260" height="300" rx="10" fill="#3a2a20"/>
    <path d="M760 1110 C760 1000 800 980 820 920 C840 990 860 960 870 900 C890 980 940 1000 930 1110 Z" fill="#ffb04a"/>
    <path d="M800 1110 C800 1040 830 1030 846 990 C860 1040 890 1050 880 1110 Z" fill="#ffe08a"/>
    <circle cx="850" cy="1000" r="300" fill="url(#fireGlow)"/>
    <!-- warm lamps -->
    <g filter="url(#glow)"><ellipse cx="760" cy="300" rx="50" ry="34" fill="#ffd58a"/><ellipse cx="960" cy="300" rx="50" ry="34" fill="#ffd58a"/></g>
    <rect x="752" y="200" width="16" height="70" fill="#c9a24a"/><rect x="952" y="200" width="16" height="70" fill="#c9a24a"/>
    <ellipse cx="540" cy="700" rx="700" ry="760" fill="url(#lamp)" opacity="0.55"/>
    <rect x="0" y="1180" width="1080" height="740" fill="#8a5a34"/>
    <g stroke="#6a4224" stroke-width="5">{''.join(f'<line x1="{x}" y1="1180" x2="{x - 80}" y2="1920"/>' for x in range(60, 1200, 140))}</g>
    <ellipse cx="459" cy="1420" rx="420" ry="120" fill="#c8402e" opacity="0.7"/>
  </symbol>'''
(HERE / "scenes/_defs.svg").write_text(base + figA + figB + figC + headA + lodge + "\n</defs>")

def svg(body): return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920">\n{body}\n  <rect width="1080" height="1920" filter="url(#grit)"/>\n</svg>\n'
S = HERE / "scenes"
S.joinpath("01-face.svg").write_text(svg('''  <use href="#lodge" width="1080" height="1920"/>
  <rect width="1080" height="1920" fill="#f6e2b8" opacity="0.35"/>
  <use href="#headA" x="-430" y="80" width="1940" height="2037"/>
  <ellipse cx="400" cy="760" rx="560" ry="640" fill="url(#lamp)" opacity="0.4"/>'''))
S.joinpath("02-setup.svg").write_text(svg(f'''  <use href="#lodge" width="1080" height="1920"/>
  <!-- table with the EMPTY bracelet box -->
  <rect x="0" y="1060" width="1080" height="860" fill="#7a4a2a" stroke="{INK}" stroke-width="6"/>
  <rect x="0" y="1060" width="1080" height="30" fill="#9a6a3a"/>
  <g transform="translate(230 960)">
    <path d="M0 40 L440 40 L420 -110 L20 -110 Z" fill="#3a0a14" stroke="{INK}" stroke-width="5"/>
    <path d="M20 30 L420 30 L402 -96 L38 -96 Z" fill="#c8102e" stroke="#e3b04b" stroke-width="5"/>
    <path d="M-10 40 L450 40 L440 190 L0 190 Z" fill="#3a0a14" stroke="{INK}" stroke-width="5"/>
    <path d="M14 56 L426 56 L418 160 L22 160 Z" fill="#c8102e" stroke="#e3b04b" stroke-width="5"/>
    <ellipse cx="220" cy="108" rx="150" ry="34" fill="none" stroke="#7a0a1c" stroke-width="14"/>
  </g>
  <use href="#tlamp" x="760" y="880" width="130" height="217"/>'''))
def place(h, feet=1330): return feet - 1170 * h / 1200
def solo(fig, h, cx):
    w = 400 * h / 1200
    return svg(f'''  <use href="#lodge" width="1080" height="1920"/>
  <ellipse cx="{cx}" cy="900" rx="360" ry="640" fill="#fff6dc" opacity="0.18" filter="url(#blur)"/>
  <use href="#{fig}" x="{cx - w/2:.0f}" y="{place(h):.0f}" width="{w:.0f}" height="{h}"/>''')
S.joinpath("03-a.svg").write_text(solo("figA", 1100, 470))
S.joinpath("04-b.svg").write_text(solo("figB", 1100, 470))
S.joinpath("05-c.svg").write_text(solo("figC", 1100, 470))
L = ['  <use href="#lodge" width="1080" height="1920"/>']
for fig, h, cx in (("figA", 1000, 175), ("figB", 930, 465), ("figC", 960, 755)):
    w = 400 * h / 1200
    L.append(f'  <use href="#{fig}" x="{cx - w/2:.0f}" y="{place(h):.0f}" width="{w:.0f}" height="{h}"/>')
S.joinpath("06-lineup.svg").write_text(svg("\n".join(L)))

def story(ending_line, ending_text):
    top = [{"text": f"CASE #{CASE}", "x": 175, "y": 190, "size": 46, "color": [255, 214, 64], "pop": False}]
    abc = {"text": "A, B or C? 👇", "x": 205, "y": 255, "size": 52, "pop": False}
    hook = {"text": "ONE OF THEM IS LYING", "y": 345, "size": 100, "pop": False}
    return {
     "title": f"Case #{CASE}: The Melted Chocolate", "voice": "am_michael", "speed": 1.18,
     "music": "noir", "music_volume": 0.65, "ambience": "lodge", "ambience_volume": 0.12,
     "chatter": True, "chatter_volume": 0.03, "fade": False, "vignette": 80,
     "layout": {"cx": 470, "max_w": 880, "cap_chars": 14},
     "lines": [
      {"at": 0.05, "text": "One of them is lying. Most people get this wrong.", "caption_y": 1230},
      {"at": 2.6, "text": "A bracelet was stolen two hours ago. All three say they just came in from the snow.", "caption_y": 1230},
      {"at": 9.1, "text": f"Who's lying? Send this to someone who'll get it wrong. {ending_line}", "caption_y": 1230}],
     "shots": [
      {"id": "01", "duration": 2.0, "svg": "scenes/01-face.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.454, 0.42], "c1": [0.454, 0.42], "ease": "linear"}, "punch": False,
       "overlays": top + [hook], "sfx": "hit"},
      {"id": "02", "duration": 1.0, "svg": "scenes/02-setup.svg", "motion": {"z0": 1.0, "z1": 1.1, "c0": [0.42, 0.45], "c1": [0.42, 0.5], "ease": "out"}, "punch": False,
       "fx": ["snow"], "snow_box": [66, 266, 574, 974],
       "overlays": top + [{"text": "Stolen", "y": 300, "size": 96}, {"text": "2 hours ago", "y": 405, "size": 96, "color": [255, 214, 64]}]},
      {"id": "03", "duration": 2.0, "svg": "scenes/03-a.svg", "motion": {"z0": 1.55, "z1": 1.25, "c0": [0.44, 0.36], "c1": [0.44, 0.58], "ease": "mix"}, "punch": False, "fx": ["flicker"],
       "overlays": top + [abc, {"type": "label", "text": "A", "x": 150, "y": 520}], "sfx": "whoosh"},
      {"id": "04", "duration": 2.0, "svg": "scenes/04-b.svg", "motion": {"z0": 1.5, "z1": 1.58, "c0": [0.44, 0.36], "c1": [0.44, 0.37]}, "fx": ["sway", "flicker"],
       "overlays": top + [abc, {"type": "label", "text": "B", "x": 150, "y": 520}], "sfx": "whoosh"},
      {"id": "05", "duration": 2.0, "svg": "scenes/05-c.svg", "motion": {"z0": 1.5, "z1": 1.58, "c0": [0.44, 0.36], "c1": [0.44, 0.37]}, "fx": ["sway", "flicker"],
       "overlays": top + [abc, {"type": "label", "text": "C", "x": 150, "y": 520}], "sfx": "whoosh"},
      {"id": "06", "duration": 2.0, "svg": "scenes/06-lineup.svg", "motion": {"z0": 1.0, "z1": 1.05, "c0": [0.46, 0.5], "c1": [0.46, 0.5], "ease": "linear"}, "punch": False,
       "overlays": top + [abc, {"text": "Who's lying? 👇", "y": 350, "size": 84, "pop": False},
                          {"type": "label", "text": "A", "x": 175, "y": 1000, "size": 90},
                          {"type": "label", "text": "B", "x": 465, "y": 1000, "size": 90},
                          {"type": "label", "text": "C", "x": 755, "y": 1000, "size": 90}], "sfx": "hit"},
      {"id": "07", "duration": 3.0, "image_of": "01", "motion": {"z0": 1.05, "z1": 1.0, "c0": [0.454, 0.42], "c1": [0.454, 0.42], "ease": "linear"}, "punch": False,
       "overlays": top + [{"text": "Send this to someone", "y": 290, "size": 70, "end": 2.7},
                          {"text": "who'll get it wrong 😈", "y": 375, "size": 70, "color": [255, 214, 64], "end": 2.7},
                          {"text": ending_text[0], "y": 480, "size": 60, "start": 0.6, "end": 2.7},
                          {"text": ending_text[1], "y": 555, "size": 60, "start": 0.6, "end": 2.7},
                          dict(hook, start=2.7)], "sfx": "whoosh"}]}
(HERE / "story.json").write_text(json.dumps(story("Answer in my Story tomorrow.", ["✅ Answer in my Story", "tomorrow"]), indent=2, ensure_ascii=False))
(HERE / "story-youtube.json").write_text(json.dumps(story("Answer in the comments tomorrow.", ["✅ Answer in the", "comments tomorrow"]), indent=2, ensure_ascii=False))
print("ok")

"""Generates the art for the Manga theme (dark, Tokyo Ghoul homage). All original drawings.

  chrome/themes/manga/assets/page.svg       new tab: a dark manga page, five panels
  chrome/themes/manga/assets/shock.svg      can't-connect page
  chrome/themes/manga/assets/centipede.svg  crawls across the bookmarks bar
  chrome/themes/manga/assets/icon.svg       switcher menu icon (the red eye)
  chrome/themes/manga/assets/still/*.svg    the same without animation (manga.freeze)
  chrome/themes/manga/dock-icons.css        ink icons for the bookmarks bar

Run: python tools/make_ghoul.py
"""
import math
import random
import re
from pathlib import Path
from urllib.parse import quote

MANGA = Path(__file__).resolve().parent.parent / "chrome" / "themes" / "manga"
A = MANGA / "assets"
(A / "still").mkdir(parents=True, exist_ok=True)

GUTTER, PANEL, BLACK = "#0e0d11", "#1a1820", "#08070a"
INK, LINE, TONE = "#d9d4c9", "#77737a", "#6d6a70"
RED, DARKRED, WARM = "#d4142a", "#5e0712", "#c9a25a"
LETTER = "'Ink Free', 'Segoe Print', 'Comic Sans MS', cursive"
SFX = "Impact, 'Arial Black', sans-serif"
JP = "'Yu Gothic UI', 'Yu Gothic', Meiryo, sans-serif"
rnd = random.Random(20)


def still(svg):
    """Same drawing with every CSS and SMIL animation stopped."""
    svg = svg.replace("</style>", "  * { animation: none !important; }\n</style>", 1)
    return re.sub(r"<animate[^>]*/>", "", svg)


def poly(pts):
    return " ".join(f"{x},{y}" for x, y in pts)


def focus_lines(cx, cy, n, r_in, r_out, color, cls=""):
    out = []
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        w = rnd.uniform(.004, .014)
        ri = r_in * rnd.uniform(.85, 1.35)
        pts = [(cx + r_out * math.cos(a - w), cy + r_out * math.sin(a - w)),
               (cx + r_out * math.cos(a + w), cy + r_out * math.sin(a + w)),
               (cx + ri * math.cos(a), cy + ri * math.sin(a))]
        out.append("M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts) + "Z")
    return f'<path class="{cls}" d="{" ".join(out)}" fill="{color}"/>'


def kakugan(x, y, s=1.0, flip=False, cls=""):
    """The red eye: black sclera, glowing red iris, veins spreading over the skin."""
    veins = "".join(
        f'<path d="M{vx} {vy} q{qx} {qy} {ex} {ey}" stroke="{RED}" stroke-width="{w}" fill="none" stroke-linecap="round"/>'
        for vx, vy, qx, qy, ex, ey, w in [
            (100, 6, 26, 8, 44, 34, 3), (112, -10, 30, -6, 52, 4, 2.5), (80, 24, 14, 22, 12, 52, 3),
            (40, 30, 2, 24, -10, 50, 2.5), (120, 20, 20, 16, 26, 44, 2)])
    return f"""<g transform="translate({x} {y}) scale({-s if flip else s} {s})"><g class="{cls}">
      {veins}
      <path d="M-120 0 Q0 -95 120 -10 Q0 60 -120 0Z" fill="{BLACK}" stroke="{INK}" stroke-width="4"/>
      <path d="M-128 -4 Q0 -112 132 -16" stroke="{INK}" stroke-width="12" fill="none" stroke-linecap="round"/>
      <circle cy="-12" r="48" fill="{RED}"/>
      <circle cy="-12" r="48" fill="none" stroke="#ff5a6b" stroke-width="3" opacity=".7"/>
      <path d="M0 -60 L5 -12 L0 36 L-5 -12Z" fill="{BLACK}"/>
      <circle cx="-18" cy="-32" r="7" fill="#ffd7da"/>
    </g></g>"""


def human_eye(x, y, s=1.0, cls=""):
    return f"""<g transform="translate({x} {y}) scale({s})"><g class="{cls}">
      <path d="M-120 0 Q0 -95 120 -10 Q0 60 -120 0Z" fill="#9b968c" stroke="{INK}" stroke-width="4"/>
      <path d="M-128 -4 Q0 -112 132 -16" stroke="{INK}" stroke-width="12" fill="none" stroke-linecap="round"/>
      <circle cy="-12" r="46" fill="#2b2a30" stroke="{BLACK}" stroke-width="4"/>
      <circle cy="-12" r="21" fill="{BLACK}"/>
      <circle cx="-16" cy="-30" r="9" fill="{INK}"/>
    </g></g>"""


def tentacle(d, width=26, cls="kag"):
    """A segmented red tentacle: base stroke, dark segment bands, thin highlight."""
    return (f'<g class="{cls}"><path d="{d}" stroke="{RED}" stroke-width="{width}" fill="none" stroke-linecap="round"/>'
            f'<path d="{d}" stroke="{DARKRED}" stroke-width="{width}" fill="none" stroke-dasharray="4 24"/>'
            f'<path d="{d}" stroke="#ff6b7a" stroke-width="2" fill="none" opacity=".6"/></g>')


def lily(x, y, s=1.0):
    """Red spider lily: long curled petals and thread-like stamens on a bare stem."""
    parts = [f'<path d="M0 0 Q6 70 -4 150" stroke="#2c3a2c" stroke-width="5" fill="none"/>']
    for i in range(7):
        ang = -170 + i * 27
        parts.append(f'<g transform="rotate({ang})"><path d="M0 0 Q26 -7 46 -2 Q54 2 48 -10" stroke="{RED}" stroke-width="6" fill="none" stroke-linecap="round"/>'
                     f'<path d="M0 0 Q40 -18 70 -22" stroke="#ff4a5c" stroke-width="1.4" fill="none"/>'
                     f'<circle cx="70" cy="-22" r="2" fill="#ff4a5c"/></g>')
    return f'<g transform="translate({x} {y}) scale({s})">{"".join(parts)}</g>'


# ---------------------------------------------------------------- the panels
PA = [(40, 40), (1100, 40), (1060, 470), (40, 470)]           # 20th ward in the rain
PB = [(1124, 40), (1880, 40), (1880, 470), (1084, 470)]       # one human eye, one red eye
PC = [(40, 494), (640, 494), (600, 1040), (40, 1040)]         # 1000 - 7
PD = [(664, 494), (1300, 494), (1340, 1040), (624, 1040)]     # the title
PE = [(1324, 494), (1880, 494), (1880, 1040), (1364, 1040)]   # the masked figure

windows = []
for bx, bw, bh in [(60, 120, 260), (190, 90, 200), (290, 150, 300), (450, 110, 230), (570, 140, 330),
                   (720, 100, 250), (830, 130, 290), (970, 120, 210)]:
    top = 470 - bh
    windows.append(f'<rect x="{bx}" y="{top}" width="{bw}" height="{bh}" fill="{BLACK}" stroke="#2b2932" stroke-width="2"/>')
    for wy in range(top + 18, 400, 26):
        for wx in range(bx + 12, bx + bw - 14, 22):
            if rnd.random() < .2:
                cls = f"win w{rnd.randint(1, 3)}" if rnd.random() < .35 else ""
                windows.append(f'<rect class="{cls}" x="{wx}" y="{wy}" width="9" height="12" fill="{WARM}" opacity=".75"/>')

petals = "".join(
    f'<path class="petal p{rnd.randint(1, 4)}" d="M{rnd.randint(30, 1890)} {rnd.randint(30, 1050)} q10 -8 20 0 q-10 8 -20 0z" fill="{RED}" opacity=".85"/>'
    for _ in range(26))

NUMBERS = [993, 986, 979, 972, 965, 958, 951, 944]
count = "".join(
    f'<text x="340" y="640" text-anchor="middle" opacity="{1 if i == 0 else 0}" style="font: 110px {SFX}; fill: {RED}; letter-spacing: 4px">{n}'
    f'<animate attributeName="opacity" values="1;0;0" keyTimes="0;{1 / len(NUMBERS):.3f};1" calcMode="discrete" '
    f'begin="{i * 1.2:.1f}s" dur="{len(NUMBERS) * 1.2:.1f}s" repeatCount="indefinite"/></text>'
    for i, n in enumerate(NUMBERS))

page = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
<defs>
  <pattern id="tone" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><circle cx="4.5" cy="4.5" r="1.5" fill="{LINE}"/></pattern>
  <pattern id="rain" width="60" height="120" patternUnits="userSpaceOnUse"><path d="M12 0 l-5 28 M40 50 l-5 28 M26 92 l-4 20" stroke="#8d93a8" stroke-opacity=".5" stroke-width="1.4" stroke-linecap="round"/></pattern>
  <radialGradient id="moonGlow"><stop offset="0" stop-color="{RED}" stop-opacity=".55"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
  <linearGradient id="spot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{INK}" stop-opacity=".22"/><stop offset="1" stop-color="{INK}" stop-opacity=".02"/></linearGradient>
  <clipPath id="cA"><polygon points="{poly(PA)}"/></clipPath>
  <clipPath id="cB"><polygon points="{poly(PB)}"/></clipPath>
  <clipPath id="cC"><polygon points="{poly(PC)}"/></clipPath>
  <clipPath id="cD"><polygon points="{poly(PD)}"/></clipPath>
  <clipPath id="cE"><polygon points="{poly(PE)}"/></clipPath>
</defs>
<style>
  .win {{ animation: win 7s steps(1) infinite; }} .w2 {{ animation-delay: -2s; }} .w3 {{ animation-delay: -4s; animation-duration: 10s; }}
  @keyframes win {{ 50% {{ opacity: .1; }} }}
  .rain {{ animation: rain .8s linear infinite; }}
  @keyframes rain {{ to {{ transform: translate(-20px, 120px); }} }}
  .blink {{ transform-box: fill-box; transform-origin: center; animation: blink 6s infinite; }}
  @keyframes blink {{ 0%,93%,100% {{ transform: scaleY(1); }} 96% {{ transform: scaleY(.08); }} }}
  .fl1 {{ animation: fl .24s steps(1) infinite; }} .fl2 {{ animation: fl .24s steps(1) infinite reverse; }}
  @keyframes fl {{ 50% {{ opacity: 0; }} }}
  .title {{ transform-box: fill-box; transform-origin: center; animation: shake 6s infinite; }}
  @keyframes shake {{ 0%,88%,100% {{ transform: none; }} 90% {{ transform: translate(-5px,3px) rotate(-1deg); }} 92% {{ transform: translate(5px,-3px) rotate(1deg); }} 94% {{ transform: translate(-3px,2px); }} }}
  .kag {{ transform-box: view-box; transform-origin: 1630px 900px; animation: kag 7s ease-in-out infinite; }}
  .kag.k2 {{ animation-delay: -2s; animation-duration: 9s; }} .kag.k3 {{ animation-delay: -4s; animation-duration: 8s; }} .kag.k4 {{ animation-delay: -6s; animation-duration: 10s; }}
  @keyframes kag {{ 50% {{ transform: rotate(4deg); }} }}
  .beat {{ transform-box: fill-box; transform-origin: center; animation: beat 1.6s infinite; }}
  @keyframes beat {{ 0%,40%,100% {{ transform: scale(1) rotate(-8deg); }} 10% {{ transform: scale(1.2) rotate(-8deg); }} 20% {{ transform: scale(1) rotate(-8deg); }} 30% {{ transform: scale(1.12) rotate(-8deg); }} }}
  .glow {{ animation: glow 3s ease-in-out infinite; }}
  @keyframes glow {{ 50% {{ opacity: .45; }} }}
  .petal {{ animation: fall 22s linear infinite; }}
  .p2 {{ animation-duration: 28s; animation-delay: -9s; }} .p3 {{ animation-duration: 18s; animation-delay: -14s; }} .p4 {{ animation-duration: 34s; animation-delay: -5s; }}
  @keyframes fall {{ from {{ transform: translate(-40px, -1150px); }} to {{ transform: translate(70px, 1150px); }} }}
  .crawl {{ animation: crawl 16s linear infinite; }}
  @keyframes crawl {{ from {{ transform: translateX(-120px); }} to {{ transform: translateX(560px); }} }}
  .legA {{ animation: leg .3s steps(1) infinite; }} .legB {{ animation: leg .3s steps(1) infinite reverse; }}
  @keyframes leg {{ 50% {{ opacity: 0; }} }}
  .arrow {{ animation: arrow 1.4s ease-in-out infinite; }}
  @keyframes arrow {{ 50% {{ transform: translateX(10px); }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<rect width="1920" height="1080" fill="{GUTTER}"/>

<!-- A: 20th ward in the rain -->
<g clip-path="url(#cA)">
  <rect x="40" y="40" width="1060" height="430" fill="{PANEL}"/>
  <rect x="40" y="40" width="1060" height="430" fill="url(#tone)" opacity=".18"/>
  <circle class="glow" cx="880" cy="140" r="170" fill="url(#moonGlow)"/>
  <circle cx="880" cy="140" r="62" fill="#7d0f1c" stroke="{RED}" stroke-width="3"/>
  {"".join(windows)}
  <!-- the coffee shop on the corner -->
  <rect x="400" y="388" width="250" height="82" fill="#16120d" stroke="{WARM}" stroke-width="2"/>
  <rect x="418" y="418" width="214" height="52" fill="{WARM}" opacity=".3"/>
  <text x="525" y="411" text-anchor="middle" style="font: 900 20px {JP}; fill: {WARM}; letter-spacing: 3px">あんていく</text>
  <rect class="rain" x="0" y="-120" width="1200" height="720" fill="url(#rain)"/>
</g>
<polygon points="{poly(PA)}" fill="none" stroke="{LINE}" stroke-width="5" stroke-linejoin="round"/>
<g transform="translate(70 66)">
  <rect width="290" height="74" fill="{BLACK}" stroke="{LINE}" stroke-width="3"/>
  <text x="18" y="32" style="font: 24px {LETTER}; fill: {INK}">Chapter ∞</text>
  <text x="18" y="60" style="font: 18px {LETTER}; fill: {INK}">20th Ward, after dark...</text>
</g>

<!-- B: one human eye, one red eye -->
<g clip-path="url(#cB)">
  <rect x="1080" y="40" width="800" height="430" fill="{PANEL}"/>
  <rect x="1080" y="40" width="800" height="430" fill="url(#tone)" opacity=".15"/>
  <path d="M1110 40 L1880 40 L1880 130 L1820 190 L1770 120 L1700 205 L1640 118 L1560 190 L1500 112 L1420 180 L1370 110 L1290 170 L1240 100 L1110 120Z" fill="#6f6c6b"/>
  {human_eye(1300, 300, cls="blink")}
  {kakugan(1660, 300, flip=True, cls="blink")}
</g>
<polygon points="{poly(PB)}" fill="none" stroke="{LINE}" stroke-width="5" stroke-linejoin="round"/>
<g transform="translate(1480 420)">
  <ellipse rx="112" ry="36" fill="{BLACK}" stroke="{LINE}" stroke-width="3"/>
  <text y="9" text-anchor="middle" style="font: 900 26px {JP}; fill: {INK}">僕は…喰種だ</text>
</g>

<!-- C: 1000 - 7 -->
<g clip-path="url(#cC)">
  <rect x="40" y="494" width="600" height="546" fill="{BLACK}"/>
  <polygon points="300,494 380,494 540,1040 140,1040" fill="url(#spot)"/>
  {count}
  <!-- the empty chair in the spotlight -->
  <g fill="none" stroke="{TONE}" stroke-width="10" stroke-linecap="round">
    <path d="M280 760 V960 M400 760 V960"/><path d="M270 860 H410"/><path d="M280 860 L262 980 M400 860 L418 980"/><path d="M280 780 H400"/>
  </g>
  <ellipse cx="340" cy="985" rx="150" ry="16" fill="#000" opacity=".6"/>
  <!-- a centipede crossing the floor -->
  <g class="crawl"><g transform="translate(60 1000)">
    <g class="legA" stroke="{LINE}" stroke-width="2"><path d="M4 4 l-4 9 M16 4 l-4 9 M28 4 l-4 9 M40 4 l-4 9 M52 4 l-4 9 M64 4 l-4 9"/></g>
    <g class="legB" stroke="{LINE}" stroke-width="2"><path d="M4 4 l4 9 M16 4 l4 9 M28 4 l4 9 M40 4 l4 9 M52 4 l4 9 M64 4 l4 9"/></g>
    <rect x="0" y="-3" width="72" height="9" rx="4.5" fill="{DARKRED}"/>
    <path d="M6 -3 v9 M18 -3 v9 M30 -3 v9 M42 -3 v9 M54 -3 v9 M66 -3 v9" stroke="{BLACK}" stroke-width="1.6"/>
    <circle cx="75" cy="1" r="6" fill="{RED}"/>
    <path d="M79 -3 q8 -6 12 -2 M79 5 q8 6 12 2" stroke="{LINE}" stroke-width="1.5" fill="none"/>
  </g></g>
</g>
<polygon points="{poly(PC)}" fill="none" stroke="{LINE}" stroke-width="5" stroke-linejoin="round"/>
<g transform="translate(120 700)">
  <text x="220" y="0" text-anchor="middle" style="font: 28px {LETTER}; fill: {INK}">what's 1000 minus 7?</text>
</g>

<!-- D: the title -->
<g clip-path="url(#cD)">
  <rect x="600" y="494" width="760" height="546" fill="{PANEL}"/>
  <g class="fl1" opacity=".55">{focus_lines(982, 770, 150, 190, 700, RED)}</g>
  <g class="fl2" opacity=".35">{focus_lines(982, 770, 150, 190, 700, LINE)}</g>
  <ellipse cx="982" cy="770" rx="250" ry="170" fill="{PANEL}"/>
</g>
<polygon points="{poly(PD)}" fill="none" stroke="{LINE}" stroke-width="5" stroke-linejoin="round"/>
<g class="title">
  <text x="982" y="820" text-anchor="middle" style="font: 900 190px {JP}; fill: {RED}; stroke: {BLACK}; stroke-width: 8px; paint-order: stroke">喰種</text>
  <text x="982" y="880" text-anchor="middle" style="font: 34px {SFX}; fill: {INK}; letter-spacing: 8px">NEW TAB</text>
  <text x="982" y="918" text-anchor="middle" style="font: 900 22px {JP}; fill: {TONE}; letter-spacing: 6px">第∞話</text>
</g>

<!-- E: the masked figure -->
<g clip-path="url(#cE)">
  <rect x="1324" y="494" width="560" height="546" fill="{PANEL}"/>
  <rect x="1324" y="494" width="560" height="546" fill="url(#tone)" opacity=".15"/>
  {tentacle("M1600 880 C1520 800 1440 760 1410 620", cls="kag")}
  {tentacle("M1610 860 C1560 760 1560 660 1500 540", cls="kag k2")}
  {tentacle("M1660 860 C1720 760 1720 660 1790 540", cls="kag k3")}
  {tentacle("M1670 880 C1760 800 1830 760 1860 640", cls="kag k4")}
  <!-- coat -->
  <path d="M1500 1040 Q1520 880 1590 860 L1680 860 Q1760 880 1780 1040Z" fill="{BLACK}" stroke="{LINE}" stroke-width="3"/>
  <!-- head, pale hair, mask with one eye covered and a stitched zipper mouth -->
  <circle cx="1635" cy="770" r="92" fill="{BLACK}" stroke="{LINE}" stroke-width="4"/>
  <path d="M1540 760 Q1530 660 1635 668 Q1745 660 1730 760 L1712 716 L1692 750 L1672 700 L1650 740 L1630 696 L1608 742 L1586 702 L1570 752 L1552 720Z" fill="#6f6c6b"/>
  <circle cx="1600" cy="780" r="22" fill="{RED}"/>
  <path d="M1600 760 l3 20 -3 20 -3 -20z" fill="{BLACK}"/>
  <path d="M1650 760 h52 v34 q-26 12 -52 0z" fill="#26242b" stroke="{LINE}" stroke-width="2"/>
  <path d="M1582 830 H1690" stroke="{INK}" stroke-width="3"/>
  <path d="M1590 822 v16 M1604 822 v16 M1618 822 v16 M1632 822 v16 M1646 822 v16 M1660 822 v16 M1674 822 v16" stroke="{INK}" stroke-width="2"/>
  {lily(1420, 930, .9)}{lily(1830, 915, 1.05)}{lily(1500, 985, .7)}
  <text class="beat" x="1420" y="600" style="font: 900 74px {JP}; fill: {RED}; stroke: {BLACK}; stroke-width: 4px; paint-order: stroke">ドクン</text>
</g>
<polygon points="{poly(PE)}" fill="none" stroke="{LINE}" stroke-width="5" stroke-linejoin="round"/>
<g transform="translate(1630 1014)">
  <polygon points="0,-30 226,-30 226,0 0,0" fill="{BLACK}" stroke="{LINE}" stroke-width="3"/>
  <text x="14" y="-8" style="font: 18px {SFX}; fill: {INK}; letter-spacing: 2px">NEXT PAGE</text>
  <g class="arrow"><path d="M146 -15 h50 m-14 -11 l14 11 -14 11" stroke="{RED}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></g>
</g>

{petals}
</svg>
"""

# ---------------------------------------------------------------- can't-connect page
shock = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="380" viewBox="0 0 640 380">
<defs><clipPath id="p"><polygon points="20,20 620,20 600,360 40,360"/></clipPath></defs>
<style>
  .f1 {{ animation: fl .22s steps(1) infinite; }} .f2 {{ animation: fl .22s steps(1) infinite reverse; }}
  @keyframes fl {{ 50% {{ opacity: 0; }} }}
  .eye {{ transform-box: fill-box; transform-origin: center; animation: blink 4s infinite; }}
  @keyframes blink {{ 0%,90%,100% {{ transform: scaleY(1); }} 94% {{ transform: scaleY(.08); }} }}
  .beat {{ transform-box: fill-box; transform-origin: center; animation: beat 1.6s infinite; }}
  @keyframes beat {{ 0%,40%,100% {{ transform: scale(1) rotate(-8deg); }} 10% {{ transform: scale(1.18) rotate(-8deg); }} 30% {{ transform: scale(1.1) rotate(-8deg); }} }}
  .cur {{ animation: fl 1.2s steps(1) infinite; }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<rect width="640" height="380" fill="{GUTTER}"/>
<g clip-path="url(#p)">
  <rect width="640" height="380" fill="{PANEL}"/>
  <g class="f1" opacity=".55">{focus_lines(320, 150, 110, 120, 420, RED)}</g>
  <g class="f2" opacity=".35">{focus_lines(320, 150, 110, 120, 420, LINE)}</g>
  <ellipse cx="320" cy="150" rx="170" ry="90" fill="{PANEL}"/>
  {kakugan(320, 165, s=1.05, cls="eye")}
</g>
<polygon points="20,20 620,20 600,360 40,360" fill="none" stroke="{LINE}" stroke-width="5" stroke-linejoin="round"/>
<text class="beat" x="470" y="90" style="font: 900 56px {JP}; fill: {RED}; stroke: {BLACK}; stroke-width: 3px; paint-order: stroke">ドクン</text>
<text x="320" y="282" text-anchor="middle" style="font: 700 30px {LETTER}; fill: {INK}">something ate your connection</text>
<text x="320" y="326" text-anchor="middle" style="font: 18px Consolas, monospace; fill: {RED}">1000 - 7 = 993... press F5<tspan class="cur">_</tspan></text>
</svg>
"""

# ---------------------------------------------------------------- bookmarks-bar centipede
centipede = f"""<svg xmlns="http://www.w3.org/2000/svg" width="70" height="20" viewBox="0 0 70 20">
<style>
  .a {{ animation: leg .24s steps(1) infinite; }} .b {{ animation: leg .24s steps(1) infinite reverse; }}
  @keyframes leg {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<g class="a" stroke="{LINE}" stroke-width="1.3"><path d="M5 11 l-3 7 M14 11 l-3 7 M23 11 l-3 7 M32 11 l-3 7 M41 11 l-3 7 M50 11 l-3 7"/></g>
<g class="b" stroke="{LINE}" stroke-width="1.3"><path d="M5 11 l3 7 M14 11 l3 7 M23 11 l3 7 M32 11 l3 7 M41 11 l3 7 M50 11 l3 7"/></g>
<rect x="1" y="6" width="56" height="7" rx="3.5" fill="{DARKRED}" stroke="{RED}" stroke-width=".8"/>
<path d="M9 6 v7 M18 6 v7 M27 6 v7 M36 6 v7 M45 6 v7" stroke="{BLACK}" stroke-width="1.2"/>
<circle cx="60" cy="9.5" r="4.6" fill="{RED}"/>
<path d="M63 7 q4 -4 7 -2 M63 12 q4 4 7 2" stroke="{LINE}" stroke-width="1.1" fill="none"/>
</svg>
"""

icon = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M1 8Q8 1.5 15 8Q8 13 1 8Z" fill="{BLACK}" stroke="{INK}" stroke-width="1.1"/><circle cx="8" cy="7.6" r="3" fill="{RED}"/><path d="M8 4.8l.5 2.8-.5 2.8-.5-2.8z" fill="{BLACK}"/></svg>
"""

for name, svg in {"page": page, "shock": shock, "centipede": centipede}.items():
    (A / f"{name}.svg").write_text(svg, encoding="utf-8")
    (A / "still" / f"{name}.svg").write_text(still(svg), encoding="utf-8")
(A / "icon.svg").write_text(icon, encoding="utf-8")

# ---------------------------------------------------------------- ink dock icons
ICON_BODIES = {
    "AI": '<path d="M7 2.5Q7 8 12.5 8Q7 8 7 13.5Q7 8 1.5 8Q7 8 7 2.5Z"/><path d="M12.5 1.5v3M11 3h3" stroke="RED"/>',
    "Social": '<path d="M3 2.5h6.5A1.5 1.5 0 0 1 11 4v3.5A1.5 1.5 0 0 1 9.5 9H6L3.5 11V9H3A1.5 1.5 0 0 1 1.5 7.5V4A1.5 1.5 0 0 1 3 2.5Z"/><path d="M13 6h.5A1 1 0 0 1 14.5 7v3.5a1 1 0 0 1-1 1h-.5v2l-2.5-2H8a1 1 0 0 1-1-1V11"/><path d="M4.5 5.8h4" stroke="RED"/>',
    "Piracy": '<path d="M3 1.5v13"/><path d="M3 2.5h10l-2 3 2 3H3"/><path d="M6 4l2.5 3M8.5 4 6 7" stroke="RED"/>',
    "Tetris": '<path d="M1.5 4h13v4.3h-4.3v4.3H5.8V8.3H1.5Z"/><path d="M5.8 4v4.3M10.2 4v4.3M5.8 8.3h4.4"/><path d="M7 9.8h2" stroke="RED"/>',
    "TFT": '<path d="M8 1.5l5.6 3.25v6.5L8 14.5l-5.6-3.25v-6.5Z"/><path d="M8 5.2l.85 1.75 1.9.25-1.4 1.3.35 1.9L8 9.5l-1.7.9.35-1.9-1.4-1.3 1.9-.25Z" stroke="RED"/>',
    "Chess": '<circle cx="8" cy="4.3" r="2"/><path d="M6.3 6.6h3.4"/><path d="M6.6 6.8 6 11h4l-.6-4.2"/><path d="M4.5 13.8h7l-.8-2.8H5.3Z"/>',
    "Linux": '<rect x="1.5" y="2.5" width="13" height="11" rx="1"/><path d="M4.3 6.3 6.3 8l-2 1.7"/><path d="M8 10.5h3.5" stroke="RED"/>',
    "Other": '<circle cx="8" cy="8" r="3.6"/><path d="M3.2 10.6C.6 12.3 1 13.4 4.4 12.6 7 12 10.2 10.6 12.6 8.9 15.4 7 15.2 5.7 11.9 6.4"/>',
    "Freeze": '<path d="M8 1v14M1.9 4.5l12.2 7M1.9 11.5l12.2-7"/><path d="M6 2.5 8 4l2-1.5M6 13.5 8 12l2 1.5" stroke="RED"/>',
}
FOLDER = '<path d="M1.5 4.5A1.5 1.5 0 0 1 3 3h3l1.5 1.5H13A1.5 1.5 0 0 1 14.5 6v5.5A1.5 1.5 0 0 1 13 13H3a1.5 1.5 0 0 1-1.5-1.5Z"/>'


def ink_url(body):
    body = body.replace('stroke="RED"', f"stroke='{RED}'")
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none' stroke='{INK}' "
           f"stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'>{body}</svg>").replace('"', "'")
    return "data:image/svg+xml," + quote(svg, safe="/:=' ,.-")


ITEM = "#PlacesToolbarItems > .bookmark-item"
css = ["""/* ==========================================================
   Manga dock icons, generated by tools/make_ghoul.py (don't edit by hand).
   Pale ink line icons with a red accent, matched by bookmark/folder name;
   any other folder gets an ink folder.
   ========================================================== */
""", f'{ITEM}[container] > .toolbarbutton-icon {{ content: url("{ink_url(FOLDER)}") !important; }}']
for name, body in ICON_BODIES.items():
    css.append(f'{ITEM}[label="{name}"] > .toolbarbutton-icon {{ content: url("{ink_url(body)}") !important; }}')
(MANGA / "dock-icons.css").write_text("\n".join(css) + "\n", encoding="utf-8")
print("wrote the ghoul art")

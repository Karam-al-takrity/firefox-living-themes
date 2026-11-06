"""Generates the Nocturne animated backgrounds.

  chrome/themes/nocturne/ASSETS/space-scene.svg  - new tab page scene (coding + gaming + space)
  chrome/themes/nocturne/ASSETS/stars.svg        - tiny twinkling star tile for the toolbar
  chrome/themes/nocturne/ASSETS/tagline.svg      - rotating status line under the search box
  chrome/themes/nocturne/ASSETS/center.svg       - wordmark + status line for when the search box is turned off
  chrome/themes/nocturne/ASSETS/*-still.svg      - frozen copies used when nocturne.freeze is on

Colors follow the Cotton Candy palette. Run: python tools/make_scene.py
"""
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "chrome" / "themes" / "nocturne" / "ASSETS"
OUT.mkdir(parents=True, exist_ok=True)

BG, BG2 = "#16121c", "#251b34"
PINK, BLUE, LILAC, GOLD, TEXT = "#ffb3d9", "#b3e5ff", "#d9c2ff", "#fff0a8", "#fdf6ff"

rnd = random.Random(7)


def stars(n, w, h, avoid=None, rmax=2.2):
    out = []
    while len(out) < n:
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3] and rnd.random() < .7:
            continue
        r = rnd.uniform(.6, rmax)
        color = rnd.choice([TEXT, TEXT, TEXT, PINK, BLUE, LILAC, GOLD])
        cls = f"tw tw{rnd.randint(1, 4)}"
        out.append(f'<circle class="{cls}" cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="{color}"/>')
    return "\n".join(out)


def sparkle(x, y, s, color, cls="tw tw2"):
    # four-point star
    p = f"M{x},{y-s} Q{x},{y} {x+s},{y} Q{x},{y} {x},{y+s} Q{x},{y} {x-s},{y} Q{x},{y} {x},{y-s}Z"
    return f'<path class="{cls}" d="{p}" fill="{color}"/>'


def pixel_grid(rows, px, color):
    rects = []
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                rects.append(f'<rect x="{i*px}" y="{j*px}" width="{px}" height="{px}" fill="{color}"/>')
    return "".join(rects)


# an original little pixel critter, two walking frames
CRITTER_A = [
    "...####...",
    "..######..",
    ".##.##.##.",
    ".########.",
    "##########",
    "#.######.#",
    "..#....#..",
    ".#......#.",
]
CRITTER_B = CRITTER_A[:6] + [
    "..#....#..",
    "..##..##..",
]
HEART = [
    ".##.##.",
    "#######",
    "#######",
    ".#####.",
    "..###..",
    "...#...",
]
COIN = [
    ".###.",
    "##.##",
    "##.##",
    "##.##",
    ".###.",
]

scene = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1920 1080" preserveAspectRatio="xMidYMid slice">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG2}"/>
  </linearGradient>
  <radialGradient id="neb1"><stop offset="0" stop-color="{PINK}" stop-opacity=".22"/><stop offset="1" stop-color="{PINK}" stop-opacity="0"/></radialGradient>
  <radialGradient id="neb2"><stop offset="0" stop-color="{BLUE}" stop-opacity=".18"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="neb3"><stop offset="0" stop-color="{LILAC}" stop-opacity=".2"/><stop offset="1" stop-color="{LILAC}" stop-opacity="0"/></radialGradient>
  <radialGradient id="planet" cx=".35" cy=".3" r=".8">
    <stop offset="0" stop-color="#f3e8ff"/><stop offset=".55" stop-color="{LILAC}"/><stop offset="1" stop-color="#8f78bd"/>
  </radialGradient>
  <linearGradient id="shoot" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/>
  </linearGradient>
  <radialGradient id="screenglow"><stop offset="0" stop-color="{BLUE}" stop-opacity=".35"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
  <clipPath id="type1"><rect x="0" y="-20" width="0" height="30"><animate attributeName="width" dur="12s" repeatCount="indefinite" calcMode="discrete" values="0;16;32;48;64;80;96;112;128;144;160;176;192;208;224;240;256;272;288;304;320;336;352;368;384;400;400;0" keyTimes="0;0.006;0.012;0.018;0.024;0.030;0.036;0.042;0.048;0.054;0.060;0.066;0.072;0.078;0.084;0.090;0.096;0.102;0.108;0.114;0.120;0.126;0.132;0.138;0.144;0.150;0.92;1"/></rect></clipPath>
  <clipPath id="type2"><rect x="0" y="-20" width="0" height="30"><animate attributeName="width" dur="12s" repeatCount="indefinite" calcMode="discrete" values="0;16;32;48;64;80;96;112;128;144;160;176;192;208;224;240;256;272;288;304;320;336;352;368;384;400;400;0" keyTimes="0;0.204;0.208;0.212;0.216;0.220;0.224;0.228;0.232;0.236;0.240;0.244;0.248;0.252;0.256;0.260;0.264;0.268;0.272;0.276;0.280;0.284;0.288;0.292;0.296;0.300;0.92;1"/></rect></clipPath>
  <clipPath id="type3"><rect x="0" y="-20" width="0" height="30"><animate attributeName="width" dur="12s" repeatCount="indefinite" calcMode="discrete" values="0;16;32;48;64;80;96;112;128;144;160;176;192;208;224;240;256;272;288;304;320;336;352;368;384;400;400;0" keyTimes="0;0.357;0.364;0.370;0.377;0.384;0.391;0.398;0.404;0.411;0.418;0.425;0.432;0.438;0.445;0.452;0.459;0.466;0.472;0.479;0.486;0.493;0.500;0.506;0.513;0.520;0.92;1"/></rect></clipPath>
</defs>
<style>
  .tw, .float-slow, .float, .astro, .critter, .coin, .plus, .heart, .glow {{ transform-box: fill-box; transform-origin: center; }}
  .tw  {{ animation: twinkle 4s ease-in-out infinite; }}
  .tw1 {{ animation-delay: 0s; }} .tw2 {{ animation-delay: -1s; animation-duration: 5s; }}
  .tw3 {{ animation-delay: -2s; animation-duration: 3.2s; }} .tw4 {{ animation-delay: -3s; animation-duration: 6s; }}
  @keyframes twinkle {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: .2; }} }}

  .float-slow {{ animation: bob 12s ease-in-out infinite; }}
  .float      {{ animation: bob 7s ease-in-out infinite; }}
  @keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-14px); }} }}

  .astro {{ animation: drift 9s ease-in-out infinite; }}
  @keyframes drift {{
    0%,100% {{ transform: translate(0,0) rotate(-8deg); }}
    50%     {{ transform: translate(-10px,-22px) rotate(6deg); }}
  }}
  .ring {{ animation: ringspin 30s linear infinite; }}
  @keyframes ringspin {{ to {{ stroke-dashoffset: -400; }} }}

  .shoot {{ opacity: 0; animation: shoot 9s ease-in infinite; transform-box: view-box; transform-origin: 0 0; }}
  .shoot.s2 {{ animation-delay: 4.5s; }}
  @keyframes shoot {{
    0%   {{ opacity: 0; transform: translate(0,0); }}
    2%   {{ opacity: 1; }}
    10%  {{ opacity: 0; transform: translate(-520px, 300px); }}
    100% {{ opacity: 0; transform: translate(-520px, 300px); }}
  }}

  .constel line {{ stroke-dasharray: 200; stroke-dashoffset: 200; animation: draw 10s ease-in-out infinite; }}
  @keyframes draw {{ 0% {{ stroke-dashoffset: 200; }} 30%,80% {{ stroke-dashoffset: 0; }} 100% {{ stroke-dashoffset: -200; }} }}

  .type {{ animation: typing 12s steps(24) infinite; }}
  .t2 {{ animation-name: typing2; }} .t3 {{ animation-name: typing3; }}
  @keyframes typing  {{ 0% {{ width: 0; }} 15%,92% {{ width: 400px; }} 100% {{ width: 0; }} }}
  @keyframes typing2 {{ 0%,20% {{ width: 0; }} 30%,92% {{ width: 400px; }} 100% {{ width: 0; }} }}
  @keyframes typing3 {{ 0%,35% {{ width: 0; }} 52%,92% {{ width: 400px; }} 100% {{ width: 0; }} }}
  .cursor {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}

  .walkA {{ animation: frameA .6s steps(1) infinite; }}
  .walkB {{ animation: frameB .6s steps(1) infinite; }}
  @keyframes frameA {{ 50% {{ opacity: 0; }} }}
  @keyframes frameB {{ 0% {{ opacity: 0; }} 50% {{ opacity: 1; }} }}
  .critter {{ animation: hop 1.2s ease-in-out infinite; }}
  @keyframes hop {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-8px); }} }}

  .coin {{ animation: spin 1.6s linear infinite; }}
  .coin.c2 {{ animation-delay: -.5s; }} .coin.c3 {{ animation-delay: -1s; }}
  @keyframes spin {{ 0%,100% {{ transform: scaleX(1); }} 50% {{ transform: scaleX(.15); }} }}
  .plus {{ animation: plus 3s ease-out infinite; }}
  @keyframes plus {{ 0% {{ opacity: 0; transform: translateY(0); }} 20% {{ opacity: 1; }} 100% {{ opacity: 0; transform: translateY(-50px); }} }}

  .heart {{ animation: beat 1.8s ease-in-out infinite; }}
  .heart.h2 {{ animation-delay: -.6s; }} .heart.h3 {{ animation-delay: -1.2s; }}
  @keyframes beat {{ 0%,100% {{ transform: scale(1); }} 15% {{ transform: scale(1.25); }} 30% {{ transform: scale(1); }} }}

  .moon {{ animation: orbit 24s linear infinite; transform-origin: 330px 270px; transform-box: view-box; }}
  @keyframes orbit {{ to {{ transform: rotate(360deg); }} }}
  .glow {{ animation: glow 3s ease-in-out infinite; }}
  @keyframes glow {{ 0%,100% {{ opacity: .6; }} 50% {{ opacity: 1; }} }}

  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>

<rect width="1920" height="1080" fill="url(#sky)"/>
<ellipse cx="300" cy="300" rx="600" ry="380" fill="url(#neb3)"/>
<ellipse cx="1650" cy="780" rx="620" ry="420" fill="url(#neb1)"/>
<ellipse cx="1400" cy="160" rx="520" ry="300" fill="url(#neb2)"/>
<ellipse cx="420" cy="900" rx="500" ry="300" fill="url(#neb2)"/>

{stars(170, 1920, 1080, avoid=(560, 220, 1360, 640))}
{sparkle(1180, 140, 10, GOLD)}{sparkle(240, 620, 8, PINK, "tw tw3")}{sparkle(1760, 420, 9, BLUE, "tw tw4")}
{sparkle(860, 930, 7, LILAC, "tw tw1")}{sparkle(1480, 980, 8, GOLD, "tw tw3")}

<!-- shooting stars -->
<g class="shoot"><line x1="1500" y1="60" x2="1640" y2="60" stroke="url(#shoot)" stroke-width="2.5" stroke-linecap="round" transform="rotate(-30 1640 60)"/></g>
<g class="shoot s2"><line x1="1000" y1="40" x2="1110" y2="40" stroke="url(#shoot)" stroke-width="2" stroke-linecap="round" transform="rotate(-30 1110 40)"/></g>

<!-- ringed planet + orbiting moon -->
<g class="float-slow">
  <path d="M130 270 A200 44 0 0 1 530 270" fill="none" stroke="{PINK}" stroke-opacity=".45" stroke-width="10" transform="rotate(-18 330 270)"/>
  <circle cx="330" cy="270" r="110" fill="url(#planet)"/>
  <path d="M232 238 Q330 214 428 240" stroke="#ffffff" stroke-opacity=".25" stroke-width="8" fill="none"/>
  <path d="M226 290 Q330 312 432 286" stroke="#8f78bd" stroke-opacity=".5" stroke-width="10" fill="none"/>
  <circle cx="290" cy="300" r="12" fill="#a893d4" opacity=".6"/><circle cx="372" cy="232" r="8" fill="#a893d4" opacity=".5"/>
  <path d="M130 270 A200 44 0 0 0 530 270" fill="none" stroke="{PINK}" stroke-width="10" stroke-linecap="round" class="ring" stroke-dasharray="40 14" transform="rotate(-18 330 270)"/>
</g>
<g class="moon"><circle cx="330" cy="90" r="16" fill="{BLUE}"/><circle cx="325" cy="86" r="4" fill="#8fc9e8"/></g>

<!-- "&lt;/&gt;" constellation -->
<g class="constel" stroke="{LILAC}" stroke-opacity=".7" stroke-width="2" fill="{TEXT}">
  <line x1="1520" y1="160" x2="1470" y2="210"/><line x1="1470" y1="210" x2="1520" y2="260"/>
  <line x1="1600" y1="140" x2="1560" y2="280"/>
  <line x1="1640" y1="160" x2="1690" y2="210"/><line x1="1690" y1="210" x2="1640" y2="260"/>
  <circle class="tw tw1" cx="1520" cy="160" r="4"/><circle class="tw tw2" cx="1470" cy="210" r="5"/><circle class="tw tw3" cx="1520" cy="260" r="4"/>
  <circle class="tw tw4" cx="1600" cy="140" r="4"/><circle class="tw tw1" cx="1560" cy="280" r="4"/>
  <circle class="tw tw2" cx="1640" cy="160" r="4"/><circle class="tw tw3" cx="1690" cy="210" r="5"/><circle class="tw tw4" cx="1640" cy="260" r="4"/>
</g>

<!-- orbit system around the center (sits behind the search box) -->
<g transform="rotate(-8 960 560)" opacity=".9">
  <ellipse cx="960" cy="560" rx="380" ry="380" fill="url(#neb3)" class="glow"/>
  <path id="orb1" d="M400 560 a560 150 0 1 0 1120 0 a560 150 0 1 0 -1120 0" fill="none" stroke="{LILAC}" stroke-opacity=".16" stroke-width="1.5"/>
  <path id="orb2" d="M540 560 a420 112 0 1 1 840 0 a420 112 0 1 1 -840 0" fill="none" stroke="{BLUE}" stroke-opacity=".16" stroke-width="1.5" stroke-dasharray="4 10"/>
  <path id="orb3" d="M660 560 a300 80 0 1 0 600 0 a300 80 0 1 0 -600 0" fill="none" stroke="{PINK}" stroke-opacity=".18" stroke-width="1.5"/>
  <!-- pink planet -->
  <g><circle r="13" fill="{PINK}"/><circle r="13" fill="none" stroke="#fff" stroke-opacity=".3" stroke-width="3" stroke-dasharray="10 60"/>
    <animateMotion dur="70s" repeatCount="indefinite"><mpath href="#orb1"/></animateMotion></g>
  <!-- gold star on the same orbit, opposite side -->
  <g><path d="M0,-9 Q0,0 9,0 Q0,0 0,9 Q0,0 -9,0 Q0,0 0,-9Z" fill="{GOLD}"/>
    <animateMotion dur="70s" begin="-35s" repeatCount="indefinite"><mpath href="#orb1"/></animateMotion></g>
  <!-- ringed blue planet -->
  <g><ellipse rx="20" ry="5" fill="none" stroke="{LILAC}" stroke-width="2.5" transform="rotate(-20)"/><circle r="9" fill="{BLUE}"/>
    <animateMotion dur="45s" repeatCount="indefinite"><mpath href="#orb2"/></animateMotion></g>
  <!-- tiny game controller -->
  <g><path d="M-14,-6 L14,-6 Q19,-6 20,0 L21,6 Q21,10 17,10 Q14,10 12,6 L-12,6 Q-14,10 -17,10 Q-21,10 -21,6 L-20,0 Q-19,-6 -14,-6Z" fill="{LILAC}"/>
    <circle cx="11" cy="-1" r="2" fill="{PINK}"/><circle cx="15" cy="2" r="2" fill="{BLUE}"/><rect x="-14" y="-2" width="7" height="2" fill="#2a2140"/><rect x="-11.5" y="-4.5" width="2" height="7" fill="#2a2140"/>
    <animateMotion dur="45s" begin="-22s" repeatCount="indefinite"><mpath href="#orb2"/></animateMotion></g>
  <!-- rocket, nose follows the path -->
  <g><g transform="rotate(90)">
      <path d="M0,-16 Q8,-6 7,8 L-7,8 Q-8,-6 0,-16Z" fill="#f5eefc"/>
      <circle cy="-3" r="3" fill="{BLUE}"/>
      <path d="M-7,4 L-12,12 L-7,10Z M7,4 L12,12 L7,10Z" fill="{PINK}"/>
      <path d="M-4,9 Q0,22 4,9Z" fill="{GOLD}"><animate attributeName="opacity" values="1;.4;1" dur=".3s" repeatCount="indefinite"/></path>
    </g>
    <animateMotion dur="26s" repeatCount="indefinite" rotate="auto"><mpath href="#orb3"/></animateMotion></g>
</g>

<!-- laptop on a floating asteroid -->
<g class="float">
  <ellipse cx="400" cy="880" rx="230" ry="120" fill="url(#screenglow)" class="glow"/>
  <path d="M190 900 Q210 860 280 856 L520 852 Q600 860 610 900 Q590 960 500 980 L300 984 Q210 970 190 900Z" fill="#3a2f4a"/>
  <path d="M190 900 Q210 860 280 856 L520 852 Q600 860 610 900 Q520 890 400 892 Q280 892 190 900Z" fill="#4a3d5e"/>
  <circle cx="300" cy="930" r="14" fill="#2c2339"/><circle cx="470" cy="945" r="10" fill="#2c2339"/><circle cx="540" cy="915" r="7" fill="#2c2339"/>
  <!-- laptop -->
  <path d="M250 872 L550 872 L580 890 L220 890Z" fill="#cfc3e6"/>
  <rect x="268" y="690" width="264" height="182" rx="10" fill="#cfc3e6"/>
  <rect x="280" y="702" width="240" height="160" rx="5" fill="#120e18"/>
  <circle cx="294" cy="714" r="3.5" fill="#ff7aa8"/><circle cx="306" cy="714" r="3.5" fill="{GOLD}"/><circle cx="318" cy="714" r="3.5" fill="#9ee6b8"/>
  <g font-family="Consolas, 'Cascadia Code', monospace" font-size="15">
    <g transform="translate(292 748)"><text clip-path="url(#type1)" fill="{PINK}">&gt; <tspan fill="{TEXT}">npm run dream</tspan></text></g>
    <g transform="translate(292 776)"><text clip-path="url(#type2)" fill="#9ee6b8">✓ compiled 42 stars</text></g>
    <g transform="translate(292 804)"><text clip-path="url(#type3)" fill="{PINK}">&gt; <tspan fill="{TEXT}">git push origin moon</tspan></text></g>
    <rect class="cursor" x="292" y="818" width="9" height="16" fill="{BLUE}"/>
  </g>
  <g fill="{TEXT}" opacity=".7"><text x="545" y="760" font-family="Consolas, monospace" font-size="22" class="tw tw2">{{ }}</text></g>
</g>

<!-- astronaut gamer -->
<g class="astro">
  <!-- backpack -->
  <rect x="1548" y="600" width="44" height="96" rx="14" fill="#cfc3e6"/>
  <!-- body -->
  <rect x="1570" y="610" width="110" height="120" rx="40" fill="#f5eefc"/>
  <rect x="1600" y="650" width="50" height="30" rx="8" fill="{LILAC}"/>
  <circle cx="1612" cy="665" r="4" fill="{PINK}"/><circle cx="1626" cy="665" r="4" fill="{BLUE}"/><circle cx="1640" cy="665" r="4" fill="{GOLD}"/>
  <!-- legs -->
  <rect x="1582" y="712" width="36" height="66" rx="16" fill="#f5eefc" transform="rotate(12 1600 712)"/>
  <rect x="1636" y="712" width="36" height="66" rx="16" fill="#f5eefc" transform="rotate(-10 1654 712)"/>
  <!-- helmet -->
  <circle cx="1625" cy="560" r="70" fill="#f5eefc"/>
  <rect x="1572" y="526" width="106" height="68" rx="32" fill="#2a2140"/>
  <path d="M1588 545 Q1600 532 1622 534" stroke="{PINK}" stroke-width="7" stroke-linecap="round" fill="none" opacity=".8"/>
  <circle cx="1660" cy="575" r="5" fill="{BLUE}" opacity=".8"/>
  <rect x="1688" y="530" width="10" height="36" rx="5" fill="#cfc3e6"/>
  <!-- arms holding a controller -->
  <rect x="1548" y="650" width="34" height="74" rx="16" fill="#f5eefc" transform="rotate(-30 1565 650)"/>
  <rect x="1668" y="650" width="34" height="74" rx="16" fill="#f5eefc" transform="rotate(30 1685 650)"/>
  <g transform="translate(1570 708)">
    <path d="M10 0 L100 0 Q120 0 124 22 L128 44 Q130 58 116 58 Q106 58 98 44 L32 44 Q24 58 14 58 Q0 58 2 44 L6 22 Q10 0 10 0Z" fill="{PINK}"/>
    <rect x="22" y="14" width="6" height="18" rx="1" fill="#2a2140"/><rect x="16" y="20" width="18" height="6" rx="1" fill="#2a2140"/>
    <circle cx="92" cy="16" r="5" fill="{BLUE}"/><circle cx="102" cy="26" r="5" fill="{GOLD}"/><circle cx="82" cy="26" r="5" fill="#9ee6b8"/><circle cx="92" cy="36" r="5" fill="{LILAC}"/>
  </g>
  <!-- tether to nowhere -->
  <path d="M1548 680 Q1480 720 1500 800 Q1520 880 1460 920" stroke="{LILAC}" stroke-width="3" fill="none" stroke-dasharray="6 8" opacity=".6"/>
</g>

<!-- pixel hearts (lives) -->
<g transform="translate(1520 430)"><g class="heart"><g transform="scale(.9)">{pixel_grid(HEART, 5, PINK)}</g></g></g>
<g transform="translate(1560 430)"><g class="heart h2"><g transform="scale(.9)">{pixel_grid(HEART, 5, PINK)}</g></g></g>
<g transform="translate(1600 430)"><g class="heart h3"><g transform="scale(.9)">{pixel_grid(HEART, 5, "#5a4a6e")}</g></g></g>

<!-- pixel critter collecting coins -->
<g transform="translate(1180 900)">
  <g class="critter">
    <g class="walkA">{pixel_grid(CRITTER_A, 7, BLUE)}</g>
    <g class="walkB">{pixel_grid(CRITTER_B, 7, BLUE)}</g>
    <rect x="21" y="21" width="7" height="7" fill="{BG}"/><rect x="42" y="21" width="7" height="7" fill="{BG}"/>
  </g>
</g>
<g transform="translate(1300 880)"><g class="coin">{pixel_grid(COIN, 6, GOLD)}</g></g>
<g transform="translate(1360 860)"><g class="coin c2">{pixel_grid(COIN, 6, GOLD)}</g></g>
<g transform="translate(1420 880)"><g class="coin c3">{pixel_grid(COIN, 6, GOLD)}</g></g>
<text class="plus" x="1300" y="860" font-family="Consolas, monospace" font-size="20" font-weight="bold" fill="{GOLD}">+1</text>
</svg>
"""

tile = f"""<svg xmlns="http://www.w3.org/2000/svg" width="480" height="90" viewBox="0 0 480 90">
<style>
  .tw {{ animation: twinkle 4s ease-in-out infinite; }}
  .tw1 {{ animation-delay: 0s; }} .tw2 {{ animation-delay: -1.3s; animation-duration: 5s; }}
  .tw3 {{ animation-delay: -2.1s; animation-duration: 3.4s; }} .tw4 {{ animation-delay: -3s; animation-duration: 6s; }}
  @keyframes twinkle {{ 0%,100% {{ opacity: .9; }} 50% {{ opacity: .1; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
{stars(22, 480, 90, rmax=1.3)}
{sparkle(120, 22, 4, GOLD)}{sparkle(380, 60, 3.5, PINK, "tw tw3")}
</svg>
"""

(OUT / "space-scene.svg").write_text(scene, encoding="utf-8")
(OUT / "stars.svg").write_text(tile, encoding="utf-8")
print("wrote", OUT / "space-scene.svg", "and", OUT / "stars.svg")


# ---- rotating status line that sits under the new tab search box ----
MESSAGES = [
    "compiling dreams...",
    "press start to continue",
    "achievement unlocked: new tab",
    "while (alive) { explore(); }",
    'git commit -m "reached orbit"',
    "loading next level...",
    "it works on my machine",
]
T, TYPE = 3.6, 1.4                    # seconds per message, seconds spent typing
D = T * len(MESSAGES)
W, CW, FS = 760, 10.4, 19             # svg width, monospace char width, font size

def fmt(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")

lines = []
for i, msg in enumerate(MESSAGES):
    full = "> " + msg
    n = len(full)
    x0 = (W - n * CW) / 2
    steps = range(n + 1)
    kt = ";".join(fmt(k / n * TYPE / D) for k in steps)
    widths = ";".join(fmt(k * CW) for k in steps)
    xs = ";".join(fmt(x0 + k * CW + 2) for k in steps)
    esc = full.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    lines.append(f"""
<g opacity="{1 if i == 0 else 0}">
  <animate attributeName="opacity" begin="{fmt(i * T)}s" dur="{fmt(D)}s" repeatCount="indefinite"
           values="1;1;0;0" keyTimes="0;{fmt((T - .3) / D)};{fmt(T / D)};1"/>
  <clipPath id="m{i}"><rect x="{fmt(x0)}" y="0" width="0" height="40">
    <animate attributeName="width" begin="{fmt(i * T)}s" dur="{fmt(D)}s" repeatCount="indefinite" calcMode="discrete" values="{widths}" keyTimes="{kt}"/>
  </rect></clipPath>
  <text x="{fmt(x0)}" y="27" clip-path="url(#m{i})" xml:space="preserve"><tspan fill="{PINK}">&gt; </tspan>{esc[5:]}</text>
  <rect class="cur" x="{fmt(x0)}" y="11" width="9" height="19" fill="{BLUE}">
    <animate attributeName="x" begin="{fmt(i * T)}s" dur="{fmt(D)}s" repeatCount="indefinite" calcMode="discrete" values="{xs}" keyTimes="{kt}"/>
  </rect>
</g>""")

BAR_X, BAR_W = 300, 160
tag = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="78" viewBox="0 0 {W} 78">
<style>
  text {{ font-family: Consolas, "Cascadia Code", monospace; font-size: {FS}px; fill: {TEXT}; }}
  .hud {{ font-size: 12px; fill: #ad9fbd; letter-spacing: .12em; }}
  .cur {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  .lvl {{ animation: lvl {fmt(D)}s linear infinite; }}
  @keyframes lvl {{ 0%,96% {{ opacity: 0; }} 97%,100% {{ opacity: 1; }} }}
</style>
{"".join(lines)}
<g>
  <text class="hud" x="{BAR_X - 14}" y="62" text-anchor="end">LVL 99</text>
  <rect x="{BAR_X}" y="53" width="{BAR_W}" height="10" rx="5" fill="{LILAC}" fill-opacity=".18"/>
  <rect x="{BAR_X}" y="53" width="0" height="10" rx="5" fill="{GOLD}">
    <animate attributeName="width" values="0;{BAR_W};{BAR_W}" keyTimes="0;.96;1" dur="{fmt(D)}s" repeatCount="indefinite"/>
  </rect>
  <text class="hud" x="{BAR_X + BAR_W + 14}" y="62">XP</text>
  <text class="hud lvl" x="{BAR_X + BAR_W + 44}" y="62" style="fill:{GOLD}">LEVEL UP!</text>
</g>
</svg>
"""
(OUT / "tagline.svg").write_text(tag, encoding="utf-8")
print("wrote", OUT / "tagline.svg")


# ---- still versions, swapped in when animations are frozen (nocturne.freeze) ----
import re

def make_still(svg):
    """Same picture with every animation stopped: CSS animations off, SMIL frozen in place."""
    svg = svg.replace("</style>", "  * { animation: none !important; }\n</style>", 1)
    # typed terminal lines: show them fully typed
    svg = re.sub(r'<animate attributeName="width"[^>]*/>', "", svg)
    svg = svg.replace('width="0" height="30">', 'width="400" height="30">')
    svg = re.sub(r'<animate attributeName="opacity"[^>]*/>', "", svg)

    # orbiting things: freeze each one at the spot it would start from
    def freeze(m):
        attrs = m.group(1)
        dur = float(re.search(r'dur="([\d.]+)s"', attrs).group(1))
        b = re.search(r'begin="(-?[\d.]+)s"', attrs)
        f = ((-float(b.group(1)) if b else 0.0) / dur) % 1
        rot = ' rotate="auto"' if 'rotate="auto"' in attrs else ""
        return (f'<animateMotion dur="0.01s" fill="freeze" calcMode="linear" keyPoints="{f:.3f};{f:.3f}" '
                f'keyTimes="0;1"{rot}>{m.group(2)}</animateMotion>')
    return re.sub(r'<animateMotion([^>]*)>(<mpath[^>]*/>)</animateMotion>', freeze, svg)

tag_still = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="78" viewBox="0 0 {W} 78">
<style>
  text {{ font-family: Consolas, "Cascadia Code", monospace; font-size: {FS}px; fill: {TEXT}; }}
  .hud {{ font-size: 12px; fill: #ad9fbd; letter-spacing: .12em; }}
</style>
<text x="{W / 2}" y="27" text-anchor="middle" xml:space="preserve"><tspan fill="{BLUE}">||</tspan> paused, saving power</text>
<text class="hud" x="{BAR_X - 14}" y="62" text-anchor="end">LVL 99</text>
<rect x="{BAR_X}" y="53" width="{BAR_W}" height="10" rx="5" fill="{LILAC}" fill-opacity=".18"/>
<rect x="{BAR_X}" y="53" width="{BAR_W // 2}" height="10" rx="5" fill="{BLUE}"/>
<text class="hud" x="{BAR_X + BAR_W + 14}" y="62">XP</text>
</svg>
"""
(OUT / "space-scene-still.svg").write_text(make_still(scene), encoding="utf-8")
(OUT / "stars-still.svg").write_text(make_still(tile), encoding="utf-8")
(OUT / "tagline-still.svg").write_text(tag_still, encoding="utf-8")
print("wrote still versions")


# ---- centerpiece: wordmark + status line in one image, used when the search box is off ----
def inner(svg):
    return svg[svg.index(">", svg.index("<svg")) + 1: svg.rindex("</svg>")]

CEN_W, CEN_H = 820, 250

def centerpiece(tagsvg, animated):
    flow = (f'<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{CEN_W} 0" '
            f'dur="12s" repeatCount="indefinite"/>') if animated else ""
    # inline style so the status line's `text {}` rule can't restyle the wordmark
    wm = "font: 200 92px 'Segoe UI Variable Display', 'Segoe UI', sans-serif; letter-spacing: 16px;"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CEN_W}" height="{CEN_H}" viewBox="0 0 {CEN_W} {CEN_H}">
<defs>
  <linearGradient id="wm" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{CEN_W}" y2="0" spreadMethod="repeat">
    <stop offset="0" stop-color="{BLUE}"/><stop offset=".33" stop-color="{PINK}"/>
    <stop offset=".66" stop-color="{LILAC}"/><stop offset="1" stop-color="{BLUE}"/>{flow}
  </linearGradient>
  <filter id="wmglow" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>
<text x="{CEN_W / 2 + 8}" y="112" text-anchor="middle" style="{wm} fill: {PINK}; opacity: .35" filter="url(#wmglow)">nocturne</text>
<text x="{CEN_W / 2 + 8}" y="112" text-anchor="middle" style="{wm} fill: url(#wm)">nocturne</text>
<g transform="translate({(CEN_W - W) / 2} 160)">{inner(tagsvg)}</g>
</svg>
"""

(OUT / "center.svg").write_text(centerpiece(tag, True), encoding="utf-8")
(OUT / "center-still.svg").write_text(centerpiece(tag_still, False), encoding="utf-8")
print("wrote centerpiece")

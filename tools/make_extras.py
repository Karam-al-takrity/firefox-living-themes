"""Generates the small extra Nocturne assets:

  chrome/themes/nocturne/ASSETS/gameover.svg  - pixel GAME OVER screen for "can't connect" pages
  chrome/themes/nocturne/ASSETS/rocket.svg    - rocket + sparkle trail that flies while a page loads
  chrome/themes/nocturne/ASSETS/eq.svg        - bouncing equalizer bars for tabs playing sound
  chrome/themes/nocturne/ASSETS/cursor.svg    - pixel-art mouse pointer
  chrome/themes/nocturne/ASSETS/walker.svg    - the pixel critter, walking, for the bookmarks dock

Run: python tools/make_extras.py
"""
from make_scene import OUT, PINK, BLUE, LILAC, GOLD, TEXT, CRITTER_A, CRITTER_B, pixel_grid, stars

INK = "#2a2140"

# 5x7 pixel letters for the title
FONT = {
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    " ": ["....."] * 7,
}


def pixel_text(text, px, color):
    out = []
    for n, ch in enumerate(text):
        out.append(f'<g transform="translate({n * 6 * px} 0)">{pixel_grid(FONT[ch], px, color)}</g>')
    return "".join(out)


# ---- GAME OVER screen ----
GW, GH, PX = 640, 330, 8
title_w = len("GAME OVER") * 6 * PX - PX
tx = (GW - title_w) / 2
SAD = CRITTER_A[:6] + ["..#....#..", "..#....#.."]
countdown = "".join(
    f'<text x="{GW / 2 + 92}" y="292" opacity="0" style="fill:{GOLD}">{9 - i}'
    f'<animate attributeName="opacity" values="1;0;0" keyTimes="0;.1;1" calcMode="discrete" '
    f'begin="{i}s" dur="10s" repeatCount="indefinite"/></text>'
    for i in range(10))
gameover = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{GW}" height="{GH}" viewBox="0 0 {GW} {GH}" shape-rendering="crispEdges">
<defs>
  <linearGradient id="go" gradientUnits="userSpaceOnUse" x1="{tx}" y1="0" x2="{tx + title_w}" y2="0">
    <stop offset="0" stop-color="{PINK}"/><stop offset=".5" stop-color="{LILAC}"/><stop offset="1" stop-color="{BLUE}"/>
  </linearGradient>
</defs>
<style>
  text, circle, .tear {{ shape-rendering: auto; }}
  text {{ font-family: Consolas, "Cascadia Code", monospace; font-size: 20px; fill: {TEXT}; }}
  .tw {{ animation: tw 3s ease-in-out infinite; }} .tw2 {{ animation-delay: -1s; }} .tw3 {{ animation-delay: -2s; }} .tw4 {{ animation-delay: -1.5s; }}
  @keyframes tw {{ 50% {{ opacity: .2; }} }}
  .title {{ animation: shake 4s steps(1) infinite; }}
  @keyframes shake {{ 0%,92% {{ transform: none; }} 94% {{ transform: translate(3px,-2px); }} 96% {{ transform: translate(-3px,2px); }} }}
  .sad {{ animation: sway 2.4s ease-in-out infinite; transform-box: fill-box; transform-origin: bottom center; }}
  @keyframes sway {{ 50% {{ transform: rotate(-6deg); }} }}
  .tear {{ animation: tear 2.4s ease-in infinite; }}
  @keyframes tear {{ 0%,40% {{ opacity: 0; transform: translateY(0); }} 50% {{ opacity: 1; }} 100% {{ opacity: 0; transform: translateY(16px); }} }}
  .blink {{ animation: blink 1.2s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
{stars(26, GW, GH, avoid=(60, 10, 580, 320), rmax=1.6)}
<g class="title">
  <g transform="translate({tx + 5} 35)">{pixel_text("GAME OVER", PX, INK)}</g>
  <g transform="translate({tx} 30)" fill="url(#go)">{pixel_text("GAME OVER", PX, "url(#go)")}</g>
</g>
<g transform="translate({GW / 2 - 25} 140)">
  <g class="sad">
    {pixel_grid(SAD, 5, BLUE)}
    <path d="M12 12l6 6M18 12l-6 6M32 12l6 6M38 12l-6 6" stroke="{INK}" stroke-width="2.5" stroke-linecap="square"/>
  </g>
  <rect class="tear" x="40" y="22" width="4" height="6" rx="2" fill="{BLUE}"/>
</g>
<text x="{GW / 2}" y="250" text-anchor="middle" style="fill:#ad9fbd; font-size: 16px; letter-spacing: .12em">connection lost</text>
<text x="{GW / 2 - 20}" y="292" text-anchor="middle"><tspan style="fill:{PINK}">CONTINUE?</tspan> <tspan class="blink">press F5</tspan></text>
{countdown}
</svg>
"""

# ---- rocket with a sparkle trail (points right) ----
rocket = f"""<svg xmlns="http://www.w3.org/2000/svg" width="190" height="20" viewBox="0 0 190 20">
<defs><linearGradient id="t" x1="0" x2="1">
  <stop offset="0" stop-color="{BLUE}" stop-opacity="0"/><stop offset=".6" stop-color="{LILAC}" stop-opacity=".7"/><stop offset="1" stop-color="{PINK}"/>
</linearGradient></defs>
<style>
  .f {{ animation: f .25s steps(1) infinite; }} @keyframes f {{ 50% {{ opacity: .35; }} }}
  .s {{ animation: s 1s ease-in-out infinite; }} .s2 {{ animation-delay: -.5s; }}
  @keyframes s {{ 50% {{ opacity: .1; }} }}
</style>
<rect x="0" y="9" width="160" height="2" rx="1" fill="url(#t)"/>
<path class="s" d="M70 4l1 2 2 1-2 1-1 2-1-2-2-1 2-1z" fill="{GOLD}"/>
<path class="s s2" d="M115 12l1 2 2 1-2 1-1 2-1-2-2-1 2-1z" fill="{PINK}"/>
<g transform="translate(176 10) rotate(90)">
  <path d="M0,-12 Q6,-4 5,6 L-5,6 Q-6,-4 0,-12Z" fill="#f5eefc"/>
  <circle cy="-2" r="2.2" fill="{BLUE}"/>
  <path d="M-5,3 L-9,9 L-5,7Z M5,3 L9,9 L5,7Z" fill="{PINK}"/>
  <path class="f" d="M-3,7 Q0,16 3,7Z" fill="{GOLD}"/>
</g>
</svg>
"""

# ---- equalizer bars ----
eq = f"""<svg xmlns="http://www.w3.org/2000/svg" width="14" height="12" viewBox="0 0 14 12">
<style>
  rect {{ transform-box: fill-box; transform-origin: bottom; animation: b .9s ease-in-out infinite; }}
  .b2 {{ animation-duration: .7s; animation-delay: -.3s; }} .b3 {{ animation-duration: 1.1s; animation-delay: -.6s; }}
  @keyframes b {{ 0%,100% {{ transform: scaleY(.3); }} 50% {{ transform: scaleY(1); }} }}
  @media (prefers-reduced-motion: reduce) {{ rect {{ animation: none; }} }}
</style>
<rect x="0.5" y="0" width="3" height="12" rx="1.5" fill="{PINK}"/>
<rect class="b2" x="5.5" y="0" width="3" height="12" rx="1.5" fill="{BLUE}"/>
<rect class="b3" x="10.5" y="0" width="3" height="12" rx="1.5" fill="{LILAC}"/>
</svg>
"""

# ---- pixel pointer (o = fill, # = outline, + = highlight) ----
ARROW = [
    "#..........",
    "##.........",
    "#+#........",
    "#+o#.......",
    "#+oo#......",
    "#+ooo#.....",
    "#+oooo#....",
    "#+ooooo#...",
    "#+oooooo#..",
    "#+ooooooo#.",
    "#+ooo#####.",
    "#+o#o#.....",
    "#o#.#o#....",
    "##..#o#....",
    "#....#o#...",
    ".....#o#...",
    "......##...",
]
CP = 1.5
cells = []
for j, row in enumerate(ARROW):
    for i, ch in enumerate(row):
        color = {"#": INK, "o": PINK, "+": TEXT}.get(ch)
        if color:
            cells.append(f'<rect x="{i * CP}" y="{j * CP}" width="{CP}" height="{CP}" fill="{color}"/>')
cursor = (f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="26" viewBox="0 0 24 26" '
          f'shape-rendering="crispEdges">{"".join(cells)}</svg>\n')

# ---- the critter walking (frames + bob), for the dock ----
walker = f"""<svg xmlns="http://www.w3.org/2000/svg" width="25" height="22" viewBox="0 0 25 22" shape-rendering="crispEdges">
<style>
  .a {{ animation: a .4s steps(1) infinite; }} .b {{ animation: b .4s steps(1) infinite; }}
  @keyframes a {{ 50% {{ opacity: 0; }} }} @keyframes b {{ 0% {{ opacity: 0; }} 50% {{ opacity: 1; }} }}
  .bob {{ animation: bob .8s ease-in-out infinite; }} @keyframes bob {{ 50% {{ transform: translateY(-2px); }} }}
</style>
<g class="bob" transform="translate(0 2)">
  <g class="a">{pixel_grid(CRITTER_A, 2.5, BLUE)}</g>
  <g class="b">{pixel_grid(CRITTER_B, 2.5, BLUE)}</g>
  <rect x="7.5" y="7.5" width="2.5" height="2.5" fill="{INK}"/><rect x="15" y="7.5" width="2.5" height="2.5" fill="{INK}"/>
</g>
</svg>
"""

for name, svg in {"gameover": gameover, "rocket": rocket, "eq": eq, "cursor": cursor, "walker": walker}.items():
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
print("wrote extras")

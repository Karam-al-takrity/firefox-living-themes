"""Draws Meridian as an animated SVG, for the CSS-only edition (no JavaScript).

The full edition draws a live clock with clock.js. CSS can't read the time,
so this version keeps the instrument and its motion but not the real time:
rings turn, planets orbit, gears mesh, the balance swings, a second hand
ticks and the moon cycles through its phases.

  css-only/chrome/themes/meridian/assets/meridian.svg
  css-only/chrome/themes/meridian/assets/still/meridian.svg   (meridian.freeze)

Run: python tools/make_meridian_css.py   (build_css_only.py runs it for you)
"""
import math
import random
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "css-only" / "chrome" / "themes" / "meridian" / "assets"

W, H = 1920, 1080
S = min(W, H)
R = S * 0.43
CX, CY = W / 2, H / 2 - S * 0.012
TAU = math.tau
BRASS, BRIGHT, DIM, FAINT = "#c9a86a", "#f0d9a6", "rgba(201,168,106,.34)", "rgba(201,168,106,.16)"
RUBY = "#c8324a"
SERIF = "'Palatino Linotype', 'Book Antiqua', Georgia, serif"
LINE = S * 0.0012
MONTHS = ["JANUARIVS", "FEBRVARIVS", "MARTIVS", "APRILIS", "MAIVS", "IVNIVS", "IVLIVS", "AVGVSTVS", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
DAYS = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
ROMAN = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
f = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")


def pt(r, a):
    """Point at radius r and angle a (0 = right, clockwise, like canvas) around the centre."""
    return CX + math.cos(a) * r, CY + math.sin(a) * r


def circle(r, color, width, x=None, y=None):
    return f'<circle cx="{f(CX if x is None else x)}" cy="{f(CY if y is None else y)}" r="{f(r)}" fill="none" stroke="{color}" stroke-width="{f(width)}"/>'


def ticks(n, r1, r2, color, width, every=0, r3=0):
    d = []
    for i in range(n):
        a = i / n * TAU
        inner = r3 if every and i % every == 0 else r2
        x1, y1 = pt(r1, a)
        x2, y2 = pt(inner, a)
        d.append(f"M{f(x1)} {f(y1)}L{f(x2)} {f(y2)}")
    return f'<path d="{"".join(d)}" stroke="{color}" stroke-width="{f(width)}" fill="none"/>'


def ring_text(text, r, angle, size, color, spacing):
    """Letters set round a circle, centred on angle (0 = top), each turned to face out."""
    start = angle - ((len(text) - 1) * spacing) / (2 * r)
    out = []
    for i, ch in enumerate(text):
        a = start + i * spacing / r
        deg = math.degrees(a)
        out.append(f'<text x="{f(CX)}" y="{f(CY - r)}" transform="rotate({f(deg)} {f(CX)} {f(CY)})">{ch}</text>')
    return (f'<g style="font: {f(size)}px {SERIF}; fill: {color}" text-anchor="middle" dominant-baseline="middle">'
            + "".join(out) + "</g>")


# ---------------------------------------------------------------- background
rnd = random.Random(7)
stars = "".join(
    f'<circle cx="{f(rnd.random() * W)}" cy="{f(rnd.random() * H)}" r="{f(rnd.random() * 1.3 + .4)}" fill="#e8dec4" opacity="{f(.1 + rnd.random() * .5)}"/>'
    for _ in range(260))

# ---------------------------------------------------------------- calendar ring
cal = [circle(R, BRASS, LINE * 1.8), circle(R * .985, DIM, LINE * .7), circle(R * .875, BRASS, LINE)]
start = 0.0
for m in range(12):
    span = DAYS[m] / 365.25 * TAU
    a = start - math.pi / 2
    x1, y1 = pt(R * .875, a)
    x2, y2 = pt(R * .985, a)
    cal.append(f'<path d="M{f(x1)} {f(y1)}L{f(x2)} {f(y2)}" stroke="{BRASS}" stroke-width="{f(LINE)}"/>')
    short, long_ = [], []
    for d in range(1, int(DAYS[m]) + 1):
        if d >= DAYS[m]:
            break
        da = a + d / 365.25 * TAU
        is_long = d % 5 == 0
        p1 = pt(R * .985, da)
        p2 = pt(R * (.955 if is_long else .97), da)
        (long_ if is_long else short).append(f"M{f(p1[0])} {f(p1[1])}L{f(p2[0])} {f(p2[1])}")
    cal.append(f'<path d="{"".join(short)}" stroke="{DIM}" stroke-width="{f(LINE * .7)}"/>')
    cal.append(f'<path d="{"".join(long_)}" stroke="{BRASS}" stroke-width="{f(LINE)}"/>')
    cal.append(ring_text(MONTHS[m], R * .915, start + span / 2, R * .036, BRIGHT, R * .036))
    start += span

# ---------------------------------------------------------------- hour ring
hours = [circle(R * .86, BRASS, LINE), circle(R * .725, BRASS, LINE * 1.3), circle(R * .715, DIM, LINE * .7),
         ticks(60, R * .86, R * .84, BRASS, LINE * .8, 5, R * .825)]
for h in range(12):
    hours.append(ring_text(ROMAN[h], R * .778, h / 12 * TAU, R * .062, BRIGHT, R * .05))

# ---------------------------------------------------------------- rete
r = R * .7
rete = [f'<circle cx="{f(CX)}" cy="{f(CY - r * .2)}" r="{f(r * .76)}" fill="none" stroke="{BRASS}" stroke-width="{f(LINE)}"/>',
        circle(r * .99, DIM, LINE * .8)]
curl = (f"M0 {f(-r * .5)}C{f(r * .2)} {f(-r * .62)} {f(r * .05)} {f(-r * .82)} {f(r * .22)} {f(-r * .94)}"
        f"M0 {f(-r * .5)}C{f(-r * .2)} {f(-r * .62)} {f(-r * .05)} {f(-r * .82)} {f(-r * .22)} {f(-r * .94)}")
flame = (f"M{f(r * .22)} {f(-r * .94)}Q{f(r * .27)} {f(-r * .9)} {f(r * .3)} {f(-r * .965)}"
         f"Q{f(r * .24)} {f(-r * .96)} {f(r * .22)} {f(-r * .94)}Z")
for i in range(8):
    rete.append(f'<g transform="translate({f(CX)} {f(CY)}) rotate({i * 45})">'
                f'<path d="{curl}" fill="none" stroke="{DIM}" stroke-width="{f(LINE * .8)}"/>'
                f'<path d="{flame}" fill="{BRASS}"/></g>')
seed = 41


def lcg():
    global seed
    seed = (seed * 16807) % 2147483647
    return seed / 2147483647


for c in range(11):
    a0, d0 = lcg() * TAU, r * (.5 + lcg() * .42)
    x, y = math.cos(a0) * d0, math.sin(a0) * d0
    pts = [(x, y)]
    for i in range(3 + int(lcg() * 3)):
        x += (lcg() - .5) * r * .2
        y += (lcg() - .5) * r * .2
        pts.append((x, y))
    rete.append('<path d="' + "".join(("L" if i else "M") + f"{f(CX + px)} {f(CY + py)}" for i, (px, py) in enumerate(pts))
                + f'" fill="none" stroke="rgba(143,180,201,.45)" stroke-width="{f(LINE * .7)}"/>')
    for px, py in pts:
        rete.append(f'<circle cx="{f(CX + px)}" cy="{f(CY + py)}" r="{f(LINE * (1 + lcg() * 1.1))}" fill="#dfeaf2"/>')

# ---------------------------------------------------------------- orbits and planets (seconds per orbit: slow on purpose)
ORBITS = [(.14, "#b9b4a6", 1.1, 30), (.2, "#f1d9a0", 1.6, 52), (.26, "#6fb7e0", 1.8, 80),
          (.32, "#d2694a", 1.3, 130), (.38, "#e3c28f", 2.5, 300), (.43, "#e6d6a0", 2.1, 520)]
orbits = [circle(o[0] * R, FAINT, LINE * .8) for o in ORBITS] + [circle(R * .46, BRASS, LINE)]
planets = []
prnd = random.Random(5)
for i, (rr, col, d, period) in enumerate(ORBITS):
    size = d * S * .0024
    x, y = CX + rr * R, CY
    ring = (f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(size * 2)}" ry="{f(size * .7)}" fill="none" stroke="{col}" stroke-width="{f(S * .0009)}" transform="rotate(-23 {f(x)} {f(y)})"/>'
            if i == 5 else "")
    planets.append(f'<g class="orbit" style="animation-duration: {period}s; animation-delay: -{f(prnd.random() * period)}s">'
                   f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(size)}" fill="{col}"/>{ring}</g>')

# ---------------------------------------------------------------- gears
U = R * .2


def gear(teeth, rp):
    tooth = rp * .1 + 1.5
    d = []
    for i in range(teeth):
        a, w = i / teeth * TAU, TAU / teeth
        for j, (rad, fr) in enumerate([(rp - tooth, -.25), (rp + tooth, -.14), (rp + tooth, .14), (rp - tooth, .25)]):
            x, y = math.cos(a + fr * w) * rad, math.sin(a + fr * w) * rad
            d.append(("M" if i == 0 and j == 0 else "L") + f"{f(x)} {f(y)}")
    spokes = "".join(f"M{f(math.cos(k / 5 * TAU) * rp * .2)} {f(math.sin(k / 5 * TAU) * rp * .2)}"
                     f"L{f(math.cos(k / 5 * TAU) * rp * .72)} {f(math.sin(k / 5 * TAU) * rp * .72)}" for k in range(5))
    return (f'<path d="{"".join(d)}Z" fill="rgba(201,168,106,.07)" stroke="{BRASS}" stroke-width="{f(max(1, S * .0011))}"/>'
            f'<circle r="{f(rp * .72)}" fill="none" stroke="{DIM}"/><circle r="{f(rp * .2)}" fill="none" stroke="{BRASS}"/>'
            f'<path d="{spokes}" stroke="{DIM}" stroke-width="{f(max(1.2, rp * .05))}"/>'
            f'<circle r="{f(max(1.5, rp * .07))}" fill="{RUBY}"/>')


def beside(g, unit, angle):
    return g[0] + math.cos(angle) * (g[2] + unit) * .2, g[1] + math.sin(angle) * (g[2] + unit) * .2


gears_spec = []
a1 = (-1.52, .5, 1);       gears_spec.append((a1, 36, 1, 1, 0))
a2 = (*beside(a1, .5, -.95), .5);  gears_spec.append((a2, 18, .5, -2, .09))
a3 = (*beside(a1, .667, 3.4), .667); gears_spec.append((a3, 24, .667, -1.5, .13))
b1 = (1.48, .56, .833);    gears_spec.append((b1, 30, .833, 1.2, 0))
b2 = (*beside(b1, .417, -2.2), .417); gears_spec.append((b2, 15, .417, -2.4, .2))
BASE = 12.566   # seconds per turn of the 1:1 gear
gears = []
for (gx, gy, _), teeth, unit, ratio, phase in gears_spec:
    x, y = CX + gx * R, CY + gy * R
    dur = BASE / abs(ratio)
    gears.append(f'<g transform="translate({f(x)} {f(y)}) rotate({f(math.degrees(phase))})"><g class="gear{" rev" if ratio < 0 else ""}" style="animation-duration: {f(dur)}s">'
                 f'{gear(teeth, U * unit)}</g></g>')

bx, by = CX - R * 1.5, CY - R * .4
spring = "".join(("M" if k == 0 else "L") + f"{f(bx + math.cos(k * .1) * (U * .06 + k * .1 / (TAU * 4) * U * .42))} {f(by + math.sin(k * .1) * (U * .06 + k * .1 / (TAU * 4) * U * .42))}"
                 for k in range(int(TAU * 4 / .1)))
balance = (f'<path d="{spring}" fill="none" stroke="{DIM}" stroke-width="{f(LINE * .8)}"/>'
           f'<g class="balance" style="transform-origin: {f(bx)}px {f(by)}px">'
           f'{circle(U * .62, BRASS, LINE * 1.8, bx, by)}{circle(U * .54, DIM, LINE * .7, bx, by)}'
           f'<path d="M{f(bx - U * .62)} {f(by)}H{f(bx + U * .62)}M{f(bx)} {f(by - U * .62)}V{f(by + U * .62)}" stroke="{BRASS}" stroke-width="{f(LINE)}"/>'
           + "".join(f'<circle cx="{f(bx + math.cos(k * TAU / 4) * U * .62)}" cy="{f(by + math.sin(k * TAU / 4) * U * .62)}" r="{f(LINE * 2)}" fill="{BRASS}"/>' for k in range(4))
           + f'<circle cx="{f(bx)}" cy="{f(by)}" r="{f(LINE * 2.4)}" fill="{RUBY}"/></g>')

# ---------------------------------------------------------------- moon dial (phases cycle: a shadow sweeps across the disc)
mx, my, mr = CX + R * 1.48, CY - R * .36, R * .2
m = mr * .68
moon_ticks = "".join(
    f"M{f(mx + math.cos(i / 30 * TAU) * mr * .92)} {f(my + math.sin(i / 30 * TAU) * mr * .92)}"
    f"L{f(mx + math.cos(i / 30 * TAU) * mr * .86)} {f(my + math.sin(i / 30 * TAU) * mr * .86)}" for i in range(30))
moon = (f'{circle(mr, BRASS, LINE, mx, my)}{circle(mr * .92, DIM, LINE, mx, my)}'
        f'<path d="{moon_ticks}" stroke="{BRASS}" stroke-width="{f(LINE)}"/>'
        f'<clipPath id="moonclip"><circle cx="{f(mx)}" cy="{f(my)}" r="{f(m)}"/></clipPath>'
        f'<g clip-path="url(#moonclip)"><circle cx="{f(mx)}" cy="{f(my)}" r="{f(m)}" fill="#e9dcb8"/>'
        f'<circle class="shade" cx="{f(mx)}" cy="{f(my)}" r="{f(m * 1.04)}" fill="#0a0f1c"/></g>'
        f'{circle(m, BRASS, LINE, mx, my)}'
        f'<text x="{f(mx)}" y="{f(my + mr * 1.26)}" text-anchor="middle" style="font: {f(mr * .17)}px {SERIF}; fill: {BRASS}">LVNA</text>')

# ---------------------------------------------------------------- the second hand, and the centre
second = (f'<g class="second"><path d="M{f(CX)} {f(CY + R * .12)}V{f(CY - R * .82)}" stroke="{RUBY}" stroke-width="{f(max(1, S * .0012))}"/>'
          f'<circle cx="{f(CX)}" cy="{f(CY - R * .62)}" r="{f(R * .02)}" fill="none" stroke="{RUBY}" stroke-width="{f(LINE)}"/></g>')
centre = f'<circle cx="{f(CX)}" cy="{f(CY)}" r="{f(R * .02)}" fill="{BRIGHT}"/><circle cx="{f(CX)}" cy="{f(CY)}" r="{f(R * .009)}" fill="{RUBY}"/>'
pointer = (f'<path d="M{f(CX)} {f(CY - R * .985)}L{f(CX - R * .018)} {f(CY - R * 1.035)}L{f(CX + R * .018)} {f(CY - R * 1.035)}Z" fill="{RUBY}"/>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">
<defs>
  <radialGradient id="bg" cx="{f(CX / W)}" cy="{f(CY / H)}" r=".75"><stop offset="0" stop-color="#111a2e"/><stop offset=".55" stop-color="#090d18"/><stop offset="1" stop-color="#04060b"/></radialGradient>
  <radialGradient id="sun"><stop offset="0" stop-color="#fff0c4"/><stop offset=".3" stop-color="rgba(240,190,90,.65)"/><stop offset="1" stop-color="rgba(240,190,90,0)"/></radialGradient>
</defs>
<style>
  .turn, .orbit, .second {{ transform-box: view-box; transform-origin: {f(CX)}px {f(CY)}px; }}
  .calendar {{ animation: spin 1800s linear infinite reverse; }}
  .rete {{ animation: spin 360s linear infinite; }}
  .orbit {{ animation: spin linear infinite reverse; }}
  .gear {{ animation: spin linear infinite; transform-box: view-box; transform-origin: 0 0; }}
  .gear.rev {{ animation-direction: reverse; }}
  .second {{ animation: spin 60s steps(60) infinite; }}
  .balance {{ transform-box: view-box; animation: swing 1s ease-in-out infinite alternate; }}
  .shade {{ animation: phase 40s linear infinite; }}
  .draw {{ transform-box: view-box; transform-origin: {f(CX)}px {f(CY)}px; animation: draw 2.2s cubic-bezier(.2,.8,.2,1) both; }}
  .d2 {{ animation-delay: .25s; }} .d3 {{ animation-delay: .5s; }} .d4 {{ animation-delay: .8s; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  @keyframes swing {{ from {{ transform: rotate(-80deg); }} to {{ transform: rotate(80deg); }} }}
  @keyframes phase {{ from {{ transform: translateX({f(-m * 2.1)}px); }} to {{ transform: translateX({f(m * 2.1)}px); }} }}
  @keyframes draw {{ from {{ opacity: 0; transform: rotate(-25deg) scale(.96); }} to {{ opacity: 1; transform: none; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
{stars}
<g class="draw"><g class="turn calendar">{"".join(cal)}</g>{pointer}</g>
<g class="draw d2">{"".join(hours)}</g>
<g class="draw d3"><g class="turn rete">{"".join(rete)}</g></g>
<g class="draw d4">{"".join(orbits)}{"".join(planets)}<circle cx="{f(CX)}" cy="{f(CY)}" r="{f(R * .09)}" fill="url(#sun)"/></g>
<g class="draw d3">{"".join(gears)}{balance}{moon}</g>
<g class="draw d4">{second}{centre}</g>
</svg>
"""

(OUT / "still").mkdir(parents=True, exist_ok=True)
(OUT / "meridian.svg").write_text(svg, encoding="utf-8")
still = svg.replace("</style>", "  * { animation: none !important; }\n</style>", 1)
(OUT / "still" / "meridian.svg").write_text(still, encoding="utf-8")
print("wrote", OUT / "meridian.svg")

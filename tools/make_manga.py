"""Generates the extra pieces added to the ame and relics themes.

  chrome/themes/ame/assets/cat-walk.svg        black cat that strolls across the bookmarks bar
  chrome/themes/ame/assets/nosignal.svg        neon NO SIGNAL page for can't-connect pages
  chrome/themes/relics/assets/deadline.svg     "the line went dead" page for can't-connect pages
  chrome/themes/relics/assets/crow-fly.svg     small crow that flies across the bookmarks bar

Run: python tools/make_manga.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "chrome" / "themes"


def still(svg):
    """Same drawing with every CSS and SMIL animation stopped."""
    svg = svg.replace("</style>", "  * { animation: none !important; }\n</style>", 1)
    return re.sub(r"<animate[^>]*/>", "", svg)


# ---------------------------------------------------------------- ame: cat walking
AME = ROOT / "ame" / "assets"
cat_walk = """<svg xmlns="http://www.w3.org/2000/svg" width="46" height="30" viewBox="0 0 46 30">
<style>
  .l1 { animation: legA .5s ease-in-out infinite alternate; transform-box: fill-box; transform-origin: top; }
  .l2 { animation: legA .5s ease-in-out infinite alternate-reverse; transform-box: fill-box; transform-origin: top; }
  @keyframes legA { from { transform: rotate(-22deg); } to { transform: rotate(22deg); } }
  .tail { animation: tail 1.6s ease-in-out infinite; transform-box: fill-box; transform-origin: right bottom; }
  @keyframes tail { 50% { transform: rotate(-16deg); } }
  .body { animation: step .5s ease-in-out infinite alternate; }
  @keyframes step { to { transform: translateY(-1px); } }
  @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
</style>
<g class="body" fill="#05070c" stroke="#3de0ff" stroke-width=".8" stroke-opacity=".7">
  <path class="tail" d="M8 15 Q1 12 3 3" fill="none" stroke="#05070c" stroke-width="3.2" stroke-linecap="round"/>
  <path class="tail" d="M8 15 Q1 12 3 3" fill="none" stroke-width=".8"/>
  <rect class="l1" x="11" y="18" width="3" height="10" rx="1.5"/>
  <rect class="l2" x="15" y="18" width="3" height="10" rx="1.5"/>
  <rect class="l2" x="28" y="18" width="3" height="10" rx="1.5"/>
  <rect class="l1" x="32" y="18" width="3" height="10" rx="1.5"/>
  <ellipse cx="22" cy="16" rx="15" ry="6.5"/>
  <circle cx="38" cy="11" r="6.5"/>
  <path d="M33.5 7 L34.5 1.5 L37.5 5.5Z M39 5.5 L42 1.5 L43.2 7Z"/>
  <circle cx="40.6" cy="10.4" r="1.3" fill="#ffb35c" stroke="none"/>
</g>
</svg>
"""
nosignal = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
<defs>
  <filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <pattern id="rain" width="40" height="80" patternUnits="userSpaceOnUse"><path d="M8 0 l-3 18 M28 34 l-3 18 M18 60 l-2 12" stroke="#8fb8ff" stroke-opacity=".35" stroke-width="1.2" stroke-linecap="round"/></pattern>
</defs>
<style>
  .rain { animation: rain .7s linear infinite; }
  @keyframes rain { to { transform: translate(-12px, 80px); } }
  .flick { animation: flick 4.5s steps(1) infinite; }
  @keyframes flick { 0%,40%,44%,46%,100% { opacity: 1; } 42%,45% { opacity: .15; } }
  .bars rect { animation: bar 1.8s steps(1) infinite; }
  .bars rect:nth-child(2) { animation-delay: .3s; } .bars rect:nth-child(3) { animation-delay: .6s; } .bars rect:nth-child(4) { animation-delay: .9s; }
  @keyframes bar { 0%,49% { opacity: .15; } 50%,70% { opacity: 1; } 71%,100% { opacity: .15; } }
  .blink { animation: blink 1.2s steps(1) infinite; }
  @keyframes blink { 50% { opacity: 0; } }
  @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
</style>
<rect x="-20" y="-80" width="700" height="460" fill="url(#rain)" class="rain"/>
<g class="flick" filter="url(#glow)">
  <rect x="120" y="60" width="400" height="120" rx="22" fill="none" stroke="#ff4f9a" stroke-width="5"/>
  <text x="320" y="140" text-anchor="middle" style="font: 300 58px 'Segoe UI Variable Display','Segoe UI',sans-serif; letter-spacing: 10px; fill: none; stroke: #ff4f9a; stroke-width: 2.4">NO SIGNAL</text>
</g>
<g class="bars" transform="translate(296 214)" filter="url(#glow)" fill="#3de0ff">
  <rect x="0" y="24" width="8" height="10" rx="2"/><rect x="12" y="16" width="8" height="18" rx="2"/>
  <rect x="24" y="8" width="8" height="26" rx="2"/><rect x="36" y="0" width="8" height="34" rx="2"/>
</g>
<text x="320" y="292" text-anchor="middle" style="font: 17px 'Segoe UI',sans-serif; letter-spacing: 3px; fill: #8b97b3">the rain took the connection</text>
<text x="320" y="326" text-anchor="middle" style="font: 15px Consolas, monospace; fill: #ffb35c">press F5 to try again<tspan class="blink">_</tspan></text>
</svg>
"""
(AME / "cat-walk.svg").write_text(cat_walk, encoding="utf-8")
(AME / "still" / "cat-walk.svg").write_text(still(cat_walk), encoding="utf-8")
(AME / "nosignal.svg").write_text(nosignal, encoding="utf-8")
(AME / "still" / "nosignal.svg").write_text(still(nosignal), encoding="utf-8")

# ---------------------------------------------------------------- relics: the line went dead
REL = ROOT / "relics" / "assets"
deadline = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="380" viewBox="0 0 640 380">
<defs>
  <radialGradient id="wall" cx=".5" cy=".45" r=".6"><stop offset="0" stop-color="#241c1f"/><stop offset="1" stop-color="#110d0f" stop-opacity="0"/></radialGradient>
</defs>
<style>
  .smoke { animation: smoke 4s ease-out infinite; transform-box: fill-box; transform-origin: bottom center; }
  .smoke.s2 { animation-delay: -1.4s; } .smoke.s3 { animation-delay: -2.7s; }
  @keyframes smoke { 0% { opacity: 0; transform: translateY(0) scale(.6); } 20% { opacity: .55; } 100% { opacity: 0; transform: translateY(-60px) scale(1.4) skewX(12deg); } }
  .ember { animation: ember 3s ease-in-out infinite; }
  @keyframes ember { 0%,100% { opacity: .2; } 50% { opacity: .7; } }
  .drip { animation: drip 3.2s ease-in infinite; transform-box: fill-box; transform-origin: top; }
  .drip.d2 { animation-delay: -1.1s; } .drip.d3 { animation-delay: -2.2s; }
  @keyframes drip { 0% { transform: scaleY(.2); } 70% { transform: scaleY(1); } 100% { transform: scaleY(1); opacity: .2; } }
  .smile { animation: grin 6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
  @keyframes grin { 0%,80%,100% { transform: scale(1); } 86% { transform: scale(1.04); } }
  @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
</style>
<rect width="640" height="380" fill="url(#wall)"/>
<!-- the smiley, painted on the wall -->
<g transform="translate(410 150)"><g class="smile" fill="none" stroke="#c1121f" stroke-width="9" stroke-linecap="round">
  <circle r="86"/>
  <path d="M-30 -22 v14 M30 -22 v14" stroke-width="12"/>
  <path d="M-46 22 Q0 70 46 22"/>
  <path class="drip" d="M-62 64 v34" stroke-width="5"/><path class="drip d2" d="M18 84 v28" stroke-width="5"/><path class="drip d3" d="M64 58 v40" stroke-width="5"/>
</g></g>
<!-- the lantern, gone out -->
<g transform="translate(170 150)">
  <path d="M0 -92 v18" stroke="#3a2d31" stroke-width="3"/>
  <rect x="-22" y="-76" width="44" height="10" rx="3" fill="#2a2124"/>
  <ellipse cx="0" cy="0" rx="48" ry="66" fill="#2a2124" stroke="#3a2d31" stroke-width="3"/>
  <path d="M-46 -20 Q0 -14 46 -20 M-48 4 Q0 10 48 4 M-44 28 Q0 34 44 28" stroke="#3a2d31" stroke-width="2.5" fill="none"/>
  <rect x="-22" y="64" width="44" height="10" rx="3" fill="#2a2124"/>
  <circle class="ember" cx="0" cy="10" r="4" fill="#ff8a4a"/>
  <g fill="none" stroke="#a3958c" stroke-width="3" stroke-linecap="round">
    <path class="smoke" d="M0 -80 q-10 -14 0 -28 q10 -14 0 -28"/>
    <path class="smoke s2" d="M-4 -80 q-12 -12 -2 -26 q10 -14 -4 -26"/>
    <path class="smoke s3" d="M4 -80 q8 -14 0 -26 q-8 -12 4 -28"/>
  </g>
</g>
<text x="320" y="300" text-anchor="middle" style="font: italic 300 26px 'Segoe UI Variable Display','Segoe UI',serif; letter-spacing: 3px; fill: #efe6d2">the line went dead</text>
<text x="320" y="336" text-anchor="middle" style="font: 14px 'Segoe UI',sans-serif; letter-spacing: 4px; fill: #a3958c">PRESS F5 TO LIGHT THE LANTERN AGAIN</text>
</svg>
"""
(REL / "deadline.svg").write_text(deadline, encoding="utf-8")
(REL / "still" / "deadline.svg").write_text(still(deadline), encoding="utf-8")
crow_fly = """<svg xmlns="http://www.w3.org/2000/svg" width="40" height="28" viewBox="0 0 40 28">
<style>
  .up { animation: up .36s steps(1) infinite; } .down { animation: down .36s steps(1) infinite; }
  @keyframes up { 50% { opacity: 0; } } @keyframes down { 0% { opacity: 0; } 50% { opacity: 1; } }
  .bob { animation: bob .72s ease-in-out infinite; } @keyframes bob { 50% { transform: translateY(2px); } }
  @media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
</style>
<g class="bob" fill="#07060a" stroke="#d99a8a" stroke-opacity=".45" stroke-width=".7">
  <path class="up" d="M14 14 Q16 2 6 0 Q18 4 21 13Z M22 13 Q26 3 34 1 Q28 8 25 14Z"/>
  <path class="down" d="M14 15 Q10 25 3 27 Q14 24 20 16Z M22 16 Q28 24 35 26 Q28 20 25 15Z"/>
  <path d="M8 16 Q14 11 24 13 Q31 14 34 16 L39 15.5 L34 18 Q27 21 18 19 Q11 20 8 16Z"/>
  <path d="M8 16 L1 13 L3 17 L1 20Z"/>
  <circle cx="31.5" cy="15.3" r=".9" fill="#c1121f" stroke="none"/>
</g>
</svg>
"""
(REL / "crow-fly.svg").write_text(crow_fly, encoding="utf-8")
(REL / "still" / "crow-fly.svg").write_text(still(crow_fly), encoding="utf-8")
print("wrote ame and relics art")

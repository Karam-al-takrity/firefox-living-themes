"""Builds the CSS-only edition in css-only/chrome/ from the main themes in chrome/.

The CSS-only edition contains no JavaScript, needs no theme loader and touches
nothing in the Firefox install folder. Differences from the full edition:
  - no switcher button: themes are switched with prefs in about:config
  - no music
  - Meridian's new tab is an animated SVG (tools/make_meridian_css.py) instead
    of the live clock: no real time or date, everything else moves

Don't edit css-only/ by hand: change chrome/ or this script, then run
    python tools/build_css_only.py
It finishes by checking that every file the stylesheets point to exists.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "chrome"
DST = ROOT / "css-only" / "chrome"

# files only the theme loader uses
SKIP_DIRS = {"switcher"}
SKIP_FILES = {".js", ".json", ".cfg"}
SKIP_NAMES = {"music.svg", "music-off.svg", "music-playing.svg"}

if DST.exists():
    shutil.rmtree(DST)
for path in SRC.rglob("*"):
    rel = path.relative_to(SRC)
    if rel.parts and rel.parts[0] == "themes" and len(rel.parts) > 1 and rel.parts[1] in SKIP_DIRS:
        continue
    if path.is_dir() or path.suffix in SKIP_FILES or path.name in SKIP_NAMES:
        continue
    out = DST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, out)

(DST / "userChrome.css").write_text("""/* CSS-only edition: no JavaScript, nothing installed outside your profile.
   Each theme loads only while its pref is true (about:config, live, no restart):
     relics.active   = true  -> relics
     ame.active      = true  -> ame
     manga.active    = true  -> manga
     meridian.active = true  -> meridian
     all of them false       -> nocturne (the default)
   Keep at most one of them true. */
@import url("themes/relics/userChrome.css") -moz-pref("relics.active");
@import url("themes/ame/userChrome.css") -moz-pref("ame.active");
@import url("themes/manga/userChrome.css") -moz-pref("manga.active");
@import url("themes/meridian/userChrome.css") -moz-pref("meridian.active");
@import url("themes/nocturne/gate-chrome.css") not -moz-pref("relics.active");
""", encoding="utf-8")
(DST / "userContent.css").write_text("""/* CSS-only edition: each theme's page styles load only while its pref is true
   (see userChrome.css). */
@import url("themes/relics/userContent.css") -moz-pref("relics.active");
@import url("themes/ame/userContent.css") -moz-pref("ame.active");
@import url("themes/manga/userContent.css") -moz-pref("manga.active");
@import url("themes/meridian/userContent.css") -moz-pref("meridian.active");
@import url("themes/nocturne/gate-content.css") not -moz-pref("relics.active");
""", encoding="utf-8")

# Meridian: the new tab shows the animated SVG instead of the script-drawn clock
mc = DST / "themes" / "meridian" / "userContent.css"
css = mc.read_text(encoding="utf-8")
newtab_old = """  html, body { background: #070a13 !important; color: #e6dcc4 !important; }
  .logo-and-wordmark-wrapper, .logo-and-wordmark { display: none !important; }
}
/* the private page's text would sit behind the clock. Search from the address bar. */
@-moz-document url("about:privatebrowsing") {
  body > * { visibility: hidden !important; }
}"""
newtab_new = """  html, body { background: #070a13 !important; color: #e6dcc4 !important; }
  .logo-and-wordmark-wrapper, .logo-and-wordmark { display: none !important; }
  /* the instrument, drawn by assets/meridian.svg */
  body::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -1;
    pointer-events: none;
    background: url("assets/meridian.svg") center / cover no-repeat;
  }
  @media -moz-pref("meridian.freeze") {
    body::before { background-image: url("assets/still/meridian.svg") !important; }
  }
}"""
assert css.count(newtab_old) == 1, "meridian userContent.css changed: update build_css_only.py"
css = css.replace(newtab_old, newtab_new)
css = css.replace("""   The clock is drawn over the new tab by chrome.js; the page
   underneath only has to be the same night blue.""", """   CSS-only edition: the new tab shows the animated instrument
   from assets/meridian.svg (no live time or date).""")
mc.write_text(css, encoding="utf-8")

subprocess.run([sys.executable, str(ROOT / "tools" / "make_meridian_css.py")], check=True)

# ---- checks: nothing that needs a script, and every url() points at a real file
problems = [str(p.relative_to(ROOT)) for p in DST.rglob("*") if p.suffix in SKIP_FILES]
for sheet in DST.rglob("*.css"):
    text = sheet.read_text(encoding="utf-8")
    for ref in re.findall(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', text):
        if ref.startswith(("data:", "chrome:", "http", "#", "resource:", "about:")):
            continue
        if not (sheet.parent / ref).exists():
            problems.append(f"{sheet.relative_to(ROOT)} -> missing {ref}")
if problems:
    print("PROBLEMS:\n  " + "\n  ".join(problems))
    sys.exit(1)
files = sum(1 for p in DST.rglob("*") if p.is_file())
print(f"built css-only/chrome: {files} files, no scripts, every url() resolves")

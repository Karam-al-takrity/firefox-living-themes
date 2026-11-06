/* =====================================================================
   SWITCHER - chrome.js
   Run in every browser window by theme-loader.cfg (Firefox autoconfig),
   because chrome/userChrome.css imports themes/switcher/ first.

   - Finds every theme in chrome/themes/ (each folder with a userChrome.css;
     an optional theme.json gives it a title, description and icon).
   - Makes sure exactly one theme is active. A theme is active when its pref
     <name>.active is true; chrome/userChrome.css and userContent.css import
     each theme only while that pref is on, so switching is live - no restart.
   - Runs each theme's own chrome.js (music etc.); those check <name>.active
     themselves and stay quiet while their theme is off.
   - Adds a palette button next to the menu button: pick a theme from the
     list, freeze its animations or mute its music.
   - Ctrl+Alt+T cycles through the themes.
   ===================================================================== */
"use strict";
(function (win) {
  if (!win.gBrowser || win.themeSwitcher) return;
  const doc = win.document;
  const prefs = Services.prefs;
  const Ci = Components.interfaces;
  const BASE = "resource://user-chrome/themes/";
  const DEFAULT_THEME = "nocturne";

  // ---------------- find the themes ----------------
  const dir = Services.dirsvc.get("ProfD", Ci.nsIFile);
  dir.append("chrome");
  dir.append("themes");
  const names = [];
  for (const f of dir.directoryEntries) {
    const entry = f.QueryInterface(Ci.nsIFile);
    if (!entry.isDirectory() || entry.leafName === "switcher" || entry.leafName.startsWith(".")) continue;
    const css = entry.clone();
    css.append("userChrome.css");
    if (css.exists()) names.push(entry.leafName);
  }
  names.sort();

  const isActive = n => prefs.getBoolPref(n + ".active", false);
  const current = () => names.find(isActive);

  // exactly one active theme
  if (!current() && names.length) {
    prefs.setBoolPref((names.includes(DEFAULT_THEME) ? DEFAULT_THEME : names[0]) + ".active", true);
  }
  // write every theme's flag explicitly (themes treat a missing flag as "on")
  { const on = current(); for (const n of names) if (n !== on) prefs.setBoolPref(n + ".active", false); }

  // ---------------- run each theme's chrome.js ----------------
  for (const n of names) {
    const js = dir.clone();
    js.append(n);
    js.append("chrome.js");
    if (!js.exists()) continue;
    const scope = { window: win, document: doc, Services, console: win.console, themeName: n, themeURL: BASE + n + "/" };
    try {
      Services.scriptloader.loadSubScript(BASE + n + "/chrome.js?" + js.lastModifiedTime, scope);
    } catch (e) {
      Components.utils.reportError("switcher: " + n + "/chrome.js: " + e);
    }
  }

  // ---------------- switching ----------------
  function activate(name) {
    if (!names.includes(name) || isActive(name)) return;
    // turn the new one on first, so there is never a moment with no theme
    prefs.setBoolPref(name + ".active", true);
    for (const n of names) if (n !== name) prefs.setBoolPref(n + ".active", false);
    for (const w of Services.wm.getEnumerator("navigator:browser")) {
      const root = w.document.documentElement;
      root.removeAttribute("theme-switching");
      void root.clientWidth;
      root.setAttribute("theme-switching", "true");
      w.setTimeout(() => root.removeAttribute("theme-switching"), 800);
    }
  }
  function cycle() {
    if (!names.length) return;
    const i = names.indexOf(current());
    activate(names[(i + 1) % names.length]);
  }

  // ---------------- the button and its menu ----------------
  const meta = {};
  const btn = doc.createXULElement("toolbarbutton");
  btn.id = "theme-switcher-button";
  btn.className = "toolbarbutton-1 chromeclass-toolbar-additional";
  btn.setAttribute("type", "menu");
  btn.setAttribute("label", "Themes");
  btn.setAttribute("tooltiptext", "Switch theme  (Ctrl+Alt+T cycles)");
  btn.setAttribute("image", BASE + "switcher/assets/palette.svg");
  const popup = doc.createXULElement("menupopup");
  popup.id = "theme-switcher-popup";
  btn.appendChild(popup);
  const anchor = doc.getElementById("PanelUI-button");
  if (anchor) anchor.before(btn);
  else doc.getElementById("nav-bar").appendChild(btn);

  function item(label, opts = {}) {
    const m = doc.createXULElement("menuitem");
    m.setAttribute("label", label);
    for (const [k, v] of Object.entries(opts)) if (v !== undefined && v !== null) m.setAttribute(k, v);
    popup.appendChild(m);
    return m;
  }

  function fill() {
    popup.textContent = "";
    const head = item("Themes", { disabled: "true", class: "theme-switcher-header" });
    head.disabled = true;
    const now = current();
    for (const n of names) {
      const info = meta[n] || {};
      const m = item(info.title || n.charAt(0).toUpperCase() + n.slice(1), {
        class: "menuitem-iconic theme-switcher-theme",
        image: info.icon ? BASE + n + "/" + info.icon : null,
        acceltext: info.description || "",
        tooltiptext: info.description || "",
      });
      m.toggleAttribute("current", n === now);
      m.addEventListener("command", () => activate(n));
    }
    if (!now) return;
    popup.appendChild(doc.createXULElement("menuseparator"));
    const freeze = item("Freeze animations", { type: "checkbox", class: "theme-switcher-option" });
    if (prefs.getBoolPref(now + ".freeze", false)) freeze.setAttribute("checked", "true");
    freeze.addEventListener("command", () => prefs.setBoolPref(now + ".freeze", !prefs.getBoolPref(now + ".freeze", false)));
    const hasMusic = names.includes(now) && (() => { const js = dir.clone(); js.append(now); js.append("chrome.js"); return js.exists(); })();
    if (hasMusic) {
      const music = item("Music", { type: "checkbox", class: "theme-switcher-option" });
      if (prefs.getBoolPref(now + ".music", true)) music.setAttribute("checked", "true");
      music.addEventListener("command", () => prefs.setBoolPref(now + ".music", !prefs.getBoolPref(now + ".music", true)));
    }
  }
  popup.addEventListener("popupshowing", fill);

  // read each theme's theme.json (optional)
  for (const n of names) {
    win.fetch(BASE + n + "/theme.json").then(r => r.ok ? r.json() : null).then(j => { if (j) meta[n] = j; }).catch(() => {});
  }

  // ---------------- keyboard: Ctrl+Alt+T cycles ----------------
  win.addEventListener("keydown", e => {
    if (e.ctrlKey && e.altKey && !e.shiftKey && !e.metaKey && e.code === "KeyT") {
      e.preventDefault();
      e.stopPropagation();
      cycle();
    }
  }, true);

  win.themeSwitcher = { get themes() { return names.slice(); }, get current() { return current(); }, activate, cycle };
})(window);

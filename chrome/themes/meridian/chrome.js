/* =====================================================================
   MERIDIAN - chrome.js
   Run in every browser window by the switcher (via theme-loader.cfg).

   Shows the astronomical clock (assets/clock.js) over the new tab page.
   It lives inside the page area only, never takes clicks and never covers
   the toolbars, and it runs only while a new tab shows in the focused window.

   Sound, new tab only and quiet: the clock's tick, and now and then a few
   notes of a music box. All synthesised, no audio files.

   Prefs: meridian.active (set by the switcher), meridian.freeze,
          meridian.music, meridian.music.volume (0-100, default 25)
   ===================================================================== */
"use strict";
(function (win) {
  if (!win.gBrowser || win.meridianTheme) return;
  const doc = win.document;
  const prefs = Services.prefs;
  const HTML = "http://www.w3.org/1999/xhtml";
  const PREF_ACTIVE = "meridian.active", PREF_FREEZE = "meridian.freeze";
  const PREF_ON = "meridian.music", PREF_VOL = "meridian.music.volume";
  const NEWTAB = /^about:(newtab|home|privatebrowsing)(?:[?#]|$)/;

  const lib = {};
  Services.scriptloader.loadSubScript(themeURL + "assets/clock.js", lib);

  const isActive = () => prefs.getBoolPref(PREF_ACTIVE, false);
  const isFrozen = () => prefs.getBoolPref(PREF_FREEZE, false) || win.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const isOn = () => prefs.getBoolPref(PREF_ON, true);
  const level = () => Math.max(0, Math.min(100, prefs.getIntPref(PREF_VOL, 25))) / 100;
  const rand = (a, b) => a + Math.random() * (b - a);
  const hz = midi => 440 * Math.pow(2, (midi - 69) / 12);

  let focused = Services.focus.activeWindow === win;
  const onNewTab = () => {
    const uri = win.gBrowser.selectedBrowser && win.gBrowser.selectedBrowser.currentURI;
    return !!uri && NEWTAB.test(uri.spec);
  };
  const showing = () => isActive() && win.windowState !== win.STATE_MINIMIZED && onNewTab();

  /* ------------------------------ the overlay ------------------------------- */
  const canvas = doc.createElementNS(HTML, "canvas");
  canvas.id = "meridian-canvas";
  canvas.style.cssText = "position:absolute;inset:0;width:100%;height:100%;z-index:5;pointer-events:none;display:none;";
  const box = doc.getElementById("tabbrowser-tabbox");
  if (box) box.append(canvas);

  let clock = null, failed = false, raf = 0, lastFrame = 0, frozenTimer = 0;
  let introAt = win.performance.now();

  function ensureClock() {
    if (clock || failed) return;
    try {
      clock = lib.createMeridian(canvas);
    } catch (e) {
      failed = true;
      Components.utils.reportError("meridian: " + e);
    }
  }
  function paint(now, intro) {
    const dpr = win.devicePixelRatio;
    const w = Math.max(2, Math.round(canvas.clientWidth * dpr));
    const h = Math.max(2, Math.round(canvas.clientHeight * dpr));
    clock.resize(w, h);
    clock.draw(now, new Date(), intro);
  }
  function frame(now) {
    raf = 0;
    if (!clock || !showing() || !focused || isFrozen()) return;
    raf = win.requestAnimationFrame(frame);
    if (now - lastFrame < 15) return;    // high-refresh screens stay at 60 fps
    lastFrame = now;
    paint(now, Math.min(1, (now - introAt) / 2800));
  }
  function startLoop() { if (!raf) raf = win.requestAnimationFrame(frame); }
  function stopLoop() { if (raf) { win.cancelAnimationFrame(raf); raf = 0; } }

  /* --------------------------------- sound ---------------------------------- */
  let ac = null, master = null, verb = null, click = null;
  let playing = false, stopTimer = 0, tickTimer = 0;
  const timers = new Set();
  function later(ms, fn) { const id = win.setTimeout(() => { timers.delete(id); fn(); }, ms); timers.add(id); }
  function clearTimers() { for (const id of timers) win.clearTimeout(id); timers.clear(); }

  function build() {
    ac = new win.AudioContext();
    master = ac.createGain();
    master.gain.value = 0;
    master.connect(ac.destination);
    const len = Math.floor(ac.sampleRate * 3);
    const buf = ac.createBuffer(2, len, ac.sampleRate);
    for (let c = 0; c < 2; c++) {
      const d = buf.getChannelData(c);
      for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3);
    }
    verb = ac.createConvolver();
    verb.buffer = buf;
    const wet = ac.createGain();
    wet.gain.value = 0.35;
    verb.connect(wet).connect(master);
    const n = Math.floor(ac.sampleRate * 0.02);
    click = ac.createBuffer(1, n, ac.sampleRate);
    const d = click.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
  }
  function tick() {
    if (!playing) return;
    const s = ac.createBufferSource();
    s.buffer = click;
    const f = ac.createBiquadFilter();
    f.type = "bandpass"; f.Q.value = 4;
    f.frequency.value = new Date().getSeconds() % 2 ? 2600 : 3300;
    const g = ac.createGain();
    g.gain.value = 0.05;
    s.connect(f).connect(g).connect(master);
    s.start();
    // stay on the real second, so the sound lands with the hand
    tickTimer = win.setTimeout(tick, 1000 - (Date.now() % 1000));
  }
  // a music box tine: a clear tone with a quick metallic overtone
  function tine(midi, t, vel) {
    const out = ac.createGain();
    out.gain.setValueAtTime(0.0001, t);
    out.gain.exponentialRampToValueAtTime(vel, t + 0.004);
    out.gain.exponentialRampToValueAtTime(0.0001, t + 2.8);
    for (const [mul, amp] of [[1, 1], [3.01, 0.22], [6.2, 0.06]]) {
      const o = ac.createOscillator();
      o.frequency.value = hz(midi) * mul;
      const g = ac.createGain();
      g.gain.value = amp;
      o.connect(g).connect(out);
      o.start(t);
      o.stop(t + 2.9);
    }
    out.connect(master);
    out.connect(verb);
  }
  const PHRASES = [
    [74, 78, 81, 86, 85, 81],
    [71, 74, 78, 83, 81, 78, 74],
    [69, 73, 76, 81, 78, 74],
    [78, 81, 83, 85, 81],
    [66, 69, 74, 78, 76, 73, 69],
  ];
  let phrase = 0;
  function musicBox() {
    if (!playing) return;
    const notes = PHRASES[phrase++ % PHRASES.length];
    const t = ac.currentTime + 0.05, step = 0.46;
    notes.forEach((n, i) => tine(n, t + i * step + rand(-0.012, 0.012), 0.05 + rand(0, 0.015)));
    later(notes.length * step * 1000 + rand(6000, 14000), musicBox);
  }
  function ramp(to, sec) {
    const t = ac.currentTime;
    master.gain.cancelScheduledValues(t);
    master.gain.setValueAtTime(master.gain.value, t);
    master.gain.linearRampToValueAtTime(to, t + sec);
  }
  function startMusic() {
    if (!ac) build();
    playing = true;
    win.clearTimeout(stopTimer);
    ac.resume();
    ramp(level(), 1.5);
    clearTimers();
    win.clearTimeout(tickTimer);
    tick();
    later(2500, musicBox);
  }
  function stopMusic() {
    playing = false;
    clearTimers();
    win.clearTimeout(tickTimer);
    if (!ac) return;
    ramp(0, 0.8);
    stopTimer = win.setTimeout(() => { if (!playing && ac) ac.suspend(); }, 1100);
  }

  /* ------------------------------ music button ------------------------------ */
  const btn = doc.createXULElement("toolbarbutton");
  btn.id = "meridian-music-button";
  btn.className = "toolbarbutton-1 chromeclass-toolbar-additional";
  btn.setAttribute("label", "The mechanism");
  btn.addEventListener("command", () => prefs.setBoolPref(PREF_ON, !isOn()));
  btn.addEventListener("wheel", e => {
    e.preventDefault();
    const next = Math.round(level() * 100) + (e.deltaY < 0 ? 5 : -5);
    prefs.setIntPref(PREF_VOL, Math.max(0, Math.min(100, next)));
  }, { passive: false });
  const strip = doc.getElementById("TabsToolbar-customization-target");
  if (strip) strip.after(btn);

  function paintButton() {
    btn.hidden = !isActive();
    const muted = !isOn() || level() === 0;
    btn.toggleAttribute("muted", muted);
    btn.toggleAttribute("playing", playing);
    btn.setAttribute("image", themeURL + "assets/icons/" + (muted ? "music-off.svg" : "music.svg"));
    btn.setAttribute("tooltiptext",
      "Tick and music box: " + (isOn() ? "on" : "off") + ", volume " + Math.round(level() * 100) + "%" +
      "\nPlays on the new tab page. Click to " + (isOn() ? "mute" : "unmute") + ", scroll to change volume.");
  }

  /* --------------------------------- state ---------------------------------- */
  function update() {
    const show = showing();
    canvas.style.display = show ? "block" : "none";
    win.clearInterval(frozenTimer);
    frozenTimer = 0;
    if (show) {
      ensureClock();
      if (clock) {
        if (focused && !isFrozen()) startLoop();
        else {
          stopLoop();
          // frozen or in the background: a still picture, kept to the right minute
          paint(win.performance.now(), 1);
          frozenTimer = win.setInterval(() => paint(win.performance.now(), 1), 30000);
        }
      }
    } else {
      stopLoop();
    }
    const want = show && isOn() && level() > 0 && focused;
    if (want && !playing) startMusic();
    else if (!want && playing) stopMusic();
    else if (playing) ramp(level(), 0.3);
    paintButton();
  }

  /* --------------------------------- events --------------------------------- */
  const progress = {
    QueryInterface: ChromeUtils.generateQI(["nsIWebProgressListener", "nsISupportsWeakReference"]),
    onLocationChange(aWebProgress) {
      if (aWebProgress && !aWebProgress.isTopLevel) return;
      if (onNewTab()) introAt = win.performance.now();
      update();
    },
  };
  const prefObserver = { observe() { update(); } };
  const WATCHED = [PREF_ACTIVE, PREF_FREEZE, PREF_ON, PREF_VOL];
  win.gBrowser.tabContainer.addEventListener("TabSelect", update);
  win.gBrowser.addProgressListener(progress);
  win.addEventListener("activate", () => { focused = true; update(); });
  win.addEventListener("deactivate", () => { focused = false; update(); });
  win.addEventListener("sizemodechange", update);
  win.addEventListener("resize", () => { if (clock && canvas.style.display !== "none" && !raf) paint(win.performance.now(), 1); });
  for (const p of WATCHED) prefs.addObserver(p, prefObserver);
  win.addEventListener("unload", () => {
    for (const p of WATCHED) prefs.removeObserver(p, prefObserver);
    clearTimers();
    win.clearTimeout(tickTimer);
    win.clearInterval(frozenTimer);
    stopLoop();
    if (ac) ac.close();
  }, { once: true });

  win.meridianTheme = {
    get state() { return { showing: showing(), clock: !!clock, failed, playing, focused, frozen: isFrozen() }; },
  };
  update();
})(window);

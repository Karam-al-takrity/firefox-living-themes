/* =====================================================================
   RELICS - chrome.js
   Run in every browser window by theme-loader.cfg (Firefox autoconfig).

   "Night music": a quiet generative ambience that plays only while a new
   tab is showing in the focused window. Nothing is downloaded and there
   are no audio files - everything is synthesised live with Web Audio:
     - koto-like plucks wandering over a Japanese in-scale (D Eb G A Bb)
     - a low, slowly beating drone
     - wind through the window
     - the lantern crackling now and then
     - a distant temple bell every half minute or so
   A small music button sits at the right end of the tab strip:
     click = music on/off, mouse wheel = volume.
   Prefs (both optional, created on first use):
     relics.music         true/false  (default true)
     relics.music.volume  0-100       (default 35)
   ===================================================================== */
"use strict";
(function (win) {
  if (!win.gBrowser || win.relicsMusic) return;
  const doc = win.document;
  const prefs = Services.prefs;
  const PREF_ON = "relics.music";
  const PREF_VOL = "relics.music.volume";
  const NEWTAB = /^about:(newtab|home)(?:[?#]|$)/;

  const PREF_ACTIVE = "relics.active";   // set by the theme switcher; true when there is no switcher
  const isActive = () => prefs.getBoolPref(PREF_ACTIVE, true);
  const isOn = () => prefs.getBoolPref(PREF_ON, true);
  const level = () => Math.max(0, Math.min(100, prefs.getIntPref(PREF_VOL, 35))) / 100;
  const rand = (a, b) => a + Math.random() * (b - a);
  const pick = list => list[Math.floor(Math.random() * list.length)];

  let ac = null, master = null, bus = null, verb = null, tick = null;
  let playing = false, active = Services.focus.activeWindow === win, stopTimer = 0;
  const timers = new Set();

  function later(ms, fn) {
    const id = win.setTimeout(() => { timers.delete(id); fn(); }, ms);
    timers.add(id);
  }
  function clearTimers() { for (const id of timers) win.clearTimeout(id); timers.clear(); }

  /* ------------------------------ sound ------------------------------ */
  function noise(sec) {
    const len = Math.floor(ac.sampleRate * sec);
    const buf = ac.createBuffer(1, len, ac.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
    return buf;
  }
  function room(sec, decay) {
    const len = Math.floor(ac.sampleRate * sec);
    const buf = ac.createBuffer(2, len, ac.sampleRate);
    for (let c = 0; c < 2; c++) {
      const d = buf.getChannelData(c);
      for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, decay);
    }
    return buf;
  }

  function build() {
    ac = new win.AudioContext();
    master = ac.createGain();
    master.gain.value = 0;
    const comp = ac.createDynamicsCompressor();
    comp.threshold.value = -18;
    comp.ratio.value = 3;
    master.connect(comp).connect(ac.destination);

    verb = ac.createConvolver();
    verb.buffer = room(4, 2.8);
    const wet = ac.createGain();
    wet.gain.value = 0.5;
    verb.connect(wet).connect(master);

    bus = ac.createGain();
    bus.gain.value = 0.75;
    bus.connect(master);
    bus.connect(verb);

    tick = noise(0.05);

    // wind: looping noise through a slowly wandering band-pass
    const wind = ac.createBufferSource();
    wind.buffer = noise(4);
    wind.loop = true;
    const band = ac.createBiquadFilter();
    band.type = "bandpass";
    band.frequency.value = 520;
    band.Q.value = 0.7;
    const windGain = ac.createGain();
    windGain.gain.value = 0.05;
    const sweep = ac.createOscillator();
    sweep.frequency.value = 0.07;
    const sweepDepth = ac.createGain();
    sweepDepth.gain.value = 260;
    sweep.connect(sweepDepth).connect(band.frequency);
    const gust = ac.createOscillator();
    gust.frequency.value = 0.11;
    const gustDepth = ac.createGain();
    gustDepth.gain.value = 0.025;
    gust.connect(gustDepth).connect(windGain.gain);
    wind.connect(band).connect(windGain).connect(master);
    windGain.connect(verb);
    wind.start(); sweep.start(); gust.start();

    // drone: D2, slightly detuned against itself, with A2 and D3 above
    const droneFilter = ac.createBiquadFilter();
    droneFilter.type = "lowpass";
    droneFilter.frequency.value = 420;
    const droneGain = ac.createGain();
    droneGain.gain.value = 0.045;
    droneFilter.connect(droneGain).connect(master);
    droneGain.connect(verb);
    for (const [freq, detune, amp] of [[73.42, -4, 1], [73.42, 5, 1], [110, 0, 0.6], [146.83, 3, 0.35]]) {
      const o = ac.createOscillator();
      o.type = "triangle";
      o.frequency.value = freq;
      o.detune.value = detune;
      const g = ac.createGain();
      g.gain.value = amp;
      o.connect(g).connect(droneFilter);
      o.start();
    }
  }

  // D in-scale (miyako-bushi), low to high
  const SCALE = [196.00, 220.00, 293.66, 311.13, 392.00, 440.00, 466.16, 587.33, 622.25, 783.99, 880.00];

  function pluck(freq, t, vel) {
    const o = ac.createOscillator();
    o.type = "triangle";
    o.frequency.value = freq;
    const o2 = ac.createOscillator();
    o2.frequency.value = freq * 2.01;
    const g2 = ac.createGain();
    g2.gain.value = 0.3;
    const tone = ac.createBiquadFilter();
    tone.type = "lowpass";
    tone.frequency.setValueAtTime(freq * 6, t);
    tone.frequency.exponentialRampToValueAtTime(freq * 1.5, t + 1.2);
    const env = ac.createGain();
    env.gain.setValueAtTime(0.0001, t);
    env.gain.exponentialRampToValueAtTime(vel, t + 0.008);
    env.gain.exponentialRampToValueAtTime(0.0001, t + 2.6);
    o.connect(tone);
    o2.connect(g2).connect(tone);
    tone.connect(env).connect(bus);
    o.start(t); o2.start(t);
    o.stop(t + 2.8); o2.stop(t + 2.8);
  }

  function phrase() {
    if (!playing) return;
    const t = ac.currentTime + 0.05;
    const r = Math.random();
    if (r < 0.5) {
      pluck(pick(SCALE), t, rand(0.08, 0.16));
    } else if (r < 0.85) {
      // a short run of three neighbouring notes, up or down
      const start = Math.floor(rand(0, SCALE.length - 2));
      const dir = Math.random() < 0.5 ? 1 : -1;
      for (let k = 0; k < 3; k++) {
        const idx = Math.max(0, Math.min(SCALE.length - 1, start + dir * k));
        pluck(SCALE[idx], t + k * rand(0.18, 0.34), rand(0.06, 0.13));
      }
    } // otherwise: a breath of silence
    later(rand(1800, 5200), phrase);
  }

  function crackle() {
    if (!playing) return;
    const t = ac.currentTime + 0.02;
    const s = ac.createBufferSource();
    s.buffer = tick;
    const hp = ac.createBiquadFilter();
    hp.type = "highpass";
    hp.frequency.value = 2500;
    const g = ac.createGain();
    g.gain.setValueAtTime(rand(0.015, 0.04), t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + rand(0.01, 0.03));
    s.connect(hp).connect(g).connect(master);
    s.start(t);
    later(Math.random() < 0.3 ? rand(40, 120) : rand(600, 2600), crackle);
  }

  function bell() {
    if (!playing) return;
    const t = ac.currentTime + 0.05;
    const f = pick([110, 146.83]);
    for (const [mul, amp, len] of [[1, 0.06, 7], [2.76, 0.025, 4], [5.4, 0.012, 2.5], [8.93, 0.006, 1.5]]) {
      const o = ac.createOscillator();
      o.frequency.value = f * mul;
      const g = ac.createGain();
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(amp, t + 0.01);
      g.gain.exponentialRampToValueAtTime(0.0001, t + len);
      o.connect(g);
      g.connect(verb);
      g.connect(master);
      o.start(t);
      o.stop(t + len + 0.1);
    }
    later(rand(25000, 50000), bell);
  }

  /* ----------------------------- control ----------------------------- */
  function onNewTab() {
    const uri = win.gBrowser.selectedBrowser && win.gBrowser.selectedBrowser.currentURI;
    return !!uri && NEWTAB.test(uri.spec);
  }
  function shouldPlay() {
    return isActive() && isOn() && level() > 0 && active &&
      win.windowState !== win.STATE_MINIMIZED && onNewTab();
  }
  function ramp(to, sec) {
    const t = ac.currentTime;
    master.gain.cancelScheduledValues(t);
    master.gain.setValueAtTime(master.gain.value, t);
    master.gain.linearRampToValueAtTime(to, t + sec);
  }
  function start() {
    if (!ac) build();
    playing = true;
    win.clearTimeout(stopTimer);
    ac.resume();
    ramp(level() * 0.9, 2.5);
    clearTimers();
    later(500, phrase);
    later(1500, crackle);
    later(rand(4000, 9000), bell);
  }
  function stop() {
    playing = false;
    clearTimers();
    if (!ac) return;
    ramp(0, 1.2);
    stopTimer = win.setTimeout(() => { if (!playing && ac) ac.suspend(); }, 1500);
  }
  function update() {
    const want = shouldPlay();
    if (want && !playing) start();
    else if (!want && playing) stop();
    else if (playing) ramp(level() * 0.9, 0.4);
    paintButton();
  }

  /* ----------------------------- button ------------------------------ */
  const btn = doc.createXULElement("toolbarbutton");
  btn.id = "relics-music-button";
  btn.className = "toolbarbutton-1 chromeclass-toolbar-additional";
  btn.setAttribute("label", "Night music");
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
    const frozen = prefs.getBoolPref("relics.freeze", false);
    const icon = muted ? "icons/music-off.svg"
      : playing ? (frozen ? "still/icons/music-playing.svg" : "icons/music-playing.svg")
      : "icons/music.svg";
    btn.setAttribute("image", themeURL + "assets/" + icon);
    btn.setAttribute("tooltiptext",
      "Night music: " + (isOn() ? "on" : "off") + ", volume " + Math.round(level() * 100) + "%" +
      "\nPlays on the new tab page. Click to " + (isOn() ? "mute" : "unmute") + ", scroll to change volume.");
  }

  /* ----------------------------- events ------------------------------ */
  const progress = {
    QueryInterface: ChromeUtils.generateQI(["nsIWebProgressListener", "nsISupportsWeakReference"]),
    onLocationChange() { update(); },
  };
  const prefObserver = { observe() { update(); } };

  win.gBrowser.tabContainer.addEventListener("TabSelect", update);
  win.gBrowser.addProgressListener(progress);
  win.addEventListener("activate", () => { active = true; update(); });
  win.addEventListener("deactivate", () => { active = false; update(); });
  win.addEventListener("sizemodechange", update);
  prefs.addObserver(PREF_ON, prefObserver);
  prefs.addObserver(PREF_ACTIVE, prefObserver);
  win.addEventListener("unload", () => {
    prefs.removeObserver(PREF_ON, prefObserver);
    prefs.removeObserver(PREF_ACTIVE, prefObserver);
    clearTimers();
    if (ac) ac.close();
  }, { once: true });

  win.relicsMusic = {
    get state() {
      return { playing, on: isOn(), volume: Math.round(level() * 100), context: ac ? ac.state : "none", active, newtab: onNewTab() };
    },
  };
  update();
})(window);

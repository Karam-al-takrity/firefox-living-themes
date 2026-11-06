/* =====================================================================
   AME (rain) - chrome.js
   Run in every browser window by theme-loader.cfg (Firefox autoconfig).

   "Rain radio": lo-fi night music that plays only while a new tab is
   showing in the focused window. No audio files - all synthesised live:
     - soft electric-piano chords: Dm9 - Gm9 - C13 - Fmaj9, slowly strummed
     - a warm sine bass under each chord
     - now and then a single high note from F major pentatonic
     - steady rain, drops tapping the glass, a faint record crackle
     - distant thunder about once a minute
   A small music button sits at the right end of the tab strip:
     click = music on/off, mouse wheel = volume.
   Prefs (optional, created on first use):
     ame.music         true/false  (default true)
     ame.music.volume  0-100       (default 35)
   ===================================================================== */
"use strict";
(function (win) {
  if (!win.gBrowser || win.ameMusic) return;
  const doc = win.document;
  const prefs = Services.prefs;
  const PREF_ON = "ame.music";
  const PREF_VOL = "ame.music.volume";
  const NEWTAB = /^about:(newtab|home)(?:[?#]|$)/;

  const PREF_ACTIVE = "ame.active";   // set by the theme switcher; true when there is no switcher
  const isActive = () => prefs.getBoolPref(PREF_ACTIVE, true);
  const isOn = () => prefs.getBoolPref(PREF_ON, true);
  const level = () => Math.max(0, Math.min(100, prefs.getIntPref(PREF_VOL, 35))) / 100;
  const rand = (a, b) => a + Math.random() * (b - a);
  const pick = list => list[Math.floor(Math.random() * list.length)];
  const hz = midi => 440 * Math.pow(2, (midi - 69) / 12);

  let ac = null, master = null, keys = null, verb = null, tick = null;
  let playing = false, active = Services.focus.activeWindow === win, stopTimer = 0, chordIndex = 0;
  const timers = new Set();
  function later(ms, fn) { const id = win.setTimeout(() => { timers.delete(id); fn(); }, ms); timers.add(id); }
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
  // pink noise: softer and warmer than white noise (less hiss), sounds like real rain
  function pinkNoise(sec) {
    const len = Math.floor(ac.sampleRate * sec);
    const buf = ac.createBuffer(2, len, ac.sampleRate);
    for (let c = 0; c < 2; c++) {
      const d = buf.getChannelData(c);
      let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
      for (let i = 0; i < len; i++) {
        const w = Math.random() * 2 - 1;
        b0 = 0.99886 * b0 + w * 0.0555179; b1 = 0.99332 * b1 + w * 0.0750759;
        b2 = 0.969 * b2 + w * 0.153852;    b3 = 0.8665 * b3 + w * 0.3104856;
        b4 = 0.55 * b4 + w * 0.5329522;    b5 = -0.7616 * b5 - w * 0.016898;
        d[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.11;
        b6 = w * 0.115926;
      }
    }
    return buf;
  }
  function loopNoise(filters, gain) {
    const src = ac.createBufferSource();
    src.buffer = pinkNoise(8);
    src.loop = true;
    let node = src;
    for (const [type, freq, q] of filters) {
      const f = ac.createBiquadFilter();
      f.type = type; f.frequency.value = freq; if (q) f.Q.value = q;
      node.connect(f); node = f;
    }
    const g = ac.createGain();
    g.gain.value = gain;
    node.connect(g).connect(master);
    src.start();
    return g;
  }

  function build() {
    ac = new win.AudioContext();
    master = ac.createGain();
    master.gain.value = 0;
    const comp = ac.createDynamicsCompressor();
    comp.threshold.value = -18; comp.ratio.value = 3;
    master.connect(comp).connect(ac.destination);

    verb = ac.createConvolver();
    verb.buffer = room(3, 3);
    const wet = ac.createGain();
    wet.gain.value = 0.35;
    verb.connect(wet).connect(master);

    // the keys: warm low-passed bus with a gentle tremolo
    keys = ac.createGain();
    keys.gain.value = 0.85;
    const warm = ac.createBiquadFilter();
    warm.type = "lowpass"; warm.frequency.value = 2300;
    const trem = ac.createOscillator();
    trem.frequency.value = 4.2;
    const tremDepth = ac.createGain();
    tremDepth.gain.value = 0.12;
    trem.connect(tremDepth).connect(keys.gain);
    trem.start();
    keys.connect(warm);
    warm.connect(master);
    warm.connect(verb);

    tick = noise(0.04);

    // rain: a soft, low wash heard through the window - no hiss on top
    const wash = loopNoise([["highpass", 120], ["lowpass", 950], ["lowpass", 1400]], 0.05);
    const swell = ac.createOscillator();
    swell.frequency.value = 0.04;
    const swellDepth = ac.createGain();
    swellDepth.gain.value = 0.012;
    swell.connect(swellDepth).connect(wash.gain);
    swell.start();
  }

  // chords as MIDI notes (bass first): Dm9, Gm9, C13, Fmaj9
  const CHORDS = [
    [38, 53, 57, 60, 64, 65],
    [43, 53, 58, 62, 65, 69],
    [36, 52, 58, 62, 64, 69],
    [41, 52, 57, 60, 64, 67],
  ];
  const MELODY = [72, 74, 77, 79, 81, 84, 86];   // F major pentatonic, upper octave

  function epiano(freq, t, vel, len) {
    const car = ac.createOscillator();
    car.frequency.value = freq;
    const mod = ac.createOscillator();
    mod.frequency.value = freq;
    const idx = ac.createGain();
    idx.gain.setValueAtTime(freq * 2.2, t);
    idx.gain.exponentialRampToValueAtTime(freq * 0.25, t + 1.4);
    mod.connect(idx).connect(car.frequency);
    const env = ac.createGain();
    env.gain.setValueAtTime(0.0001, t);
    env.gain.exponentialRampToValueAtTime(vel, t + 0.012);
    env.gain.exponentialRampToValueAtTime(vel * 0.35, t + 0.8);
    env.gain.exponentialRampToValueAtTime(0.0001, t + len);
    car.connect(env).connect(keys);
    car.start(t); mod.start(t);
    car.stop(t + len + 0.05); mod.stop(t + len + 0.05);
  }
  function bass(freq, t, len) {
    const o = ac.createOscillator();
    o.frequency.value = freq;
    const g = ac.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.11, t + 0.05);
    g.gain.exponentialRampToValueAtTime(0.0001, t + len);
    o.connect(g).connect(master);
    o.start(t); o.stop(t + len + 0.05);
  }

  function chord() {
    if (!playing) return;
    const notes = CHORDS[chordIndex % CHORDS.length];
    chordIndex++;
    const t = ac.currentTime + 0.05;
    const bar = 5.2;
    bass(hz(notes[0]), t, bar);
    notes.slice(1).forEach((n, i) => epiano(hz(n), t + i * rand(0.025, 0.06), rand(0.035, 0.055), 4.2));
    if (Math.random() < 0.6) {
      // a lighter second touch halfway through the bar
      notes.slice(2).forEach((n, i) => epiano(hz(n), t + bar / 2 + i * 0.03, rand(0.015, 0.025), 2.4));
    }
    if (Math.random() < 0.55) later(rand(900, 3800), () => {
      if (playing) epiano(hz(pick(MELODY)), ac.currentTime + 0.02, rand(0.03, 0.05), 2.6);
    });
    later(bar * 1000, chord);
  }

  function drip() {
    if (!playing) return;
    const t = ac.currentTime + 0.02;
    // a single soft drop on the sill: low, rounded, mostly heard as an echo
    const f = rand(900, 1500);
    const o = ac.createOscillator();
    o.frequency.setValueAtTime(f, t);
    o.frequency.exponentialRampToValueAtTime(f * 0.7, t + 0.07);
    const g = ac.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(rand(0.004, 0.009), t + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.09);
    o.connect(g); g.connect(verb);
    o.start(t); o.stop(t + 0.12);
    later(rand(1800, 6000), drip);
  }

  function crackle() {
    if (!playing) return;
    const t = ac.currentTime + 0.02;
    const s = ac.createBufferSource();
    s.buffer = tick;
    const hp = ac.createBiquadFilter();
    hp.type = "bandpass"; hp.frequency.value = 2200; hp.Q.value = 0.8;
    const g = ac.createGain();
    g.gain.setValueAtTime(rand(0.0015, 0.005), t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.012);
    s.connect(hp).connect(g).connect(master);
    s.start(t);
    later(rand(400, 2500), crackle);
  }

  function thunder() {
    if (!playing) return;
    const t = ac.currentTime + 0.05;
    const s = ac.createBufferSource();
    s.buffer = noise(7);
    const lp = ac.createBiquadFilter();
    lp.type = "lowpass";
    lp.frequency.setValueAtTime(260, t);
    lp.frequency.exponentialRampToValueAtTime(70, t + 6);
    const g = ac.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.22, t + 0.4);
    g.gain.exponentialRampToValueAtTime(0.08, t + 1.6);
    g.gain.exponentialRampToValueAtTime(0.0001, t + 6.5);
    s.connect(lp).connect(g);
    g.connect(master); g.connect(verb);
    s.start(t); s.stop(t + 7);
    later(rand(50000, 110000), thunder);
  }

  /* ----------------------------- control ----------------------------- */
  function onNewTab() {
    const uri = win.gBrowser.selectedBrowser && win.gBrowser.selectedBrowser.currentURI;
    return !!uri && NEWTAB.test(uri.spec);
  }
  function shouldPlay() {
    return isActive() && isOn() && level() > 0 && active && win.windowState !== win.STATE_MINIMIZED && onNewTab();
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
    later(400, chord);
    later(900, drip);
    later(1200, crackle);
    later(rand(15000, 30000), thunder);
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
  btn.id = "ame-music-button";
  btn.className = "toolbarbutton-1 chromeclass-toolbar-additional";
  btn.setAttribute("label", "Rain radio");
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
    const frozen = prefs.getBoolPref("ame.freeze", false);
    const icon = muted ? "icons/music-off.svg"
      : playing ? (frozen ? "still/icons/music-playing.svg" : "icons/music-playing.svg")
      : "icons/music.svg";
    btn.setAttribute("image", themeURL + "assets/" + icon);
    btn.setAttribute("tooltiptext",
      "Rain radio: " + (isOn() ? "on" : "off") + ", volume " + Math.round(level() * 100) + "%" +
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

  win.ameMusic = {
    get state() {
      return { playing, on: isOn(), volume: Math.round(level() * 100), context: ac ? ac.state : "none", active, newtab: onNewTab() };
    },
  };
  update();
})(window);

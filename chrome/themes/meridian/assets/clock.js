/* =====================================================================
   MERIDIAN - clock.js
   A brass astronomical clock drawn on a 2D canvas. Everything is real:
   the hands tell the time, the calendar ring turns to today's date, the
   planets sit at their calculated positions and the moon dial shows the
   actual phase. Slow-changing parts are drawn once and cached as images.

   Loaded by chrome.js, and by tools/meridian-preview.html for testing.
   ===================================================================== */
this.createMeridian = function (canvas) {
  const ctx = canvas.getContext("2d", { alpha: false });
  const HTML = "http://www.w3.org/1999/xhtml";
  const TAU = Math.PI * 2;
  const BRASS = "#c9a86a", BRIGHT = "#f0d9a6", DIM = "rgba(201,168,106,.34)", FAINT = "rgba(201,168,106,.16)";
  const STEEL = "#8fb4c9", RUBY = "#c8324a", VERDIGRIS = "#5fb7a5";
  const SERIF = '"Palatino Linotype", "Book Antiqua", Georgia, serif';
  const MONTHS = ["JANUARIVS", "FEBRVARIVS", "MARTIVS", "APRILIS", "MAIVS", "IVNIVS", "IVLIVS", "AVGVSTVS", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"];
  const DAYS = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  const ROMAN = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"];

  let W = 0, H = 0, S = 0, R = 0, cx = 0, cy = 0, wide = false;
  const sprites = {};

  function sprite(size, paint) {
    const c = canvas.ownerDocument.createElementNS(HTML, "canvas");
    c.width = c.height = Math.ceil(size);
    const g = c.getContext("2d");
    g.translate(c.width / 2, c.height / 2);
    paint(g);
    return c;
  }
  function circle(g, r, color, width) {
    g.beginPath(); g.arc(0, 0, r, 0, TAU);
    g.strokeStyle = color; g.lineWidth = width; g.stroke();
  }
  function ticks(g, n, r1, r2, color, width, every, r3) {
    g.strokeStyle = color; g.lineWidth = width;
    g.beginPath();
    for (let i = 0; i < n; i++) {
      const a = (i / n) * TAU;
      const inner = every && i % every === 0 ? r3 : r2;
      g.moveTo(Math.cos(a) * r1, Math.sin(a) * r1);
      g.lineTo(Math.cos(a) * inner, Math.sin(a) * inner);
    }
    g.stroke();
  }
  // engraved text following a circle, centred on the given angle (0 = top)
  function ringText(g, text, r, angle, size, color, spacing) {
    g.save();
    g.font = `${size}px ${SERIF}`;
    g.fillStyle = color;
    g.textAlign = "center";
    g.textBaseline = "middle";
    const step = spacing || size * 0.82;
    const start = angle - ((text.length - 1) * step) / (2 * r);
    for (let i = 0; i < text.length; i++) {
      const a = start + (i * step) / r;
      g.save();
      g.rotate(a);
      g.translate(0, -r);
      g.fillText(text[i], 0, 0);
      g.restore();
    }
    g.restore();
  }
  function gearSprite(teeth, rp, spokes) {
    const tooth = rp * 0.1 + 1.5;
    return sprite((rp + tooth + 3) * 2, g => {
      g.beginPath();
      for (let i = 0; i < teeth; i++) {
        const a = (i / teeth) * TAU, w = TAU / teeth;
        const pts = [[rp - tooth, -0.25], [rp + tooth, -0.14], [rp + tooth, 0.14], [rp - tooth, 0.25]];
        for (const [r, f] of pts) {
          const x = Math.cos(a + f * w) * r, y = Math.sin(a + f * w) * r;
          if (i === 0 && f === -0.25) g.moveTo(x, y); else g.lineTo(x, y);
        }
      }
      g.closePath();
      g.fillStyle = "rgba(201,168,106,.07)";
      g.fill();
      g.strokeStyle = BRASS; g.lineWidth = Math.max(1, S * 0.0011); g.stroke();
      circle(g, rp * 0.72, DIM, 1);
      circle(g, rp * 0.2, BRASS, 1);
      g.strokeStyle = DIM; g.lineWidth = Math.max(1.2, rp * 0.05);
      g.beginPath();
      for (let i = 0; i < spokes; i++) {
        const a = (i / spokes) * TAU;
        g.moveTo(Math.cos(a) * rp * 0.2, Math.sin(a) * rp * 0.2);
        g.lineTo(Math.cos(a) * rp * 0.72, Math.sin(a) * rp * 0.72);
      }
      g.stroke();
      g.beginPath(); g.arc(0, 0, Math.max(1.5, rp * 0.07), 0, TAU); g.fillStyle = RUBY; g.fill();
    });
  }

  function build() {
    // the deep blue field, with the faintest engraved star lines
    sprites.bg = (() => {
      const c = canvas.ownerDocument.createElementNS(HTML, "canvas");
      c.width = W; c.height = H;
      const g = c.getContext("2d");
      const f = g.createRadialGradient(cx, cy, S * 0.1, cx, cy, Math.max(W, H) * 0.72);
      f.addColorStop(0, "#111a2e"); f.addColorStop(0.55, "#090d18"); f.addColorStop(1, "#04060b");
      g.fillStyle = f; g.fillRect(0, 0, W, H);
      let seed = 7;
      const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
      for (let i = 0; i < 260; i++) {
        g.fillStyle = `rgba(232,222,196,${0.1 + rnd() * 0.5})`;
        g.beginPath(); g.arc(rnd() * W, rnd() * H, rnd() * S * 0.0012 + 0.4, 0, TAU); g.fill();
      }
      return c;
    })();

    const line = Math.max(1, S * 0.0012);
    // calendar ring: turns once a year
    sprites.calendar = sprite(R * 2.1, g => {
      circle(g, R, BRASS, line * 1.8);
      circle(g, R * 0.985, DIM, line * 0.7);
      circle(g, R * 0.875, BRASS, line);
      let start = 0;
      g.font = `${R * 0.04}px ${SERIF}`;
      for (let m = 0; m < 12; m++) {
        const span = (DAYS[m] / 365.25) * TAU;
        const a = start - Math.PI / 2;
        g.strokeStyle = BRASS; g.lineWidth = line;
        g.beginPath();
        g.moveTo(Math.cos(a) * R * 0.875, Math.sin(a) * R * 0.875);
        g.lineTo(Math.cos(a) * R * 0.985, Math.sin(a) * R * 0.985);
        g.stroke();
        for (let d = 1; d < DAYS[m]; d++) {
          const da = a + (d / 365.25) * TAU, long = d % 5 === 0;
          g.strokeStyle = long ? BRASS : DIM;
          g.lineWidth = long ? line : line * 0.7;
          g.beginPath();
          g.moveTo(Math.cos(da) * R * 0.985, Math.sin(da) * R * 0.985);
          g.lineTo(Math.cos(da) * R * (long ? 0.955 : 0.97), Math.sin(da) * R * (long ? 0.955 : 0.97));
          g.stroke();
        }
        ringText(g, MONTHS[m], R * 0.915, start + span / 2, R * 0.036, BRIGHT, R * 0.036);
        start += span;
      }
    });

    // hour ring: fixed, like the dial of a clock
    sprites.hours = sprite(R * 1.8, g => {
      circle(g, R * 0.86, BRASS, line);
      circle(g, R * 0.725, BRASS, line * 1.3);
      circle(g, R * 0.715, DIM, line * 0.7);
      ticks(g, 60, R * 0.86, R * 0.84, BRASS, line * 0.8, 5, R * 0.825);
      for (let h = 0; h < 12; h++) {
        ringText(g, ROMAN[h], R * 0.778, (h / 12) * TAU, R * 0.062, BRIGHT, R * 0.05);
      }
    });

    // the rete: an open star map with curling tracery, turning with the sky
    sprites.rete = sprite(R * 1.46, g => {
      const r = R * 0.7;
      g.strokeStyle = BRASS; g.lineWidth = line;
      // the ecliptic, an offset circle as on a real astrolabe
      g.beginPath(); g.arc(0, -r * 0.2, r * 0.76, 0, TAU); g.stroke();
      circle(g, r * 0.99, DIM, line * 0.8);
      g.strokeStyle = DIM; g.lineWidth = line * 0.8;
      for (let i = 0; i < 8; i++) {
        g.save(); g.rotate((i / 8) * TAU);
        g.beginPath();
        g.moveTo(0, -r * 0.5);
        g.bezierCurveTo(r * 0.2, -r * 0.62, r * 0.05, -r * 0.82, r * 0.22, -r * 0.94);
        g.moveTo(0, -r * 0.5);
        g.bezierCurveTo(-r * 0.2, -r * 0.62, -r * 0.05, -r * 0.82, -r * 0.22, -r * 0.94);
        g.stroke();
        // star pointer flames at the end of each curl
        g.fillStyle = BRASS;
        g.beginPath();
        g.moveTo(r * 0.22, -r * 0.94); g.quadraticCurveTo(r * 0.27, -r * 0.9, r * 0.3, -r * 0.965);
        g.quadraticCurveTo(r * 0.24, -r * 0.96, r * 0.22, -r * 0.94); g.fill();
        g.restore();
      }
      // constellations: fixed stars joined by hairlines
      let seed = 41;
      const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
      for (let c = 0; c < 11; c++) {
        const a0 = rnd() * TAU, d0 = r * (0.5 + rnd() * 0.42);
        let x = Math.cos(a0) * d0, y = Math.sin(a0) * d0;
        const n = 3 + Math.floor(rnd() * 3);
        const pts = [[x, y]];
        for (let i = 0; i < n; i++) {
          x += (rnd() - 0.5) * r * 0.2; y += (rnd() - 0.5) * r * 0.2;
          pts.push([x, y]);
        }
        g.strokeStyle = "rgba(143,180,201,.45)"; g.lineWidth = line * 0.7;
        g.beginPath();
        pts.forEach(([px, py], i) => (i ? g.lineTo(px, py) : g.moveTo(px, py)));
        g.stroke();
        for (const [px, py] of pts) {
          g.fillStyle = "#dfeaf2";
          g.beginPath(); g.arc(px, py, line * (1 + rnd() * 1.1), 0, TAU); g.fill();
        }
      }
    });

    // inner plate: the orbits
    sprites.orbits = sprite(R * 0.96, g => {
      for (const o of ORBITS) circle(g, o.r * R, FAINT, line * 0.8);
      circle(g, R * 0.46, BRASS, line);
    });

    wide = W / H > 1.55;
    if (wide) {
      const u = R * 0.2;
      // meshing gears: centres sit exactly the sum of their pitch radii apart (0.2R per unit of u),
      // and teeth set the speed ratio, so they really turn each other
      const beside = (g, unit, angle) => ({ x: g.x + Math.cos(angle) * (g.rp + unit) * 0.2, y: g.y + Math.sin(angle) * (g.rp + unit) * 0.2 });
      const gear = (teeth, unit, spokes, at, ratio, phase) => ({ s: gearSprite(teeth, u * unit, spokes), x: at.x, y: at.y, rp: unit, ratio, phase: phase || 0 });
      const a1 = gear(36, 1, 6, { x: -1.52, y: 0.5 }, 1);
      const a2 = gear(18, 0.5, 4, beside(a1, 0.5, -0.95), -2, 0.09);
      const a3 = gear(24, 0.667, 5, beside(a1, 0.667, 3.4), -1.5, 0.13);
      const b1 = gear(30, 0.833, 5, { x: 1.48, y: 0.56 }, 1.2);
      const b2 = gear(15, 0.417, 4, beside(b1, 0.417, -2.2), -2.4, 0.2);
      sprites.gears = [a1, a2, a3, b1, b2];
      sprites.balance = sprite(u * 1.5, g => {
        circle(g, u * 0.62, BRASS, line * 1.8);
        circle(g, u * 0.54, DIM, line * 0.7);
        g.strokeStyle = BRASS; g.lineWidth = line;
        g.beginPath();
        g.moveTo(-u * 0.62, 0); g.lineTo(u * 0.62, 0);
        g.moveTo(0, -u * 0.62); g.lineTo(0, u * 0.62);
        g.stroke();
        g.fillStyle = BRASS;
        for (let i = 0; i < 4; i++) {
          g.rotate(TAU / 4);
          g.beginPath(); g.arc(u * 0.62, 0, line * 2, 0, TAU); g.fill();
        }
        g.beginPath(); g.arc(0, 0, line * 2.4, 0, TAU); g.fillStyle = RUBY; g.fill();
      });
      sprites.spring = sprite(u * 1.5, g => {
        g.strokeStyle = DIM; g.lineWidth = line * 0.8;
        g.beginPath();
        for (let a = 0; a < TAU * 4; a += 0.1) {
          const r = u * 0.06 + (a / (TAU * 4)) * u * 0.42;
          const x = Math.cos(a) * r, y = Math.sin(a) * r;
          if (a === 0) g.moveTo(x, y); else g.lineTo(x, y);
        }
        g.stroke();
      });
    }
  }

  /* --------------------------------- astronomy --------------------------------- */
  // mean longitudes at J2000 and degrees per day
  const ORBITS = [
    { name: "mercury", r: 0.14, L: 252.25, rate: 4.09233, c: "#b9b4a6", d: 1.1 },
    { name: "venus",   r: 0.2,  L: 181.98, rate: 1.60213, c: "#f1d9a0", d: 1.6 },
    { name: "earth",   r: 0.26, L: 100.46, rate: 0.98561, c: "#6fb7e0", d: 1.8 },
    { name: "mars",    r: 0.32, L: 355.45, rate: 0.52403, c: "#d2694a", d: 1.3 },
    { name: "jupiter", r: 0.38, L: 34.4,   rate: 0.08309, c: "#e3c28f", d: 2.5 },
    { name: "saturn",  r: 0.43, L: 49.94,  rate: 0.03346, c: "#e6d6a0", d: 2.1, ring: true },
  ];
  const J2000 = Date.UTC(2000, 0, 1, 12);
  const daysSince = date => (date.getTime() - J2000) / 86400000;
  const moonAge = date => {
    // days since a known new moon, wrapped by the synodic month
    const age = (date.getTime() - Date.UTC(2000, 0, 6, 18, 14)) / 86400000;
    return ((age % 29.530588) + 29.530588) % 29.530588;
  };
  function yearFraction(date) {
    const m = date.getMonth();
    let d = date.getDate() - 1 + (date.getHours() + date.getMinutes() / 60) / 24;
    for (let i = 0; i < m; i++) d += DAYS[i];
    return d / 365.25;
  }

  /* ------------------------------------ draw ------------------------------------ */
  function blit(img, x, y, angle) {
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.drawImage(img, -img.width / 2, -img.height / 2);
    ctx.restore();
  }
  // reveal: a pen sweeping round. p runs 0..1
  function sweepClip(x, y, p) {
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.arc(x, y, S * 2, -Math.PI / 2, -Math.PI / 2 + TAU * p);
    ctx.closePath();
    ctx.clip();
  }
  const clamp01 = v => Math.max(0, Math.min(1, v));
  const stage = (t, a, b) => { const k = clamp01((t - a) / (b - a)); return k * k * (3 - 2 * k); };

  function hand(angle, len, width, color, tail) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(angle);
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(0, -len);
    ctx.quadraticCurveTo(width * 1.4, -len * 0.82, width * 0.45, -len * 0.62);
    ctx.lineTo(width * 0.5, tail);
    ctx.lineTo(-width * 0.5, tail);
    ctx.lineTo(-width * 0.45, -len * 0.62);
    ctx.quadraticCurveTo(-width * 1.4, -len * 0.82, 0, -len);
    ctx.fill();
    // a small open ring along the blade, like a clockmaker's hand
    ctx.strokeStyle = color; ctx.lineWidth = Math.max(1, width * 0.28);
    ctx.beginPath(); ctx.arc(0, -len * 0.62, width * 1.15, 0, TAU); ctx.stroke();
    ctx.restore();
  }

  function draw(now, date, intro) {
    ctx.drawImage(sprites.bg, 0, 0);

    const sec = date.getSeconds(), ms = date.getMilliseconds();
    // the mechanical tick: the second hand snaps forward and settles
    const k = Math.min(1, ms / 140);
    const snap = 1 - Math.pow(1 - k, 3) + Math.sin(k * Math.PI) * 0.12;
    const seconds = sec - 1 + snap;
    const minutes = date.getMinutes() + sec / 60;
    const hours = (date.getHours() % 12) + minutes / 60;
    const dayFrac = (date.getHours() + minutes / 60) / 24;
    const yf = yearFraction(date);
    const smooth = now / 1000;

    const layer = (a, b, paint) => {
      const p = stage(intro, a, b);
      if (p <= 0) return;
      ctx.save();
      if (p < 1) sweepClip(cx, cy, p);
      paint();
      ctx.restore();
    };

    layer(0.0, 0.5, () => blit(sprites.calendar, cx, cy, -yf * TAU));
    layer(0.12, 0.6, () => blit(sprites.hours, cx, cy, 0));
    layer(0.25, 0.75, () => blit(sprites.rete, cx, cy, (dayFrac + yf) * TAU));
    layer(0.4, 0.85, () => blit(sprites.orbits, cx, cy, 0));

    // the pointer at the top of the calendar ring, marking today
    layer(0.5, 0.8, () => {
      ctx.fillStyle = RUBY;
      ctx.beginPath();
      ctx.moveTo(cx, cy - R * 0.985);
      ctx.lineTo(cx - R * 0.018, cy - R * 1.035);
      ctx.lineTo(cx + R * 0.018, cy - R * 1.035);
      ctx.fill();
    });

    // the planets, at their real positions (seen from above the Sun)
    const days = daysSince(date);
    const planets = stage(intro, 0.6, 0.95);
    if (planets > 0) {
      ctx.save();
      ctx.globalAlpha = planets;
      ctx.translate(cx, cy);
      for (const o of ORBITS) {
        const a = (((o.L + o.rate * days) % 360) * Math.PI) / 180;
        const x = Math.cos(a) * o.r * R, y = -Math.sin(a) * o.r * R, d = o.d * S * 0.0024;
        ctx.fillStyle = o.c;
        ctx.beginPath(); ctx.arc(x, y, d, 0, TAU); ctx.fill();
        if (o.ring) {
          ctx.strokeStyle = o.c; ctx.lineWidth = Math.max(0.8, S * 0.0009);
          ctx.beginPath(); ctx.ellipse(x, y, d * 2, d * 0.7, -0.4, 0, TAU); ctx.stroke();
        }
      }
      // the Sun
      const glow = ctx.createRadialGradient(0, 0, 0, 0, 0, R * 0.09);
      glow.addColorStop(0, "#fff0c4"); glow.addColorStop(0.3, "rgba(240,190,90,.65)"); glow.addColorStop(1, "rgba(240,190,90,0)");
      ctx.fillStyle = glow;
      ctx.beginPath(); ctx.arc(0, 0, R * 0.09, 0, TAU); ctx.fill();
      ctx.restore();
    }

    // side mechanisms, on wide windows
    const mech = stage(intro, 0.35, 0.9);
    if (wide && mech > 0) {
      ctx.save();
      ctx.globalAlpha = mech;
      const spin = smooth * 0.5;
      for (const g of sprites.gears) blit(g.s, cx + g.x * R, cy + g.y * R, spin * g.ratio + g.phase);
      // the balance wheel swings once a second, driving the tick
      const bx = cx - R * 1.5, by = cy - R * 0.4;
      blit(sprites.spring, bx, by, 0);
      blit(sprites.balance, bx, by, Math.sin(smooth * TAU) * 1.5);
      // the moon dial
      drawMoon(cx + R * 1.48, cy - R * 0.36, R * 0.2, date);
      ctx.restore();
    }

    // hands
    const hs = stage(intro, 0.7, 1);
    if (hs > 0) {
      ctx.save();
      ctx.globalAlpha = hs;
      hand((hours / 12) * TAU, R * 0.46, R * 0.026, BRIGHT, R * 0.06);
      hand((minutes / 60) * TAU, R * 0.66, R * 0.018, BRIGHT, R * 0.08);
      ctx.save();
      ctx.translate(cx, cy);
      ctx.rotate((seconds / 60) * TAU);
      ctx.strokeStyle = RUBY; ctx.lineWidth = Math.max(1, S * 0.0012);
      ctx.beginPath(); ctx.moveTo(0, R * 0.12); ctx.lineTo(0, -R * 0.82); ctx.stroke();
      ctx.restore();
      ctx.beginPath(); ctx.arc(cx, cy, R * 0.02, 0, TAU); ctx.fillStyle = BRIGHT; ctx.fill();
      ctx.beginPath(); ctx.arc(cx, cy, R * 0.009, 0, TAU); ctx.fillStyle = RUBY; ctx.fill();
      ctx.restore();
    }

    // the date, engraved beneath
    const txt = stage(intro, 0.75, 1);
    if (txt > 0 && H - (cy + R * 1.04) > S * 0.03) {
      ctx.save();
      ctx.globalAlpha = txt;
      ctx.font = `italic ${Math.max(11, S * 0.02)}px ${SERIF}`;
      ctx.fillStyle = BRASS;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(date.toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long", year: "numeric" }), cx, cy + R * 1.075);
      ctx.restore();
    }
  }

  function drawMoon(x, y, r, date) {
    const age = moonAge(date), phase = age / 29.530588;       // 0 new, .5 full
    ctx.save();
    ctx.translate(x, y);
    ctx.strokeStyle = BRASS; ctx.lineWidth = Math.max(1, S * 0.0012);
    ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.stroke();
    ctx.beginPath(); ctx.arc(0, 0, r * 0.92, 0, TAU); ctx.strokeStyle = DIM; ctx.stroke();
    ctx.strokeStyle = BRASS;
    ctx.beginPath();
    for (let i = 0; i < 30; i++) {
      const a = (i / 30) * TAU;
      ctx.moveTo(Math.cos(a) * r * 0.92, Math.sin(a) * r * 0.92);
      ctx.lineTo(Math.cos(a) * r * 0.86, Math.sin(a) * r * 0.86);
    }
    ctx.stroke();
    const m = r * 0.68;
    ctx.beginPath(); ctx.arc(0, 0, m, 0, TAU); ctx.fillStyle = "#0a0f1c"; ctx.fill();
    // the lit part, bounded by half a circle and half an ellipse
    const waxing = phase < 0.5;
    const curve = Math.cos(phase * TAU) * m;      // +m new .. -m full
    ctx.beginPath();
    ctx.arc(0, 0, m, -Math.PI / 2, Math.PI / 2, !waxing);
    ctx.ellipse(0, 0, Math.abs(curve), m, 0, Math.PI / 2, -Math.PI / 2, (curve > 0) === waxing);
    ctx.closePath();
    ctx.fillStyle = "#e9dcb8";
    ctx.fill();
    ctx.beginPath(); ctx.arc(0, 0, m, 0, TAU); ctx.strokeStyle = BRASS; ctx.stroke();
    ctx.font = `${r * 0.17}px ${SERIF}`;
    ctx.fillStyle = BRASS;
    ctx.textAlign = "center";
    ctx.fillText("LVNA", 0, r * 1.26);
    ctx.restore();
  }

  return {
    resize(w, h) {
      if (w === W && h === H) return;
      canvas.width = W = w;
      canvas.height = H = h;
      S = Math.min(W, H);
      R = S * 0.43;
      cx = W / 2;
      cy = H / 2 - S * 0.012;
      build();
    },
    // intro runs 0..1 as the pen draws the instrument in; pass 1 to skip it
    draw,
  };
};

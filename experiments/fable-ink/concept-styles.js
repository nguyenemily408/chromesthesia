/* Live interpretations of the five style mockups. All positions are computed from the current canvas size. */
function createConceptStyles(g, size, hueOf) {
  const TAU = 2 * Math.PI;
  const clamp = x => Math.min(1, Math.max(0, x));
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const color = (h, s, l, a = 1) => `hsla(${h},${s}%,${l}%,${clamp(a)})`;
  const noise = seed => {
    const value = Math.sin(seed * 78.233 + 12.9898) * 43758.5453;
    return value - Math.floor(value);
  };

  function gradient(x, y, radius, stops) {
    const light = g.createRadialGradient(x, y, 0, x, y, radius);
    stops.forEach(([at, shade]) => light.addColorStop(at, shade));
    return light;
  }

  function polygon(points, fill, stroke, width = 1) {
    g.beginPath();
    points.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y));
    g.closePath();
    g.fillStyle = fill;
    g.fill();
    if (stroke) {
      g.strokeStyle = stroke;
      g.lineWidth = width;
      g.stroke();
    }
  }

  function backdrop(w, h, inner, outer, x = .5, y = .56) {
    g.fillStyle = gradient(w * x, h * y, Math.hypot(w, h) * .65, [[0, inner], [1, outer]]);
    g.fillRect(0, 0, w, h);
  }

  function crystal(state, w, h) {
    backdrop(w, h, '#234660', '#070e21');
    const scale = Math.min(w, h * 1.34);
    const base = h * .8;
    g.fillStyle = gradient(w / 2, base, scale * .48, [[0, '#8eddfb75'], [1, '#8eddfb00']]);
    g.fillRect(0, 0, w, h);
    const facets = state.marks.map((mark, i) => ({
      ...mark, i, angle: (noise(i + 32) - .5) * 1.9, depth: noise(i + 120)
    })).sort((a, b) => a.depth - b.depth);
    for (const mark of facets) {
      const grown = reducedMotion.matches ? 1 : clamp(mark.age * 1.5 + .12);
      const x = w / 2 + (noise(mark.i + 7) - .5) * scale * .41;
      const y = base + (mark.depth - .5) * scale * .1;
      const length = scale * (.19 + .27 * mark.strength + .13 * noise(mark.i + 5)) * grown;
      const width = scale * (.021 + .027 * mark.depth) * (.55 + .45 * grown);
      g.save();
      g.translate(x, y);
      g.rotate(mark.angle);
      const prism = g.createLinearGradient(-width, -length, width, 0);
      prism.addColorStop(0, color(mark.hue, 75, 86, .98));
      prism.addColorStop(.44, color(mark.hue, 66, 45, .88));
      prism.addColorStop(.68, color(mark.hue + 42, 83, 67, .9));
      prism.addColorStop(1, color(mark.hue, 55, 24, .95));
      const shoulder = -length * .78;
      polygon([[-width, 0], [-width, shoulder], [width * .15, -length], [width, shoulder * .92], [width, 0]],
        prism, '#c4eeff72', 1.2);
      polygon([[-width, shoulder], [width * .15, -length], [width * .22, shoulder * .89]],
        color(mark.hue, 88, 87, .92), '#ecf9ff87');
      polygon([[width * .22, shoulder * .89], [width, shoulder * .92], [width, 0], [width * .22, -width * .4]],
        color(mark.hue + 18, 77, 28, .65), '#bce7fa53');
      const light = Math.max(mark.pulse, clamp(1 - mark.age * .85));
      if (light > .05) {
        g.fillStyle = gradient(0, -length, width * 2.6, [[0, `rgba(226,249,255,${light * .6})`], [1, '#b8eaff00']]);
        g.fillRect(-width * 3, -length - width * 3, width * 6, width * 6);
      }
      g.restore();
    }
  }

  function aurora(state, w, h) {
    backdrop(w, h, '#112647', '#040718', .5, .7);
    g.fillStyle = '#d8e7ff';
    for (let i = 0; i < 92; i++) {
      g.globalAlpha = .2 + noise(i + 90) * .55;
      g.fillRect(noise(i + 14) * w, noise(i + 37) * h * .8, 1 + noise(i) * 1.2, 1);
    }
    g.globalAlpha = 1;
    g.globalCompositeOperation = 'screen';
    const curtain = (index, hue, strength, phase) => {
      const pitchOffset = state.marks[index]?.height ?? .5;
      const center = h * (.21 + .15 * index + .12 * (pitchOffset - .5));
      const width = Math.max(3, w / 230);
      for (let x = -width; x < w; x += width) {
        const u = x / w;
        const bend = Math.sin(u * 8 + phase + index) * .10 + Math.sin(u * 16 - phase * .7) * .045;
        const edge = center + h * (bend + u * .16);
        const ray = h * (.26 + .14 * Math.sin(u * 4 + index)) * (.85 + .15 * noise(Math.round(u * 310) + index));
        const tint = g.createLinearGradient(0, edge - ray, 0, edge + h * .055);
        tint.addColorStop(0, color(hue + 55, 80, 56, 0));
        tint.addColorStop(.68, color(hue + 20, 85, 55, strength * .35));
        tint.addColorStop(.84, color(hue, 92, 59, strength));
        tint.addColorStop(1, color(hue, 90, 50, 0));
        g.fillStyle = tint;
        g.fillRect(x, edge - ray, width + .4, ray + h * .055);
      }
    };
    for (let i = 0; i < 4; i++) {
      const mark = state.marks[i];
      const hue = mark ? mark.hue : [162, 178, 258, 276][i];
      const glow = mark ? .29 + .35 * mark.strength * Math.exp(-mark.age * .55) : .16;
      curtain(i, hue, glow, reducedMotion.matches ? 0 : state.time * (.42 + i * .075));
    }
    g.globalCompositeOperation = 'source-over';
    const ridge = [[0, h]];
    for (let i = 0; i <= 40; i++) {
      ridge.push([w * i / 40, h * (.91 - .065 * noise(i + 24) - .035 * Math.sin(i * .32))]);
    }
    ridge.push([w, h]);
    polygon(ridge, '#080e1d');
  }

  function stainedGlass(state, w, h) {
    backdrop(w, h, '#634023', '#150e1b');
    const radius = Math.min(w, h) * .43;
    const cx = w / 2, cy = h * .49;
    g.fillStyle = gradient(cx, cy, radius * 1.7, [[.35, '#df893e55'], [1, '#c96b1800']]);
    g.fillRect(0, 0, w, h);
    g.save();
    g.translate(cx, cy);
    const count = 12;
    const pane = (sector, ring, mark) => {
      const a = sector / count * TAU - Math.PI / 2;
      const point = (r, turn) => [Math.cos(a + turn) * radius * r, Math.sin(a + turn) * radius * r];
      const gap = Math.PI / count;
      const inner = [.12, .39, .69][ring];
      const outer = [.45, .76, 1][ring];
      const points = [point(inner, 0), point((inner + outer) / 2, -gap), point(outer, -gap * .62),
        point(outer * 1.02, 0), point(outer, gap * .62), point((inner + outer) / 2, gap)];
      const [x, y] = point(outer, 0);
      const hue = mark?.hue ?? 38;
      const glow = mark ? .65 + .3 * Math.max(mark.pulse, Math.exp(-mark.age * 2.2)) : .14;
      const glass = gradient(x * .77, y * .77, radius * .35, [
        [0, color(hue + 14, 92, mark ? 78 : 25, glow)], [.55, color(hue, 91, mark ? 46 : 17, glow)],
        [1, color(hue - 16, 78, mark ? 25 : 9, glow)]
      ]);
      polygon(points, glass, '#24151d', Math.max(2, radius * .014));
      if (mark) polygon([points[0], points[2], points[3], point(outer * .86, 0)],
        color(hue + 20, 90, 82, .18), color(hue + 18, 80, 78, .28));
    };
    g.beginPath(); g.arc(0, 0, radius * 1.05, 0, TAU);
    g.fillStyle = '#22151b'; g.fill();
    g.strokeStyle = '#aa784f'; g.lineWidth = Math.max(3, radius * .026); g.stroke();
    for (let ring = 0; ring < 3; ring++) {
      for (let sector = 0; sector < count; sector++) pane(sector, ring, state.marks[ring * count + (sector * 5 % count)]);
    }
    g.beginPath(); g.arc(0, 0, radius * .13, 0, TAU);
    g.fillStyle = '#eab272'; g.fill();
    g.strokeStyle = '#35211c'; g.lineWidth = 3; g.stroke();
    g.restore();
  }

  function tide(state, w, h) {
    backdrop(w, h, '#123252', '#030a16', .72, .38);
    const time = reducedMotion.matches ? 0 : state.time;
    const shore = u => h * (.51 + .33 * u + .065 * Math.sin(u * 7 - .4));
    const sand = g.createLinearGradient(0, h * .45, w * .65, h);
    sand.addColorStop(0, '#263a4d');
    sand.addColorStop(.45, '#101b2d');
    sand.addColorStop(1, '#080d16');
    const beach = [[0, h], [w, h]];
    for (let i = 44; i >= 0; i--) beach.push([w * i / 44, shore(i / 44)]);
    polygon(beach, sand);
    g.globalCompositeOperation = 'screen';
    for (let i = 0; i < 13; i++) {
      const base = h * (.1 + .027 * i);
      g.beginPath();
      g.moveTo(0, base);
      for (let j = 1; j <= 28; j++) {
        const u = j / 28;
        g.lineTo(w * u, base + h * (.12 * u + .009 * Math.sin(u * 28 + i + time * .35)));
      }
      g.lineWidth = 1 + i * .08;
      g.strokeStyle = color(205, 54, 48, .05 + i * .004);
      g.stroke();
    }
    const drawWave = (mark, i) => {
      const age = Math.min(mark.age, 7);
      const alpha = (.35 + .6 * mark.strength) * Math.exp(-age * .32);
      const crest = u => h * (.41 + .35 * u + .058 * i + (reducedMotion.matches ? 0 : age * .028) +
        .06 * Math.sin(10 * u + i * 1.8 - time * .35) + .015 * Math.sin(25 * u - time));
      const hue = mark.hue;
      for (const [width, brightness] of [[20, .08], [7, .19], [1.4, .45]]) {
        g.beginPath();
        for (let j = 0; j <= 88; j++) {
          const u = j / 88;
          const y = crest(u);
          if (j === 0) g.moveTo(0, y); else g.lineTo(u * w, y);
        }
        g.lineWidth = width;
        g.strokeStyle = color(hue, 91, 66, brightness * alpha);
        g.stroke();
      }
      for (let j = 0; j < 116; j++) {
        const seed = i * 297 + j;
        const u = noise(seed + 13);
        const spread = noise(seed + 3) - .5;
        const y = crest(u) + spread * h * (.037 + .042 * age);
        g.fillStyle = color(hue + 26 * spread, 92, 61 + noise(seed) * 24, alpha * (.3 + noise(seed + 5) * .64));
        const radius = .55 + noise(seed + 28) * 1.65;
        g.fillRect(u * w, y, radius, radius);
      }
    };
    const horizon = {age: 3.2, strength: .4, hue: 202};
    [horizon, ...state.marks].slice(0, 7).reverse().forEach(drawWave);
    g.globalCompositeOperation = 'source-over';
  }

  function origami(state, w, h) {
    backdrop(w, h, '#fff0d5', '#d9b28f', .3, .25);
    const m = Math.min(w, h);
    const sites = [[.25,.41],[.7,.32],[.52,.64],[.82,.66],[.14,.69],[.39,.27],[.64,.55],[.28,.65],[.84,.44]];
    state.marks.slice(0, 5).forEach((mark, i) => {
      const [u, v] = sites[i];
      const x = w * u, y = h * v;
      const stem = m * (.14 + .045 * noise(i + 48));
      const grown = reducedMotion.matches ? 1 : clamp(.22 + mark.age * 1.4);
      g.save();
      g.translate(x, y);
      g.rotate((noise(i + 18) - .5) * .65);
      g.scale(grown, grown);
      polygon([[-2, 0], [3, 0], [11, stem * 1.5], [5, stem * 1.5]], '#747952');
      polygon([[3, stem * .84], [-stem * .47, stem * .49], [-stem * .24, stem * .90]], '#8e9560', '#777e54');
      polygon([[6, stem * 1.13], [stem * .49, stem * .72], [stem * .23, stem * 1.13]], '#a8a970', '#7f8456');
      g.restore();
    });
    state.marks.forEach((mark, i) => {
      const [u, v] = sites[i];
      const x = w * u, y = h * v;
      const radius = m * (i < 3 ? .15 + .07 * mark.strength : .046 + .05 * mark.strength);
      const opening = reducedMotion.matches ? 1 : .42 + .58 * clamp(mark.age * 1.7);
      g.save();
      g.translate(x, y);
      g.rotate(noise(i + 9) * TAU);
      for (let fold = 0; fold < 7; fold++) {
        g.rotate(TAU / 7);
        const length = radius * opening * (.79 + .24 * noise(i * 7 + fold));
        const tip = [length, 0], side = length * .30, hinge = length * .48;
        g.shadowColor = '#482e2b6b'; g.shadowOffsetX = 5; g.shadowOffsetY = 7; g.shadowBlur = 13;
        polygon([[0, 0], [hinge, -side], tip, [hinge * .84, side]], color(mark.hue, 57, 57));
        g.shadowColor = 'transparent';
        polygon([[0, 0], [hinge, -side], tip, [hinge * .77, -side * .14]],
          color(mark.hue, 63, 73 + 9 * Math.cos(fold) + 9 * mark.pulse), '#fff1dc73');
        polygon([[0, 0], [hinge * .77, -side * .14], tip, [hinge * .84, side]],
          color(mark.hue, 53, 48 + 9 * Math.sin(fold)), '#ae74674a');
      }
      g.restore();
    });
  }

  function renderer(draw, limit, interval, rolling = false) {
    let state, lastTime, lastMark, nextPulse;
    const paint = () => {
      const {width, height} = size();
      if (!width || !height) return;
      g.save();
      g.globalCompositeOperation = 'source-over';
      draw(state, width, height);
      g.restore();
    };
    return {
      fps: 30,
      init() {
        state = {time: 0, marks: []};
        lastTime = null;
        lastMark = -Infinity;
        nextPulse = 0;
        paint();
      },
      frame(F, time) {
        const elapsed = lastTime === null ? 0 : Math.max(0, Math.min(.1, time - lastTime));
        lastTime = time;
        state.time += elapsed;
        for (const mark of state.marks) {
          mark.age += elapsed * (F.energy > .08 ? 1.2 : .78);
          mark.pulse = Math.max(0, mark.pulse - elapsed * 1.75);
        }
        const canAdd = F.notes.length && (F.onset || state.time - lastMark >= interval);
        if (canAdd) {
          lastMark = state.time;
          // Give a chord's tones distinct places in the scene and keep dense passages readable.
          for (const note of F.notes.slice(0, rolling ? 2 : 3)) {
            if (!rolling && state.marks.length >= limit) {
              state.marks[nextPulse++ % limit].pulse = clamp(note.s);
              continue;
            }
            const mark = {
              hue: hueOf(note.pc), age: 0, strength: clamp(note.s),
              height: clamp((note.midi - 40) / 48), pulse: 0
            };
            if (rolling) {
              state.marks.unshift(mark);
              if (state.marks.length > limit) state.marks.pop();
            } else {
              state.marks.push(mark);
            }
          }
        }
        paint();
      },
      step() {},
      resize: paint,
      idle: () => true
    };
  }

  return {
    growingCrystal: renderer(crystal, 32, .43),
    aurora: renderer(aurora, 4, .32, true),
    stainedGlass: renderer(stainedGlass, 36, .36),
    tide: renderer(tide, 6, .40, true),
    origami: renderer(origami, 9, .65)
  };
}

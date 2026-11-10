# Claude handoff: renderer visuals

Scope: `index.html`, the seven renderer objects only. These are **OIL, SH, CR, AUR, BR, DOT and CAVE**. Everything else is byte-identical to the version I started from. That covers the head, CSS, the shared helpers (`paint`, `vivid`, `yOf`, `blob`, `grain`), WC, INK, `MODES`/`NAMES`, `sample()`, audio, the demo and the UI. I checked this by diffing against a backup. Object names and the existing methods (`init`, `frame`, `daub`, `draw`, `ink`, `begin`, `end`, `spawn`) keep their signatures. All music inputs still drive the same things: `F.notes` (pc/midi/s/v), `energy`, `bass`, `flux`, `onset` and the per-pitch-class `lev`/`viv` levels. No git changes, nothing deployed.

## Changes

**OIL: oil impasto**
- The ground is a warm radial base with a canvas weave of fine horizontal and vertical threads.
- Each daub is a ribbon with a broad loaded start that thins toward the tail. It is built in layers: a cast shadow, the paint body, and bristle ridges that are lighter on the side facing the light (light comes from the upper left). Some ridges start late or run dry.
- Each daub also gets a crest highlight, a groove shadow, two specular ticks and a small paint pile where the brush lifts.
- Composition: 60% of daubs gather around a focus that wanders slowly across the canvas. The flow field moves slower (`t` step `.0015+bass*.004`). There are at most 14 daubs per frame.
- New methods: `sw()` (width profile) and `rib()` (ribbon path).

**SH: shapes**
- Forms are placed along a composition axis that turns slowly (`axis()`, `place()`). Pitch still sets height; the axis sets where along the width a form sits. Bars align with the axis, and lines and half-discs run across it.
- Every form is drawn by `solid()`: a cast shadow, a body shaded from a lit corner to a shaded corner, and a fine rim.
- Onset forms: triangle; off-center rings with a core; a line that fades at both ends; paired arcs; a checker with shadows; a bar. Beat-to-beat lines now end in small nodes. The bass disc gets a radial gradient.
- Held-note fields are fewer and a bit fainter (probability `.02`, alpha `.2`), and the fade is slightly stronger (`.024`), so the composition stays legible.

**CR: crystal**
- Rotation is slower: `ry` step `.0024+energy*.007`, plus `.008` on an onset.
- Front facets get linear gradients across the face, so light seems to refract through the stone. Back facets stay flat for cost. Edge glints scale with specular light.
- There are up to 5 star glints on the brightest facets. A colored pool of light sits under the gem in the dominant note's color. Rays are fewer and softer, and onset bursts are unchanged.

**AUR: aurora**
- The curtains fold sideways: the strips' x positions shift, so where strips crowd the light reads as a bunched, brighter fold.
- The upper fringe shifts toward violet, the note's own color fills the body, and the hem at the bottom is bright. Vertical rays come from neighboring strips reaching to different heights.
- Motion is slower (`t` step `.0028+energy*.006`). Stars twinkle slowly. A far ridge catches a rim of the dominant note's light, in front of the near hills.
- New fields: `ridge` and a per-note phase `d` in `ph`.

**BR: ink brush**
- Strokes are now continuous tapered ribbons, replacing the scattered circles. Each stroke has a pressed entry dot, a full body and a tail that tapers to about 6% width.
- Each stroke has 18 bristles at fixed positions across the brush. As the ink load drops along the stroke, outer bristles drop out first, so the tail breaks into continuous streaks of dry brush.
- A wet core is drawn while the brush is loaded, with a faint bleed into the paper.
- Pen speed and curvature are slower, and width changes are smoothed (`wv`) so the stroke doesn't jitter. The paper has fibers, and the end splatter is thrown forward along the stroke.

**DOT: pointillism**
- Notes seed clusters that bloom outward over 50–120 frames, at most 34 at once. Within a cluster the dots are mostly the note's color, with flecks of its fifths-circle neighbors, a lighter tint and a dull complement, so they mix by eye.
- Dots are oriented elliptical dabs that follow a slow field, and some get a small highlight.
- Clusters drift slowly. A light scatter near the slower sweep keeps the ground between clusters worked.

**CAVE: crystal cave**
- Shards have a depth value `z`: far shards are smaller and dimmer and are drawn first. About 12% grow from the side walls.
- Each shard has three facets (a broad lit face, a bright bevel, a deep shadow face). One glow gradient runs along its length, brightest at the tip. A luminous core line appears when its note is active. The tip glow and onset sparkle are kept.
- Slow sway per shard; 40 drifting motes lit by the dominant note.
- The background is a flat fill tinted by the dominant note, plus a cached vignette canvas (`vg`, 192×120, built once).

## Verification done
- `node --check` passes on the extracted script.
- I loaded the page in the browser and switched through all seven styles via `sample()`. The screenshots look right and there are no console errors.
- Cost check: I timed the JavaScript work for each style's `sample()` run, with the canvas still on the GPU, against the original. Oil, aurora and pointillism cost a little more; crystal, ink brush and cave are about the same; shapes is unchanged.
- I removed a per-strip `globalAlpha` in aurora and two full-screen gradient fills in cave because they were expensive.

## Limits / notes for Codex
- **Live playback is untested.** The browser pane was hidden, so animation frames never ran and I couldn't play music. The slow motion and frame rates during playback still need checking in a visible browser. That means `frame()` driven by real `analyse()` output, beyond the synthetic frames from `sample()`.
- Motion only happens while audio is active, because `loop()` calls `R.frame` only then. I didn't touch the loop, so idle canvases stay still. If you want an idle drift, that's your call in the loop.
- On resize, AUR stars, hills and ridge and the CAVE shards keep their layout from `init` until the next reset. This is the same behavior as before.
- BR uses `lineCap='butt'` for the bristle pass and restores `'round'` afterward. OIL and SH set `lineCap`/`lineJoin` themselves.
- Repeated `getImageData` calls make Chrome move this canvas to the CPU, where every style is several times slower. Keep that in mind if you benchmark.

---

## Round 2: WC watercolor

Scope: only the WC block in `index.html` (about lines 235–291). I replaced that block in place by exact match on its old text and touched nothing else. A diff against a snapshot taken just before the edit shows changes only inside WC, so any INK changes already in the file are preserved. If you saved INK in the same instant I wrote, re-check that your INK edit is still there. The window was a single read-and-write, a few milliseconds.

`WC` keeps its name and its `init`, `frame` and `spawn` methods. Music inputs are used as before: onset and `n.s` drive spawning; pitch sets height through `yOf`; `n.s`, `energy` and low notes set size; `n.v` sets vividness; `pc` sets hue.

**Changes**
- **Paper:** the same warm gradient, plus a cold-press texture of faint soft blotches and fine speckle. This runs once, in `init`.
- **Translucent layered pigment:** 45% of washes carry a second glaze, smaller and offset from the first. Some of these take a neighboring hue on the circle of fifths, like wet-in-wet. Per-frame alpha is lower (`.028*(1-q)+.006`) and washes live longer (70–150 frames), so the color builds up as thin glazes and doesn't go opaque.
- **Natural soft blooms:** the spread still eases out (sqrt), and drift is slower and damped. 30% of washes get one back-run partway through: a drop of water pushes pigment outward and leaves a frilled edge.
- **Delicate pooled edges:** the gradient concentrates pigment toward the rim, and an occasional fine rim stroke is drawn per glaze. When a wash finishes drying it leaves one final thin, darker edge. A little granulation settles in the middle at mid-life.
- **Fuller, balanced composition:** an 8×5 coverage grid (`cov`, with the `cell()` helper). Each spawn tries 4 positions at the note's height and keeps the least-painted one. Spawning skips a cell that is already full so some paper stays visible, and coverage decays slowly. The scripted opening painting now spreads across the full width and reaches the top band, which used to stay empty.
- **Bounds:** at most 60 live washes (was 70) and at most 2 glazes each. The spawn rate is slightly lower: `.75` on onsets, `.05` while sustained.

**Verification**
- `node --check` passes.
- I loaded the opening painting in the browser by switching to style 1 only. I didn't press play or start the demo, so no audio played. No console errors.
- Cost: 380 scripted frames take about 48 ms, against 35 ms before (unflushed, best of 3), which works out to roughly 0.13 ms per frame.

**Limits**
- As before, I haven't checked live playback with real audio.
- The lower half of the opening painting is still a fairly dense warm wash. That's because the scripted chords lean on low notes, which map near the bottom and make large washes; the original had the same pattern.

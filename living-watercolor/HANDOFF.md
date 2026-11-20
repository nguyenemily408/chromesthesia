# Living Watercolor: hand-off for the integrator (Codex)

Written November 17 by the Claude session that built `living-watercolor/watercolor.html`.
Emily wants The Sound of Color app to use this watercolor animation. This note says what it is, how to use it, and what has and has not been checked.

## What it is

`living-watercolor/watercolor.html` is one self-contained page (no libraries, no assets). It runs a small paint simulation on the graphics card (WebGL 2 with float textures) and shows a watercolor that paints itself over a set length of time. It needs WebGL 2; without it the page shows a plain message.

It was built and checked on its own. It has not been tried inside `index.html` or `experiments/fable-ink/three-styles-full.html`, and it has never been driven by real music.

## Simplest way to use it: an iframe

Put the page in an iframe that fills the artwork area, with the buttons hidden:

```html
<iframe id="wc" src="living-watercolor/watercolor.html?ui=0&auto=0" style="border:0;width:100%;height:100%"></iframe>
```

Then talk to it from the app (same origin, so this works directly):

```js
const wc = document.getElementById('wc').contentWindow.watercolor;
```

The page sizes itself to the iframe. Keeping it in an iframe also keeps its canvases, styles and animation loop apart from the app's own renderers.

## Controls (`window.watercolor`)

| Call | What it does |
|---|---|
| `start({duration, seed, gold, auto})` | Fresh blank wet sheet. `duration` in seconds (the sheet stays damp until the last 12% and then dries). `seed` picks the arrangement. `gold` is `'notes'`, `'pitch'`, `'rhythm'`, `'harmony'` or `null`. `auto: false` turns off the built-in painting so only the app's calls add paint. |
| `play()` / `pause()` | Run or hold the painting's clock. |
| `seek(fraction)` | Jump to 0..1 of the duration. Forward jumps catch up quickly. A backward jump repaints from blank and loses paint added from outside. |
| `progress` | Current fraction, 0..1. |
| `addStroke({x, y, color, size, water, seconds, strength, metal})` | One dab of paint, laid over `seconds` (default 1.5). `x`, `y` run 0..1 from the bottom-left corner. `color` is `[cyan, magenta, yellow]` amounts; ready-made ones are in `watercolor.paints` (blue, cerulean, turquoise, rose, red, orange, yellow, green). `size` is the radius as a fraction of the height (default 0.06). `strength` is how much pigment (default 0.8). `metal: 'gold' | 'silver' | 'copper'` lays metal instead of colour. |
| `gold(style, {...})` | Gold in the style of one music mode: `gold('notes', {x, y, size, fill})` a ring or disc; `gold('pitch', {x, y, angle, length})` a thin curling line (`angle` in turns, 0.25 is straight up); `gold('rhythm', {x, y, spread})` a flick of small dots; `gold('harmony', {amount})` more gold along wash edges. |

Address options do the same from the URL: `?dur=240&seed=7&gold=pitch&auto=0&ui=0`, and `?t=0.5` jumps to that fraction and holds (used for still pictures).

## Suggested wiring to music (Emily's choices so far)

- Emily chose one gold style per filter: Notes = rings and discs, Pitch = thin lines, Rhythm = dot flicks, Harmony = wash edges.
- Colour and timing are not decided. Ideas discussed, not approved: note or chord picks the paint, loudness sets `strength`, low notes use darker paint, strong beats trigger `gold('rhythm')`.
- To keep the drying in step with a song, call `start({duration: songLength, auto: false})` when the song starts, and `pause()` / `play()` with the audio.

## Limits and things not checked

- At most 4 brushes can paint in the same instant. Extra `addStroke` calls wait their turn, so a burst of many notes is painted a little late. `gold('pitch')` and `gold('rhythm')` share the same 4 slots.
- Resizing the window restarts the sheet and repaints the built-in plan; paint added from outside before the resize is lost.
- Checked: still frames in headless Chrome (seeds 7, 3, 21; portrait 675x900 and one landscape), one full 4-minute real-time run in the Claude desktop browser before the gold work (it kept time; smooth motion was only confirmed for the first 30 seconds), and synthetic calls to `addStroke`, `gold` and `auto: false`. No console errors in any of these.
- Not checked: real music, phone browsers, Safari, PNG export through the app's Save painting button, a full real-time run since gold was added.
- Trial options left in the page, off by default: `?look=pearl`, `?look=shift`, `?metals=mixed`, `?vein=from,to,spread`.
- Earlier versions are kept beside the page as `watercolor_v1_backup.html` through `watercolor_v7_backup.html` (there is no v4). Nothing here is committed to git.

## Added November 20 (after the app integration)

- `beat(strength)`: one short gold line on existing paint for a strong beat, longer for a harder hit (strength 0 to 1). About 28 at most per song, never two within 0.4 seconds. Returns true when it painted. Meant for the app's Rhythm choice, which runs the built-in painting. The app calls it on each detected beat when Rhythm is chosen (since November 20).
- Short songs: with `externalClock: true` and `auto: true`, the page simulates four times the `duration` it is given, up to 240 seconds, so short songs still get well-spread washes.
- `watercolor_gold_lines_reference.html` and `.jpg` are a frozen copy of the page and the picture Emily approved. `watercolor_v8_backup.html` is the page just before these two additions.
- The root `HANDOFF.md` is the current state of the app; this file only describes the watercolor page.

- November 20, Codex pause fix: when embedded with externalClock, pause() drops pending catch-up steps and holds the current canvas. A subsequent follow()/seek() can explicitly set a new target; the app calls pause() before follow(1) on song completion. The standalone renderer’s normal clock is unchanged.

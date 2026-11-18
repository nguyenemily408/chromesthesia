# Fable ink experiment — handoff

November 10, 2026. Written by Fable 5.2 (Claude) for the model comparison.

Files in this folder:

- `baseline.html`, `ink-reference.png` — saved by Codex, not edited.
- `prototype.html` — the baseline with a new Ink in Water renderer and a silent preview button.
- `handoff.md` — this file.

Nothing outside `experiments/fable-ink/` was changed. `index.html` is still byte-identical to `baseline.html` (checked with a checksum). Nothing was committed or deployed. `AGENT-WORK.md` was not updated because it is outside my write scope; Codex should record the result there.

## Status in one paragraph

The prototype is a clear step toward the photograph in colour, softness and smoothness, and it is still a 2D approximation that does not look like the photograph. It shows saturated cyan, cobalt, violet and fuchsia clouds on white water, with soft translucent edges, slow motion, and colour that holds for over a minute. It does not show the photograph's cauliflower folds, and after about 40 seconds the clouds lean into elongated shapes with slightly ragged edges. I would treat it as a candidate to look at side by side with the baseline, not as a finished release.

## How to look at it

Serve the project folder (for example `python3 -m http.server 8791 --bind 127.0.0.1` inside `experiments/fable-ink`) and open `prototype.html`.

- **Preview ink (silent)** clears the water and pours the same 15 clouds every time, one per region of the screen, staggered over about 11 seconds. It makes no sound and never creates an audio engine. It hides the music panel so the whole screen is visible; **Music** brings the panel back.
- Add `?ink=cpu` to the address to run the unchanged baseline ink inside the same page for comparison. The status line says which one is running ("Graphics-card ink" or "Baseline ink (fallback)").
- Best moment to judge: 15 to 30 seconds after pressing the button.

## Assessment

**What code can credibly improve (and this prototype does):**

- Detail. The baseline tracks pigment on about 29,000 cells. The prototype tracks it on up to about 920,000 (1280 × 720), on the graphics card.
- Smoothness. 60 frames per second instead of 36.
- Colour. Pigment is treated as opaque paint that scatters light, so cyan over fuchsia gives the periwinkle and violet seen in the photograph, and thin ink stays a pale tint.
- Soft edges and a sense of depth. Clouds are lit from the upper left as rounded forms, creases are darkened, and a blurred copy of the ink sits behind the sharp one like out-of-focus ink further back.
- Coverage and pace. Clouds are poured slowly from every region of the screen, and a very slow current keeps them turning after pouring stops.

**What a 2D simulation cannot match:**

- Real ink is a 3D event. Plumes roll into vortex rings and fold into thin sheets in depth, and that folding is what creates the cauliflower surface. In 2D that mechanism does not exist; swirls merge into larger, smoother ones instead of breaking into finer ones.
- In the photograph you look through several translucent layers at different depths, with parallax and camera focus. Here there is one layer plus a blurred copy.
- Light scatters inside real pigment, giving the soft inner glow and true self-shadowing. Here the lighting is an estimate made from how thick the pigment is.

**Is a different technique justified?**

- Moving the same 2D method to the graphics card was justified and is what I built. It is the largest gain available today with no new dependencies.
- A sensible next step, still without dependencies: run two or three of these layers at different depths and blur the far ones. That would add real overlap and depth for roughly two to three times the graphics cost.
- A true 3D simulation with volume lighting is not realistic in a browser at this quality and frame rate, and not for today.
- If matching the photograph matters more than it being a live simulation, the honest route is real ink footage tinted and timed to the music. That is a product decision, not an engineering one.

## Specific changes in `prototype.html`

Only the ink renderer and the smallest wiring needed for the experiment.

1. The baseline ink object is kept unchanged and renamed `INK_CPU`. It is the fallback when the browser cannot run the new version, and what `?ink=cpu` selects.
2. New `INK_GL` object (WebGL2, half-float textures, no libraries):
   - Water motion on a 320-cell-wide grid; pigment on a grid up to 1280 wide.
   - Pigment is carried with an error-correcting step so folds stay crisp.
   - Each cloud is poured for 8 to 10 seconds from two slowly circling, pulsing nozzles. Each dab of pigment also adds volume, so the cloud swells outward instead of only being dragged along. An equal amount of clear water is drawn off evenly so the screen stays balanced.
   - Fresh ink carries a gentle push in its pour direction that fades over a few seconds. Preview clouds pour roughly toward the middle so the pushes balance.
   - Screen edges are walls, so ink stays in view.
   - A very slow, changing current keeps the clouds moving while the simulation is awake (it rests 90 seconds after the last cloud, like the baseline's 75).
   - Palette runs cyan → cobalt → violet → fuchsia, using the same hue numbers the baseline used.
   - All tuning numbers sit in one `look` object at the top of `INK_GL`.
3. New **Preview ink (silent)** button in the music panel, with one added sentence in the hint text. Shown only in the ink style.
4. The animation loop's ink frame rate reads `INK.fps` (60 for the new version, 36 for the baseline). One line changed.
5. `window.__inkLab` exposes the ink object and an `advance(n)` fast-forward for testing. Remove it when integrating.

Music still drives the ink through the same `frame()` entry point: the first sound releases six clouds, then one cloud per beat or so, coloured by the strongest note, limited to 18 at a time. All nine styles, the style menu, keys 1–9, file opening, tab listening, the demo, save, reset and fullscreen are the baseline's code, unchanged.

## What Codex's feedback changed

Codex opened an earlier build and reported fine curling detail and full coverage, but pale colour and a marbled look after about a minute. I made one tuning pass in response: much slower water, stronger drag, far slower pigment fade, denser and less whitened shading, a stronger back layer, and swelling clouds in place of fast jets. The result keeps saturated colour and separate rounded clouds at 60 seconds. The cost is that the fine curling detail Codex saw is mostly gone; the two pull against each other in 2D, because the stirring that makes fine curls is the same stirring that thins the ink into pale marbling.

## Tests actually run

All in the Claude desktop app's built-in browser (Chromium), on this Mac, at a 1280 × 720 viewport, served from `127.0.0.1:8791`.

| Check | Result |
| --- | --- |
| JavaScript syntax (`node --check` on the page script) | Passed |
| Page loads, new renderer starts | Passed, status line reads "Graphics-card ink" |
| **Preview ink (silent)** button | Passed. Clouds appear, music panel hides, zero audio engines created (counted), audio element stayed paused |
| Look at about 20, 25 and 60 seconds | Inspected as still frames after fast-forwarding the simulation with `__inkLab.advance` |
| Live animation | Ran on its own at about 59 steps per second over a 2-second sample |
| **Reset ink** | Passed, water clears |
| **Drop ink** | Passed, adds 8 clouds |
| Click on the water | Passed, adds 1 cloud |
| Style menu, all nine styles, then back to ink | Passed, no errors |
| `?ink=cpu` fallback | Passed, baseline ink renders, status line reads "Baseline ink (fallback)" |
| Music response | **Synthetic only.** I fed made-up note data into the ink's music entry point; it released 5 clouds over 5 seconds. No sound was played |
| Page errors during the above | None |

Not tested:

- **No real music of any kind.** Not the built-in demo, not a music file, not tab audio. This was deliberate, to honour "no automatic audible playback". How the ink looks and paces itself under a real song is unknown.
- Save painting, Fullscreen, Stop, Pause/Play and the seek bar were not pressed. Their code is unchanged from the baseline.
- Keys 1–9 were not pressed (the style menu was used instead).
- Window resize while ink is on screen: the code path exists but was not exercised.
- Phones, tablets, Safari, Firefox, and slower or integrated graphics. Speed was only measured on this machine.
- Losing and regaining the graphics context: handled in code, not exercised.
- Most judgement of the look came from fast-forwarded still frames, not from watching a full minute in real time.

## Known limitations

- It is a 2D approximation. See "What a 2D simulation cannot match".
- Cloud interiors are smooth with faint ring-like bands, not the photograph's deep folds.
- Edges show slight regular ripples or a hairy fringe in places, most visibly after 40 seconds. This comes from the water grid being coarser than the pigment grid.
- After about 40 seconds the slow current leans clouds into elongated, comet-like shapes.
- White water remains between clouds (roughly a third of the screen in the preview). The clouds reach every region but do not merge into one continuous mass as in the photograph.
- The Creator Lab link in the panel does not resolve from this folder. The baseline copy has the same issue; it is fine once the code lives next to `index.html`.
- On a zero-size (hidden) window the renderer waits for the next resize. I hit this once in testing and guarded it.

## If Codex integrates this

Copy the `INK_CPU` rename, the `INK_GL` block, the `const INK=` line, the preview button (markup, one CSS rule, one click handler) and the `INK.fps` line. Drop `window.__inkLab`. Before release, play the built-in demo and one real song and watch a full minute, since that is the part I did not test.

## How Fable helped, in plain English

Fable read the existing ink code and the reference photo, and worked out that the main limits were detail and the way colour and light were being faked, rather than the idea itself. It rewrote the ink so the graphics card does the work, which allows about 30 times more detail at a smoother frame rate, and changed the colouring so the ink reads as soft opaque paint clouds in the reference's cyan, cobalt, violet and fuchsia. It then checked its own work in a browser without playing any sound, found and fixed several problems along the way (ink moving far too fast, ink draining off the screen, saw-toothed edges, a crash on a hidden window), and adjusted the look once more after Codex's feedback about paleness. It has been direct about what is still missing: this is a flat simulation of something that is really three-dimensional, and it has not yet been watched with real music.

## Later correction by Codex

The palette restriction described above has been removed. The prototype now uses twelve note colors matching the legend. Music events can release up to four strong detected notes, so chords contribute multiple colors. Loudness and note strength set cloud size, while note vividness influences saturation. The silent sample spans all note colors and explicitly stops playback in its own tab. Codex verified palette and chord logic with synthetic inputs and checked the revised browser controls. Real-file playback and personal synesthesia associations are not validated by those checks.

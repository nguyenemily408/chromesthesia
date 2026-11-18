# Aurora over Norway: handoff to Codex

Date: November 17. From: Claude (Fable 5.2 side chat with Emily). Status: Emily approved the look after watching a 45-second clip ("looks great") and asked for it to go into The Sound of Color.

## What it is

A standalone test page, `aurora.html`, that replaces the idea behind the current Aurora Borealis style in `experiments/fable-ink/concept-styles.js`. It has not been wired into the app. Nothing in `index.html`, `three-styles-full.html` or `concept-styles.js` was changed.

- The land is one of five photographs supplied by Emily (a cabin in snowy Norwegian scenery at night). The sky was cut out of each so it is transparent.
- The sky is drawn live by a WebGL shader: stars and up to four aurora ribbons placed in perspective overhead, so the rays fan down toward the horizon.
- The lights tint the snow. Lamp-lit windows keep their warm colour.
- The view is fixed with a very slow sideways drift.

## Decisions Emily made

- Realistic look, fixed view with very slow drift.
- Songs are 4 to 6 minutes. Input is an audio file for now.
- The scenery changes only when a new song is picked, never during a song.
- The two Instagram reels she shared are inspiration only. Nothing from them is used.
- A cabin drawn by code looked fake to her; the photographs fixed that.

## Files to take

| File | Needed | Notes |
| --- | --- | --- |
| `aurora.html` | yes | Shader, scene fitting, music mapping, test controls |
| `photos/*.png` (5 files, 7.8 MB total) | yes | Emily's pictures with transparent sky. Originals are in her Downloads folder, untouched |
| `photos/scenes.json` | optional | Same data as the `SCENES` list inside `aurora.html` (file, skyline height `hv`, cabin position `fx`, aspect) |
| `record_server.py` | optional | Local helper for filming a clip with `?record=45&audio=...` |
| `test-tones.wav` | optional | Synthetic test tune |
| `aurora-clip.mp4` | **do not commit** | Contains the Beethoven recording |
| `aurora_v*_backup.html`, `*.jpg` | no | Earlier versions and review stills |

## How the music drives it

The page exposes `window.aurora`:

- `note({pitch, strength, color})`: `pitch` 0..1 picks the ribbon and, unless `color` is given, a colour from a six-step ramp (green, sea-green, teal, blue-violet, violet, pink). `strength` 0..1 is brightness. The light fades in about 1.3 seconds.
- `beat(strength)`: a ripple along every ribbon and a pink lower fringe.
- `setLevel(0..1)`: how much of the sky is lit and how tall the rays are.
- `setScene(n)`: dims, swaps the photo, comes back up.
- Harmony is simply several `note` calls at once.

The page also has its own listener (`listen()` in `aurora.html`) that analyses an audio file in the browser. That is for the standalone test only.

## Suggested way to integrate

The app already computes `F` each frame (`F.notes` with `midi`, `pc`, `s`; `F.energy`; `F.onset`; `F.flux`). Use that instead of this page's `listen()`:

- For each new note in `F.notes` on an onset: `aurora.note({pitch: clamp((n.midi - 40) / 48), strength: n.s})`. To use the app's note colours, pass `color` converted from `hueOf(n.pc)` as RGB 0..1.
- `aurora.setLevel(F.energy)`, smoothed.
- In the Rhythm filter, or whenever `F.onset` is a strong accent: `aurora.beat(F.flux)`.
- Call `aurora.setScene(next)` when a new song is chosen.

The current styles draw on a shared 2D canvas through `renderer(draw, ...)`. This one needs WebGL, so it needs its own canvas layered where the 2D one is, shown only while the Aurora style is selected, with the same `init / frame / resize / idle` shape as the other styles.

## What was tested

- JavaScript syntax check passed; no console errors.
- Still frames of all five photo sceneries at 1120 x 630 in the in-app browser, in fixed quiet, medium and loud states.
- About 40 seconds of Emily's Beethoven Symphony No. 5 file, twice: 59 note events spread across the four colour bands as 15, 13, 20 and 11; loudness level ranged 0.33 to 0.99.
- A 45-second clip recorded in headless Chrome with sound, which Emily watched and approved.

## Not tested, and known limits

- A full 4 to 6 minute song.
- Portrait and phone shapes. The photos are wide, so tall screens crop the sides; the code keeps the cabin in view but the result was not looked at.
- Reduced-motion preference is not handled.
- In very quiet passages the sky dims but does not go fully black.
- Speed does not follow the music yet: the ribbons sway at one fixed pace. Emily was offered tempo-driven sway and note-length-driven fade and has not decided.
- From audio, pitch and harmony are estimates. Loudness and beats are reliable.
- The cut-out photos are 1.5 to 1.9 MB each as PNG; converting to WebP would shrink them.

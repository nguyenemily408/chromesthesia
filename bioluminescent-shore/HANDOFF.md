# Bioluminescent wave → The Sound of Color (handoff)

Written by Claude on November 20 for Codex, who owns the integration in `experiments/fable-ink/three-styles-full.html`. Nothing in the app was edited. No renders were started. All original wave assets are untouched.

## Codex integration update — November 20

Latest revision: Emily chose **option 3, foam rim + sand lace only**, recorded at the end of `COLOR-REVIEW.md`. Applied to **Pitch** in the local prototype and app key, replacing the stronger crest tint described below. The main blue water keeps its hue; pitch color is added/mixed on the foam-rim brightness mask. Low/high synthetic browser tests showed subtler violet/pink accents without shader errors. The wave remains silent. The local extension has been rebuilt; live-song review of this latest revision is still pending. See `../HANDOFF.md` for the consolidated app status. Other filters retain their existing treatment.

The full-screen app and local Chrome extension now use this prototype for Tide. Real YouTube music reached the installed extension, Living Watercolor painted, and Tide/Pitch loaded. The original blue–turquoise-only palette and strong additive light were rejected as overexposed and hard to distinguish. See `COLOR-REVIEW.md` for Claude’s review.

The current shader replaces hue in the mid-bright wave and lightly tints foam edges, protects the brightest foam, reduces glow/sparkle/bursts, and compresses highlights without clipping channels to white. Pitch uses the app’s `PITCH_HUES`, supplied through `setPitchPalette(hues)`; Notes uses the same circle-of-fifths mapping as the app key. Tint smoothing uses a 0.25-second time constant. The standalone test panel includes fixed low/middle/high pitches; it is silent and hidden when embedded. The reviewed low and high stills used these synthetic inputs, not a song. The new look still needs a live-song check. The sections below describe the original handoff where they differ from this update.

Verified directly from MP4 track headers: both the original `wave5.mp4` and the packaged extension copy contain one video track and zero audio tracks; their SHA-256 hashes match. The wave players are muted. The extension intentionally forwards the captured music to the speakers, which is why Chrome can label The Sound of Color as the audio-playing tab. No wave sound is generated.

## Recommendation: rendered video + audio-driven timing and light

Use the finished Blender render as the picture and let the music decide **when** a wave rolls in, **how fast** it breaks, and **where extra light lands**. Do not try to rebuild the wave live in the browser.

| | Rendered video, audio-driven timing/glow (recommended) | Real-time geometry export |
| --- | --- | --- |
| Look | Exactly the approved render: ray-traced water, 3D spray, volumetric glow, bloom | Would need a WebGL re-creation of the wave mesh, spray, lace and glow; weeks of work to get close, and it would still look like the earlier "slab" browser attempts |
| Music reaction | Timing (when it breaks, break speed), brightness, colour tint, sparkle bursts, flash on hits | Everything, including shape, but shape is what took days to tune |
| Cost at runtime | One 1280×720 H.264 video + a small shader; cheap on phones and laptops | Heavy (hundreds of thousands of vertices + particles each frame) |
| Risk | Each wave is the same 7 s clip; reactions are "on top" of it. Variety comes from timing, speed and light | High; nothing exists yet |
| File size | wave5.mp4 is 12.9 MB | Mesh sequence would be hundreds of MB |

A middle road, if Codex later wants more variety: render 2–3 more clips from `wave5.py` with different seeds or camera heights and have the player pick one per wave. The adapter below already assumes one clip per wave, so adding clips is a small change.

## Latest usable asset

- **Video:** `bioluminescent-shore/blender/serious/wave5.mp4` — 7.0 s, 168 frames at 24 fps, 1280×720, H.264, silent. Rendered November 18 from `wave5.py` (the pull-back fix version). Frames are also kept in `frames_w5/` (168 PNGs, ~170 MB).
- **Script:** `bioluminescent-shore/blender/serious/wave5.py` (backups: `wave5_tall_splash_backup.py`, `wave5_fine_spray_backup.py`; earlier videos `wave2.mp4`, `wave3.mp4`, `wave5_before_pullback_fix.mp4`).
- **Moments in the clip** (read from the frames): calm sea until ~0.5 s · wave rises 0.5–1.5 s · curls with turquoise light inside 1.5–2.8 s · crashes and throws spray ~2.85 s · foam sheet washes up the sand 3–4.5 s · drains back 4.5–5.3 s · foam outlines fade 5.3–7 s. The clip ends on a calm sea that matches its start, so a cross-fade between the last 0.6 s and the first frames loops cleanly.

### Known visual issues in wave5.mp4
1. A pale glowing ball at the far end of the wave from ~3.75 to 5.25 s, fading by 6 s.
2. A short bright patch that stays still at the far end of the shoreline around 4–5 s.
3. The broken wave (3–4.5 s) is very bright and even; the adapter deliberately adds **less** music light to the brightest pixels so this does not blow out to white.
4. No splash near the camera; all the spray is mid-distance.
5. The clip is 7 s, so a calm "idle" is only the first 0.5 s. The prototype loops that half second slowly (0.45× speed) with a cross-fade for the idle sea.

## Prototype: `bioluminescent-shore/music-wave-preview.html`

Reversible, silent, self-contained. Loads `blender/serious/wave5.mp4` by a relative URL, so it must be served from the project folder (`python3 -m http.server 8792 --bind 127.0.0.1`, then `/bioluminescent-shore/music-wave-preview.html`). Add `?embed=1` to hide the test panel, the same way `aurora.html` does.

`window.musicWave` exposes:

| Call | What it does |
| --- | --- |
| `reset()` | Calm sea at 0 s, all added light cleared |
| `frame(F, time)` | One frame of music (see table below). Call at the app's frame rate while music plays |
| `setPlaying(bool)` | Pauses or resumes the video and the light clock |
| `snapshot()` | Returns a canvas copy of the current picture (for Save) |
| `destroy()` | Stops playback, releases both video elements and the WebGL context, sets `window.musicWave = null` |
| `setFilter(name)` (optional) | `'notes' \| 'pitch' \| 'rhythm' \| 'harmony'`; defaults to notes. The app can call this when the Filter control changes |
| `debug()` (optional) | State, video time, playback rate, number of sparkle bursts |

Suggested adapter in the app, mirroring `AURORA`: an iframe at `../../bioluminescent-shore/music-wave-preview.html?embed=1`, read `iframe.contentWindow.musicWave` on load, call `setPlaying(playingMusic())` from `resetLights`, forward `frame(F, time)` from the loop, and call `setFilter(trigger)` when the trigger changes. `keeps()` should treat it like Aurora (it never ends as a still image). Please give the `<video>` inside the iframe the same autoplay allowance as Aurora's audio: the page starts playback only from `setPlaying(true)`, which the app calls after the user's click.

## Music-to-wave table

Inputs are the app's `F` object: `energy`, `bass`, `bright`, `onset`, `flux`, `notes[{midi, pc, s, v}]`.

| Music | Wave reaction | Notes | Pitch | Rhythm | Harmony |
| --- | --- | --- | --- | --- | --- |
| `energy` (whole mix) | Glow of all lit water (`uGlow`); break speed 0.75×–1.3× | ✓ | ✓ | ✓ | ✓ |
| `energy` accumulating + `onset` | Fills a "charge"; when full, a wave rolls in from the calm sea | ✓ | ✓ | — | ✓ |
| `onset` with `flux > .3` | Starts a wave immediately (or restarts after the drain) | — | — | ✓ | — |
| `onset` while the wave is rising (0.5–2.85 s) | Pushes the break sooner: playback rate up to 2.1× | ✓ | ✓ | ✓ (stronger) | ✓ |
| `onset`, scaled by `flux` | Short flash on lit water, strongest at the crash | ✓ | ✓ | ✓ | ✓ |
| `bass` | Extra foam brightness on the near beach (`uFoam`) | ✓ | ✓ | ✓ | ✓ |
| `bright` | Twinkle speed and sparkle density | ✓ | ✓ | ✓ | ✓ |
| `notes[0].pc` | Tint of the glowing water, kept inside deep blue → turquoise (hue 230–168°, circle of fifths) | ✓ | — | — | — |
| `notes[0].midi` | Tint low → high as blue → cyan | — | ✓ | — | — |
| `notes[0].v` (major/minor estimate) | Major chords lean turquoise-green, minor chords lean deep blue | — | — | — | ✓ |
| New note / attack (`notes`, up to 4; 3 for Harmony; 1 for Rhythm) | A soft sparkle burst on lit water. Low notes near and right, high notes far along the wave; colour from pc (Notes/Harmony) or pitch (Pitch) | ✓ | ✓ | ✓ | ✓ |

Every added light is multiplied by a mask of pixels that already glow in the render, so nothing appears in the dark sky or on dry sand. Colours never leave blue–cyan–turquoise.

## Verification done and limits

- `node --check` passes on the page script.
- Loaded in the visible desktop-app browser from the local server with no console errors. `window.musicWave` exposes reset, frame, setPlaying, snapshot, setFilter, debug and destroy.
- **Synthetic music only** (the page's built-in test chords and beats); no real audio has been fed in. Checked all four filters: Notes and Harmony waves start when the charge fills and loop back to the calm sea with the cross-fade; Rhythm starts a wave on the first strong beat (video at 3.75 s after 2.6 s, rate 1.6×); Pitch tints toward cyan.
- `setPlaying(false)` holds the video time; `snapshot()` returns a 2048×1536 canvas with picture data; `reset()` returns to calm at 0 s; `destroy()` removes both videos and nulls the API. `?embed=1` hides the panel.
- Playback is silent: the videos are muted and carry no audio track.
- Not tested: inside the app's iframe, on phones, with live tab audio, or over a long session (memory of two decoded videos). `snapshot()` must be called in the same task as a draw, which it does itself, but it has not been tested through the app's Save button.
- Seeking a `<video>` to 0 for the cross-fade can stutter on slow machines; the frames_w5 PNGs are available if a sprite-sheet player is ever preferred.

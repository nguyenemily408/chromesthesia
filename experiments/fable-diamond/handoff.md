# Diamond experiment — handoff

November 11, 2026 · Claude (Opus 5.5) · side session. This is not the Fable model; the owner may still want Fable to try a version.

**File:** `experiments/fable-diamond/diamond.html`. It works on its own, with no libraries and no internet needed. To open it, serve the folder (for example `python3 -m http.server 8771` inside `experiments/fable-diamond`) and visit `http://127.0.0.1:8771/diamond.html`.

Nothing was committed. `index.html` and `experiments/fable-ink/` were not touched.

## What it is

A cut diamond floats on a pale studio background and turns slowly. When music plays, the facets light up in the note colours.

- **Shape.** A brilliant-style cut with 12 sections around the stone: a flat table on top, star, kite and upper-girdle facets on the crown, a thin girdle, then lower-girdle and main facets running down to the point. That makes 109 facets.
- **Notes to facets.** Go round the stone like a clock face. Each of the 12 wedges belongs to one note, and neighbouring wedges are a fifth apart, so the colours run smoothly round the colour wheel. The colour rule is the same as the main app: hue = ((note × 7) mod 12) × 30.
- **Table.** Looking down through the table you see the wedges on the far side of the stone, so the table shows the colours of the opposite wedges as a ring of slices.
- **Brightness.** When a note is heard, its facets brighten, and louder notes make them brighter. The colour fades over about a third of a second after the note stops. This is the same rule as the existing crystal style.
- **Sparkle ("fire").** On each sudden attack (onset), 10–45% of the facets throw a short burst of rainbow colour, and star-shaped glints appear on the facets that face you.
- **Bass glow.** Low frequencies light a soft pool of colour under the stone. It takes the colour of the lowest clearly heard note.
- **Trigger: Notes (default), with Whole Song as an option.** A small panel at the top left says "Driven by Notes" and that pitches are estimated from the sound. Its second button, Whole Song, makes the facet colours travel once through the spectrum from the start to the end of the song: all wedges stay near one moving hue, notes still set how brightly each wedge shines, and overall loudness keeps the whole stone softly lit. The bass glow follows the same moving hue. The stone keeps rotating at all times.
- **Controls.** One fixed bottom bar holds Play/Pause, a seek slider, the time, the track name, Upload song and Snapshot. No sound plays until Play is clicked. Snapshot saves a PNG of the artwork only (no bar) and doesn't pause the music. The space bar also plays and pauses.
- **Reused code.** `ensureAC`, `analyse` and the 18-second demo builder are copied unchanged from `experiments/fable-ink/three-styles-next.html`.

## How it was checked

Testing was done in the Claude desktop app's built-in browser on an Apple M2 (Chrome, WebGL through Metal). The browser pane was hidden during testing, so the screenshots were taken through the browser tools. During playback I set the output volume to zero from the test script. The analysis still received the full sound; nothing came out of the speakers.

| Check | Input | Result |
|---|---|---|
| JavaScript syntax (`node --check` on the script) | — | Pass |
| No console errors on load and during playback | — | None seen |
| Demo plays to the end | Real playback of the 18-second demo | Notes found: A C E F G B D, which are exactly the demo chords Am, F, C and G. At 0:04 the A facets were lit (yellow-green) and the F facets magenta. The button reads Replay at the end. |
| Uploaded MP3 | Beethoven Symphony No. 5, first movement (8:20). The file was handed to the real Upload input in code, because the system file picker can't be driven. | The name and 8:20 length appeared. Seeking to 20% jumped to 1:40. Over 8 seconds of playback the strongest colours were D♯, A♯, G, F, D and C, which fits the piece's C minor. The bass glow reached 0.45. Only 2 onsets fired in those 8 seconds. |
| Snapshot during playback | Beethoven | The PNG was 2048×1536 (the canvas only) and the music kept playing. The download link was caught in code instead of saving a real file into Downloads. |
| Bar never moves | Play vs Pause states | The position and size of every bar item were identical |
| Phone width 375 px | Simulated phone screen | Everything fits, with no sideways scroll. The track name is hidden at this width. |
| Whole Song mode | Beethoven, real playback (muted), seeking to 0:33 and 5:33 | Warm red-yellow at 0:33, violet-blue at 5:33. The stone kept rotating. Switching back to Notes restores the note text. The bottom bar stayed 56 px. |
| Colours, sparkle and glow in isolation | **Synthetic note data** fed straight into the renderer (A–C–E, G–B–D, forced onsets) | Each note lights its own wedges, the burst appears, and the glow appears |

**Frame rate.**
- On normal screen playback the page ran at 60 fps (median frame 16.7 ms).
- With the pane hidden, the browser slowed every page to about 30–43 fps, including when nothing was playing. That's the hidden pane, not the diamond.
- Drawing time measured directly: 5.3 ms per frame at 2048×1536 with sparkles on and every facet lit, timed with a forced wait for the graphics card. That leaves a lot of room under the 16.7 ms that 60 fps allows.
- Not measured: Intel or older laptops, and real phones.

**Screenshots in this folder:**
- `diamond-beethoven-1m48.jpg`: the uploaded song at 1:48
- `diamond-demo-0m04.jpg`: the demo at 0:04, with A and F lit
- `diamond-phone-width.jpg`: the page at phone width, silent (taken before the trigger panel was added)
- `diamond-whole-song-0m33.jpg` and `diamond-whole-song-5m33.jpg`: Whole Song mode early and late in Beethoven

## Differences from a real diamond

- **No real ray tracing.** The light path is faked. Each pixel bends light into the stone, bounces it off two imagined back facets chosen by angle, and looks up a made-up studio surrounding (bright ceiling and strip lights, dark floor, dark camera in front). The patterns look like a diamond, but they aren't physically correct.
- **12 sections instead of 8.** A real round brilliant has 8-fold symmetry and 57 or 58 facets. This one uses 12 sections (109 facets) so that each note gets its own wedge. The proportions (table 56%, shallow crown, deep pavilion) are only roughly a real cut.
- **Fire is exaggerated and timed to the music.** Real fire depends on the light and the angle. Here a colour split is drawn on chosen facets at each onset.
- **No caustics.** The glow under the stone is a painted soft pool, not real focused light.
- **Hard facet edges.** Faint grey lines are drawn on purpose so the cut reads against the pale background.
- **Opaque rendering.** The stone is drawn as a solid object with a fake inside, so you can't see the background through it.

## Known gaps and next steps

- **Orchestral sparkles are rare.** On orchestral music the existing onset detector fires rarely (2 in 8 seconds of Beethoven), so sparkles are uncommon. Pop or percussive music wasn't tested. The onset threshold could be made more sensitive, but only for this page.
- **Quiet demo bass.** The demo's bass is soft, so its glow stays weak (peak 0.16). The glow shows clearly on Beethoven.
- **Not checked:** Safari and Firefox, recovery after losing the graphics context, a real file chosen through the system picker, a real Snapshot file saved to Downloads, and long playback over a full song.
- **Not linked anywhere.** Codex decides whether and how it joins the main app.
- **Untested on a phone:** the trigger panel wraps onto two lines on narrow screens. That wasn't rechecked at phone width after the panel was added.

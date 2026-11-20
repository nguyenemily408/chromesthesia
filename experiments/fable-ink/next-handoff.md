# Ink next and three-style comparison — handoff

Historical experiment report. For the current full-screen app and latest choices, start with [the project handover](../../HANDOFF.md).

November 11, 2026. Written by Fable 5.2 (Claude). Everything here is local. Nothing was published, committed or pushed. `index.html` and `ink.html` were not edited.

## Files

- `ink-next.html` — one visual iteration of `ink.html`. Add `?look=glaze` for an optional thinner, see-through look.
- `three-styles.html` — Layered Watercolor, Ink Clouds and Musical Shapes, selectable on the same track.
- `ink-next-fade.jpg`, `ink-next-painting.jpg`, `ink-next-glaze-option.jpg` — ink screenshots.
- `three-styles-watercolor.jpg`, `three-styles-shapes.jpg`, `three-styles-ink.jpg` — one per style at about 0:13 of the built-in demo.

Preview: run `python3 -m http.server 8792 --bind 127.0.0.1` in the project folder, then open
`http://127.0.0.1:8792/experiments/fable-ink/ink-next.html` or `.../three-styles.html`.

## Ink changes (in both files)

- Each cloud is now a short series of puffs on a small spiral. Each puff inflates on its own and presses on the others, so a cloud reads as a cluster of rounded, domed folds.
- New clouds take the emptiest of a few candidate spots; pitch still nudges the height.
- Fade with music: clouds last about five times longer and melt from their thin edges inward. After the track ends they fade out fully.
- Build a painting: unchanged behavior. Ink is kept, the frame holds at the end, Save painting appears.
- Note colours are the same twelve, slightly more saturated.

## Three-style page

- One style switch (three choices). The two ink behaviors appear only for Ink Clouds.
- Changing style or behavior keeps the chosen track and returns it to the beginning.
- Layered Watercolor: the watercolor renderer from `index.html` on lighter paper, with the slow cover-up wash removed so marks stay, crisper dried edges, fewer overlapping washes and a wider vertical spread. Holds at the end and offers Save painting.
- Musical Shapes: a new light-background renderer (the old Shapes renderer was dark and accumulating). Each detected event places a ring with a centre dot for the strongest note, soft discs for the others and a vertical tick for a fourth or very high note. Colour from the note, height from pitch, size from strength. A playhead walks left to right every 9 seconds and a thin line joins the leading notes. Forms fade and spread over 7 to 9 seconds.
- Sound stays off until Play is pressed.

## Tested

Built-in browser of the Claude desktop app, 1280 × 720, built-in 18-second demo only, muted with the Mute button before Play. This was real playback through the page's own analysis, not synthetic data.

- `ink-next.html`: Fade with music and Build a painting played to the end. Fade covered the canvas by 0:13 and dissolved after the end. Painting held still and showed Save painting. The glaze option was played once in painting mode.
- `three-styles.html`: all three styles played on the same demo. Watercolor held at the end, showed Save painting and encoded a PNG in memory. Shapes had zero forms left 15 seconds after the end and no Save button. Switching to Ink Clouds showed the two behaviors and reset the clock to 0:00 with the same track.
- JavaScript syntax check passed for both files. No page errors.

## Not tested

- No Beethoven, Bach or any other real recording. There is no audio file in the project folder.
- Save painting was not clicked, so no PNG file was actually downloaded. Only in-memory PNG encoding was checked.
- Choose a song, Use demo, Start over, Pause/Resume and window resize.
- Build a painting inside `three-styles.html` (it is the same code as `ink-next.html`).
- Long songs. Ink painting and watercolor may fill or muddy the whole canvas over several minutes.
- Phones, Safari, Firefox, slower graphics hardware.

## Known weak points

- Watercolor is the least close to its reference. Washes are soft blobs with thin outlines; it lacks the reference's granulated, feathered edges and rainbow sweep.
- Shapes cluster where the playhead is and the built-in demo only reaches a few notes, so the palette looks narrow on this track.
- Ink remains a 2D approximation of real ink. Folds are rounded lobes, not the reference photograph's deep curls.
- `window.__inkLab` is a test hook; remove it before publishing.

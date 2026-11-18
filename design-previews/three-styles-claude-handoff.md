# The Sound of Color · Three visual styles

The user wants to keep the three original mockup directions in the project and try them as working visuals. Ink clouds were selected for the first prototype. Layered Watercolor and Musical Shapes are still design directions. The existing app has earlier Watercolor and Shapes renderers that provide starting code.

Build a local comparison that plays the same track in all three styles. Use the existing music analysis to estimate notes and measure their strength. Keep the sound off until the listener clicks Play, and keep the song available when changing styles so the listener can compare the same passage.

| Style | How it should look and respond | Starting point |
| --- | --- | --- |
| Layered Watercolor | Soft, translucent washes with pigment settling into textured edges. Notes add colored marks that overlap and build into a composition. Let the marks stay through the song and hold the final painting for PNG export. | Watercolor renderer in index.html. See 05-whole-song.png for color layering and composition. |
| Ink Clouds | Thick clouds billow, curl, and slowly spread in white water. Keep both behaviors already prototyped. Fade with music lets older clouds dissolve. Build a painting preserves the color until the song ends and offers a PNG. | ink.html and the current experiments/fable-ink/ink-next.html iteration. See ink-fade.jpg, ink-painting.jpg, and the original ink-reference.png in experiments/fable-ink/. |
| Musical Shapes | Clear geometric forms arrive with musical attacks. Assign color from estimated notes, height from pitch, and scale from strength. Let forms recede so the next phrase is easy to follow. | Shapes renderer in index.html. See 01-notes.png and 02-pitch.png for note colors and placement. |

Use any original three-style mockup images if available in the current conversation. The named image files are supporting references. Keep music response tied to the audio that is playing. The current analysis estimates pitches and cannot isolate instruments or establish chord names reliably.

Put the first implementation in a separate local preview under experiments/fable-ink/. Show a screenshot of each style at comparable moments using the same built-in track. Report which playback and export behaviors you tested. Share the local preview for review before publishing.

## Five triggers to test

Add a second selector for what drives the artwork, independent of the visual style. The same track should be reusable when switching triggers. Start with combinations that make the differences easy to see.

| Trigger | What to test |
| --- | --- |
| Notes | Each estimated note class adds a color. Play a known melody and a few simultaneous tones to check the palette. |
| Pitch | Lower pitches appear lower on the canvas, and higher pitches appear higher. Use an ascending and descending passage to check placement. |
| Instruments | Assign a distinct color per instrument using a demo with known, separately generated instrument parts. Label this as a demo when using known parts. For a mixed song file, be clear if instrument identification is unavailable. |
| Harmony | Use known chords in the demo to check whether the palette changes as each chord changes. Only show chord names for uploaded audio if the implementation can estimate them with reasonable confidence and labels them as estimates. |
| Whole Song | Build up one composition across the piece, preserve earlier marks, hold the final image and verify PNG export. |

Read 01-notes.png through 05-whole-song.png for the trigger concepts. Aim for a small, functional comparison. If one visual style is the clearest way to test a trigger, use it as the suggested default and keep the other style options only where they behave meaningfully.

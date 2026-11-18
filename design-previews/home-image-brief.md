# Home page image — brief for Codex

November 11, 2026. Written by Claude for Codex. Emily does not like the computer-drawn watercolor blobs behind the welcome screen and wants a generated image there instead. Codex generates the image; the page already loads it.

## Where it shows

The welcome screen of `experiments/fable-ink/three-styles-full.html`: the full-screen view with "The Sound of Color", "Press play. The song paints the screen.", the Play button, the five triggers and the Style row. The image fills the whole screen behind that text. It disappears as soon as Play is pressed, when the music starts painting.

## What it should look like

- One finished watercolor painting of music as colour, in the spirit of `reference-whole-song.png` and `05-whole-song.png`: soft layered washes, real pigment texture, feathered and dried edges, granulation, cold-press paper.
- The full rainbow, flowing left to right like a song: cyan and blue, green, yellow, orange, red, magenta, violet.
- **A calm, light centre.** The title and buttons sit in the middle third, so the middle should be mostly pale paper with only faint colour. The colour gathers toward the edges and corners.
- Light overall: warm off-white paper (around `#faf8f5`) is the main tone, so dark text stays easy to read.
- No text, letters, numbers, music notes, instruments, people, frames, borders, interface elements, signatures or watermarks.
- No visible edge of the paper and no shadow; the painting runs off every side.

## Files

Put them here (create the folder):

```
chromesthesia-codex/
  assets/
    home/
      home-wide.jpg       2560 × 1440, for computers and tablets held sideways
      home-tall.jpg       1440 × 2560, for phones held upright
```

- JPEG, quality around 82. Each under 600 KB.
- Same painting style in both. The tall one is its own composition, not a crop of the wide one: colour top and bottom, calm middle.
- Only `home-wide.jpg` is required. Without `home-tall.jpg`, phones use the wide one, cropped to fit.

## Suggested prompt

> A loose abstract watercolor painting on warm white cold-press paper, the colour of music flowing from left to right through the full rainbow: cyan, blue, green, yellow, orange, red, magenta and violet. Soft layered translucent washes with feathered wet edges, a few crisp dried edges, gentle granulation and blooms. The centre is open, pale paper with only faint colour, the colour gathering toward the edges and corners. Bright, airy, calm. Flat scan, no paper edge, no shadow, no text, no objects, no people, no frame.

For the tall version add: "Vertical composition, colour gathered at the top and bottom, the middle open and pale."

Record the prompts in `design-previews/generation-prompts.json` as you did for the mockups.

## How to check

1. Serve the project folder: `python3 -m http.server 8792 --bind 127.0.0.1`
2. Open `http://127.0.0.1:8792/experiments/fable-ink/three-styles-full.html`
3. The image appears behind the title. Until the files exist, the page shows plain paper with a very faint colour glow at the edges.
4. Check that the title, the Play button and the small trigger text are all easy to read on top of it.

## Handback

Record the files in `AGENT-WORK.md` and tell Claude. Claude will check legibility, add a soft fade under the text if needed, and send Emily screenshots. Nothing is published until Emily approves.

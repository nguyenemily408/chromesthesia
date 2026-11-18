# Watercolor texture assets — brief for Codex

November 11, 2026. Written by Claude for Codex. Codex generates the images; Claude's watercolor renderer loads and paints with them.

## What these are for

The live Layered Watercolor style currently draws every wash with maths, so it looks like soft blobs with thin outlines. The reference (`reference-whole-song.png`, `05-whole-song.png`) has real watercolor texture: feathered and dried edges, blooms, granulation and paper grain.

The renderer will use your images as **stamps**. On every musical event it picks a stamp, tints it the note's colour, sizes it by loudness, places it by pitch, rotates it, and layers it over earlier washes. One grey stamp is reused in all twelve note colours, so **do not make coloured versions**.

## Where to put them

```
chromesthesia-codex/
  assets/
    watercolor/
      manifest.json
      wash-01.png … wash-16.png
      edge-01.png … edge-08.png
      grain-01.png … grain-04.png
      paper.jpg
```

The renderer reads `manifest.json` first and loads only what it lists, so you can ship fewer files at first and add more later without code changes.

`manifest.json`:

```json
{
  "version": 1,
  "washes": ["wash-01.png", "wash-02.png"],
  "edges": ["edge-01.png"],
  "grain": ["grain-01.png"],
  "paper": "paper.jpg"
}
```

Any list may be empty and `paper` may be omitted. The renderer then falls back to its current drawn version for that part.

## The one rule that matters: black on transparent, opacity = pigment

Every PNG is **black (RGB 0,0,0) on a fully transparent background**. The only thing that varies is opacity: fully opaque where pigment is thickest, partly see-through in thin glazes, fully transparent where there is no paint. The renderer throws away the black and keeps the opacity, then fills it with the note's colour.

Recommended way to make them:

1. Generate each image as **black or dark grey ink on plain white**, no paper texture, no colour.
2. Convert brightness to opacity with a script: `alpha = 255 − luminance`, then set every pixel's RGB to 0,0,0. White becomes fully transparent.
3. Optionally raise contrast so the faintest paper-white noise goes fully transparent (for example, alpha below 8 → 0).
4. Save as PNG. Grey-plus-alpha (PNG "LA") or RGBA both work.

## The four sets

### 1. Washes — `wash-01.png` to `wash-16.png` (most important)

- 512 × 512 pixels.
- One wash per file, centred, filling roughly 70–85% of the square.
- **At least 24 px of fully transparent margin on every side.** Nothing may touch the border, or the stamp shows a straight cut line.
- Variety across the set: round, oval, lobed, elongated, torn or feathered.
- Include in different files: wet feathered edges, crisp dried edges with a slightly darker rim, a few cauliflower backruns or blooms, and uneven thickness inside.
- Edges should mostly be soft and irregular, not perfect circles.

### 2. Dried edges — `edge-01.png` to `edge-08.png`

- 512 × 512, same margin rule.
- Only the **dark ring** that forms where a wash dried: an irregular outline 3–15 px wide, mostly transparent inside.
- Shapes should roughly match the outline of a typical wash, so they read as the same paint drying.

### 3. Granulation — `grain-01.png` to `grain-04.png`

- 512 × 512, **seamless tile** (the left edge continues into the right, the top into the bottom).
- Fine speckle and settling texture, opacity mostly 10–60%.
- No large shapes, just pigment grain.

### 4. Paper — `paper.jpg`

- 1024 × 1024, **seamless tile**, JPEG quality around 80.
- Cold-press watercolor paper, very light warm off-white (average near `#fbf8f2`), low contrast.
- This one is a normal colour photo-like image, not black on transparent.

## Limits

- Each PNG under 200 KB; `paper.jpg` under 300 KB; the whole folder under 4 MB.
- No colour (except paper), no text, no signatures, no watermarks, no frames, no visible paper edge or shadow.
- Keep the files in the project. Loading them from another website would block Save painting.

## Suggested prompt (washes)

> A single loose watercolor wash, black ink only, on a pure white background, centred with generous empty margin. Irregular organic shape with soft feathered edges on one side and a crisp dried edge with a slightly darker rim on the other. Uneven pigment density, subtle granulation, one small backrun bloom. Flat scan, no paper texture, no shadow, no colour, no text.

Vary the shape words per file: round pool / long sweeping stroke / three overlapping lobes / torn cloud / small splash. Record the prompts in `design-previews/generation-prompts.json` as you did for the mockups.

## How to check your files

1. Serve the project folder: `python3 -m http.server 8792 --bind 127.0.0.1`
2. Open `http://127.0.0.1:8792/experiments/fable-ink/three-styles-full.html`
3. Choose **Layered Watercolor** as the style. The small note under the description says how many textures loaded, for example "Watercolor textures: 16 washes, 8 edges, 4 grain, paper".
4. Press **Mute**, then **Play demo**.

If the note says "drawn washes (no texture files found)", the manifest was not found or could not be read.

Add `?stamps=test` to the address to see the stamp path with stand-in shapes the code draws itself. That checks the renderer, not the look.

## Handback

When the files are in place, record them in `AGENT-WORK.md` and tell Claude. Claude will tune sizes, layering and opacity against the reference and report back with screenshots. Nothing gets published until Emily approves.

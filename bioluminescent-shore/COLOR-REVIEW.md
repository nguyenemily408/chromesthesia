# Pitch colour in the bioluminescent wave — review

Claude, November 20. Advice only: no app code, no wave prototype, no renders were changed. Codex owns the edits.

## Why Pitch looks washed out today

1. **The tint is added on top of foam that is already near white.** In `music-wave-preview.html` the shader does `c = mix(c, uTint * lum * 1.25, uTintAmt * lit * .55)`, and `uGlow`, `uFoam` and `uFlash` then multiply the same pixels. The broken wave in `wave5.mp4` (3–4.5 s) is already at 80–95% brightness, so any colour pushed there clips to white. The eye reads "brighter", not "bluer" or "greener".
2. **The hue range is far too narrow.** Pitch only sweeps hue 232° → 168° (blue → turquoise). The app's legend promises violet → blue → cyan → green → yellow → orange → pink (`PITCH_HUES`). The picture and the key disagree, and a 64° sweep of a colour the scene already is cannot be seen.
3. **The tint is a global wash.** One colour over the whole lit area, with no spatial anchor, so a change of note moves everything a little and nothing noticeably.

Real water only takes colour in two ways: **light passing through it** (the translucent crest and the thin wash on the sand, which can be any colour of the light source) and **light reflected off foam** (foam is white; it only takes a colour cast, never a saturated colour). The first path is where saturated pitch colour can live without looking fake.

## Three ways to show pitch colour

### A. Coloured light inside the translucent crest (recommended)
Treat the bioluminescence inside the rising and curling wave as the light source and give *that* the pitch colour. In the render the inside-crest glow is the mid-brightness teal band on the wave face (lum roughly 0.25–0.65), not the white foam.
- Mask: `inside = smoothstep(.15, .45, lum) * (1 - smoothstep(.6, .9, lum))` — mid-tones only, foam excluded. Optionally multiply by a vertical band for the wave zone (uv.y 0.25–0.7) so sand and far sea stay unaffected.
- Colour: replace the mid-tone's own hue, don't add to it: `c = mix(c, pitchRGB * (lum / max(lum0, .001)) , amount * inside)` where the tint keeps the pixel's brightness and swaps chroma. Keep saturation ≤ 0.8 so it still reads as glowing water.
- Palette: use the app's `PITCH_HUES` directly so the key is true. Clamp lightness to 0.45–0.55; yellow/orange will look like sodium light in water, which is still plausible at night.
- Why it works: the crest is the one place the render is translucent and mid-bright, so a colour change there is both visible and physically believable (coloured plankton light shining through water).
- Cost: one extra mask; no new textures.

### B. Coloured foam edges and lace (accent only)
Give the *edges* of the foam a colour cast while the foam body stays white: `edge = bright * (1 - smoothstep(.85, 1., lum))` picks the rim between white foam and dark water, which is where real foam shows the colour of the light under it.
- Apply at low strength (0.2–0.35), additive, and *reduce* the white (`c *= 1 - .25 * edge * amount`) before adding colour so the rim can change hue instead of clipping.
- Reads as a coloured outline on the lace on the sand and on the broken wave's front, which is a nice "pen line" effect for Pitch.
- Limit: foam cannot carry saturated yellow or pink convincingly; keep this as a secondary accent paired with A, or it will look like a colour filter on a photograph.

### C. Low / mid / high regions
Split the picture into three bands by pitch and only colour the band the current note belongs to: low notes = the near beach and wash-up (uv.y > .65), mid = the wave body (uv.y .35–.65), high = the far sea and the far end of the wave (uv.y < .35).
- Simple to explain to the viewer: "the bass lights the beach, the melody lights the wave, high notes light the horizon".
- Use the same inside-crest masking as A within each band so foam is still protected.
- Limit: the render's bands do not sit on clean horizontal lines (the wave runs diagonally), so a band split by uv.y alone will cut the wave; a diagonal split along the shoreline direction (`dot(uv, vec2(.5, .85))`) is closer. It also spends most of the picture dark most of the time, which makes the scene feel emptier for a single melody line.

## Recommendation

**Do A, with B as a light accent, and keep the bursts.** A puts the full legend palette where the water is translucent and mid-bright, so pitch changes are visible and the water still looks like water. B gives the foam lace a coloured rim without saturating the white. The existing note bursts already position low notes near/right and high notes far/left, which gives C's spatial reading for free.

Concrete settings to start from (Codex to tune on the real video):
- Pitch tint strength 0.6–0.8 on `inside`, 0.25 on `edge`, 0 on `bright` foam.
- Smooth the tint target with a 0.25 s time constant, not 0.1 per frame, so vibrato does not flicker.
- Cap the final colour at `min(c, 1)` and lower `uGlow`/`uFlash` on `bright` pixels by 70%, as the current shader already does, otherwise A's colour still clips at the crash.

## Shader limits to expect

- **No real transparency or scattering.** The video is flat pixels; the "inside the crest" effect is a brightness-band mask, not a volume. Colour will also catch any other mid-bright pixel (the far shoulder of the wave, the sheen on wet sand). Guard with a region mask if that is distracting.
- **Clipping is baked in.** Pixels the render already stores at ~1.0 cannot be recoloured; only darkened then tinted, which costs some of the render's sparkle. Prefer colouring the mid-tones to fighting the highlights.
- **sRGB video, not linear light.** Additive colour in sRGB desaturates faster than real light would; keep additive terms small and use `mix` (replacement) for the main tint.
- **Hue only, never brightness, for pitch.** Brightness is already spent on energy; if pitch also changes brightness the two become indistinguishable.
- **Colour on foam will always look like a filter.** Keep foam white; let the colour come from under it.
- **Legend must match the shader.** Whatever palette is applied, build the key from the same array (`PITCH_HUES`) so the bar and the picture agree.

Verification I did: read `music-wave-preview.html` and the Tide adapter in `three-styles-full.html`, and the frames of `wave5.mp4` for where the mid-tone band sits. I did not run the app with music and did not test any of the suggested masks; the numbers above are starting points.

## Update, November 20 (after Codex applied option A)

Emily: the coloured wave is **too much**. Six subtler options were mocked up as stills from `wave5.mp4` frames 54 (curl) and 96 (wash-up): `color-options-curl.jpg` and `color-options-wash.jpg` in this folder. Rows: 1 current crest + rim (strong), 2 crest only at 30%, 3 foam rim + sand lace only, 4 sparkle specks only, 5 far-water glow, 6 wet-sand reflection. Claude's pick is 4 (sparkle only), with 3 as the alternative. **Codex: please hold Tide colour changes until Emily chooses; her choice will be recorded here.**

Masks used for the mockups (same lum = max(g,b) as the shader): speck = smoothstep(.08,.3, lum - blur3px(lum)); edge = bright * (1 - smoothstep(.85,1,lum)); tint replaces hue and keeps brightness (mix toward colour * lum * 1.1).

### Emily's choice (November 20): option 3, foam rim + sand lace only

Codex, please replace the crest tint with this. The wave body and the white foam stay as rendered; only the thin edge between foam and dark water takes the pitch colour, which also picks up the lace lines on the sand.

- `lum = max(c.g, c.b)`; `bright = smoothstep(.35, .85, lum)`; `edge = bright * (1. - smoothstep(.85, 1., lum))`.
- Colour: `pitchRGB` from the app's `PITCH_HUES` (hsl, saturation .95, lightness .5), smoothed with about a 0.25 s time constant.
- Apply: first `c += pitchRGB * edge * .18` (a little light on the rim), then `c = mix(c, pitchRGB * lum * 1.1, .35 * edge)` so the rim's hue changes rather than clipping. No tint on `inside` (the crest band) and none on `bright` foam.
- Keep the note sparkle bursts, the `min(c, 1)` cap and the 70% reduction of glow/flash on bright pixels.
- Expected look: at a glance the water is the same blue; the lace outlines on the sand and the foam edges carry the note colour (see row 3 of `color-options-curl.jpg` and `color-options-wash.jpg`).

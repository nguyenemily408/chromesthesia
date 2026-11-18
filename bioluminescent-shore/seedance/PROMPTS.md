# Seedance 2.0 — bioluminescent shore

## Pictures to upload
- `shore_16x9.jpg`: your photo cropped to video shape (16:9). Use this one first.
- `shore_full.jpg`: the full wide photo, if the site offers 21:9.

## Settings
- Mode: **Image to video**
- Start frame: `shore_16x9.jpg`
- End frame (if the site offers it): the **same picture** again, so the clip loops seamlessly
- Length: **10 seconds**. Try 5 seconds first if each try costs money.
- Resolution: 720p for tests, 1080p for the keeper
- Camera: fixed / static, if the site has a camera setting
- Sound: off (or keep it; we can remove it)

## Prompt A — closest to your video (try first)
```
Static locked-off camera on a beach at night. A gentle shore-break wave rolls in, its lip pitches forward and curls over into a hollow tube, then collapses into foam. The foam sheet rushes up the wet sand with a lacy white-blue edge, then slides back out to sea as the next wave rises behind it. Bioluminescent plankton glow where the water is disturbed: tiny cyan and electric-blue sparkles on the wave face and in the foam, bright turquoise light inside the curl. Realistic water physics, natural wave speed, no camera movement, dark night sky, no people.
```

## Prompt B — if A moves too much or too fast
```
Fixed camera. Slow, calm ocean waves at night with bioluminescent plankton. The wave curls and breaks gently, sparkling cyan and blue where it churns, glowing turquoise inside the curl. Foam lace washes up the dark sand and recedes. Real-time speed, subtle and realistic, the scene stays like the photo.
```

## Things to avoid (paste into a "negative prompt" box if there is one)
```
camera shake, zoom, pan, slow motion, people, boats, text, watermark, daylight, sun, flying sparks, floating particles in the air, fireworks, cartoon
```

## What to check in each result
1. Does the wave curl into a hollow before it crashes?
2. Does the foam run up the sand and slide back, like the YouTube video?
3. Does the glow stay **on the water**, not floating in the air?
4. Does the end match the start (seamless loop)?

Save any keeper into this folder (e.g. `seedance_try1.mp4`) and Claude can trim it, loop it and add it to the compare page.

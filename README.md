# The Sound of Color

For the current full-screen preview with Living Watercolor and Aurora over Norway, run this from the project folder:

```sh
python3 -m http.server 8792 --bind 127.0.0.1
```

Open [the local web preview](http://127.0.0.1:8792/experiments/fable-ink/three-styles-full.html), then choose **Play demo** or **Upload MP3**. The style and filter controls appear when the canvas opens. Keep the project folders together so the preview can find its files.

In desktop Chrome or Edge, choose **Find a song** on the welcome screen or under **More**. Search for a song on YouTube or Spotify, paste a link, or use a tab you already have open. Play music in the browser tab, return to The Sound of Color, click **Share tab audio**, and select the playing tab with **Also share tab audio** enabled. If the service or browser does not share the audio, use **Upload MP3**. **Stop listening** ends the share. On phones and tablets, the music choices are **Play demo** and **Upload MP3**.

The search buttons open each service's own search page. Chrome shares the selected tab's audio with the app after the listener grants permission. Web Audio measures frequency peaks and sudden changes in energy, then the selected Notes, Pitch, Rhythm, or Harmony filter sends those measurements to the artwork. Note and chord detection are estimates from the complete audio mix. The music continues playing in its original tab.

SoundCloud is also available under **Find a song**, with its embedded player in the bottom playback bar. Search opens SoundCloud's results. Paste a full SoundCloud track or playlist link to load its player inside The Sound of Color. Press Play in the embedded player, then **Share this tab’s audio** and select The Sound of Color with tab audio enabled. **Remove player** stops and removes the player. This desktop flow requires Chrome's sharing approval each time. On November 20, live SoundCloud audio shared from this same tab reached Living Watercolor and painted while the song played. Player removal and paused SoundCloud with Aurora were also checked. The sharing picker is still required.

Live YouTube and Spotify tab audio were verified in desktop Chrome on November 18. This flow uses browser tab sharing. Official service APIs provide search and playback controls but do not expose the audio samples used by this visualizer. Spotify's [developer policy](https://developer.spotify.com/policy) restricts content analysis and synchronization with visuals, and YouTube's [developer policies](https://developers.google.com/youtube/terms/developer-policies) restrict isolating audio. Public integration requires a separate review of those terms.

| Files | What they provide |
| --- | --- |
| `experiments/fable-ink/three-styles-full.html` and `concept-styles.js` | The preview and its shared visual styles |
| `living-watercolor/watercolor.html` | Living Watercolor |
| `experiments/aurora-norway/aurora.html` and `photos/*.png` in the same Aurora folder | Aurora over Norway and its five backgrounds |
| `assets/home/home-wide.jpg` and `assets/home/home-tall.jpg` | The welcome artwork |

The original visualizer is in `index.html`. It starts with clear water in **Ink in Water**.

- Choose **Drop ink** to see cyan and violet drops fall, curl, and mix. Click or tap the water to place a drop yourself.
- Choose **Play the demo** to let the music release new drops. You can also open or drag in a music file.
- For tab audio, use **Listen to a tab** in Chrome or Edge and turn on **Also share tab audio**.
- Choose **Reset ink** for clear water or **Save painting** to download the current frame.

The browser calculates how the water moves and carries the colors on each frame. The ink spreads from where each drop lands. The music controls the timing, color, and strength of new drops.

All nine styles from the original [Chromesthesia](https://github.com/nguyenemily408/chromesthesia) are available from the menu and keys 1–9.

## Agent collaboration

See [AGENT-WORK.md](AGENT-WORK.md) for who is working on each part, completed work, testing results, and remaining steps. [AGENTS.md](AGENTS.md) gives every agent the same ownership and handoff rules. Claude’s renderer details are in [claude-handoff.md](claude-handoff.md).

## Creator Lab

Choose **Creator Lab** in the app’s music panel to open the LottieFiles demo. Claude generated the teal pulse through Creator MCP and exported [creator-lab-animation.json](creator-lab-animation.json). Use Pause, Restart, and the speed buttons to explore its two-second loop.

Serve this folder over HTTP so the player can load its JSON file. For example, run `python3 -m http.server 8766 --bind 127.0.0.1` in this folder, then open `http://127.0.0.1:8766/creator-lab.html`. The demo loads its Lottie player from a CDN and its fonts from Google Fonts, so those resources need an internet connection.

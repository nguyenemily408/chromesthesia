# The Sound of Color

For the current full-screen preview with Living Watercolor and Aurora over Norway, run this from the project folder:

```sh
python3 -m http.server 8792 --bind 127.0.0.1
```

Open [the local web preview](http://127.0.0.1:8792/experiments/fable-ink/three-styles-full.html), then choose **Play demo** or **Upload MP3**. The style and filter controls appear when the canvas opens. Keep the project folders together so the preview can find its files.

In desktop Chrome or Edge, choose **Use YouTube link** on the welcome screen or **Play from YouTube** under **More**. Paste a YouTube video link, open it and press play. Return to The Sound of Color, click **Share tab audio**, choose the YouTube tab, and turn on **Also share tab audio**. Manage the song in YouTube. **Stop listening** ends the share. On phones and tablets, the music choices are **Play demo** and **Upload MP3**.

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

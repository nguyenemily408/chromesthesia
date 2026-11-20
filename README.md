# The Sound of Color

Start with [HANDOFF.md](HANDOFF.md) for the current project state, Emily's latest choices, what has been tested, and remaining work. Older experiment handoffs contain superseded choices.

For the current full-screen preview with Living Watercolor and Aurora over Norway, run this from the project folder:

```sh
python3 -m http.server 8792 --bind 127.0.0.1
```

Open [the local web preview](http://127.0.0.1:8792/experiments/fable-ink/three-styles-full.html), then choose **Play demo** or **Upload MP3**. The **Art style** and **Follows** controls appear when the canvas opens and keep their selections independently. **Play demo** uses Vivaldi’s *Winter*; the page stays silent until Play. Living Watercolor following Rhythm uses the gold-line reference painting; Notes, Pitch and Harmony keep their audio-driven painting. These changes are live at [soundofcolor.vercel.app](https://soundofcolor.vercel.app/); see HANDOFF.md for verification and deployment details. Recording credits: [assets/audio/CREDITS.md](assets/audio/CREDITS.md). Keep the project folders together so the preview can find its files.

On desktop, choose **Find a song** on the welcome screen or under **More**, then choose a service. Both entry points use the same steps. For Spotify, copy the song/album/playlist link using Spotify’s **Share** menu; the Sound of Color website address is not a song link. An incorrect link now shows guidance directly below the box.

- **YouTube, SoundCloud and Spotify:** paste a supported song or playlist link and choose **Use link**. The service’s own player loads in the bottom bar and the app requests this tab’s audio. Choose the Sound of Color tab with audio sharing enabled. The player attempts to start; its own Play control remains available. Pause holds the artwork and its timer; Play resumes the same painting.
- **YouTube fallback:** if a video refuses embedding, use **Open on YouTube**, play there, then share that tab’s audio. Some music videos refuse the localhost preview but work from the public site.
- The free local extension remains an optional way to start visuals from a music tab.

Website tab sharing requires desktop Chrome or Edge and the browser’s permission. **Stop listening** ends the share. On phones and tablets, use **Play demo** or **Upload MP3**. After choosing a file, press **Play your song**.

Live YouTube and Spotify tab audio were verified in desktop Chrome on November 18. This flow uses browser tab sharing. Official service APIs provide search and playback controls but do not expose the audio samples used by this visualizer. Spotify's [developer policy](https://developer.spotify.com/policy) restricts content analysis and synchronization with visuals, and YouTube's [developer policies](https://developers.google.com/youtube/terms/developer-policies) restrict isolating audio. Public integration requires a separate review of those terms.

| Files | What they provide |
| --- | --- |
| `experiments/fable-ink/three-styles-full.html` and `concept-styles.js` | The preview and its shared visual styles |
| `living-watercolor/watercolor.html` | Living Watercolor |
| `experiments/aurora-norway/aurora.html` and `photos/*.png` in the same Aurora folder | Aurora over Norway and its five backgrounds |
| `assets/home/home-wide.jpg` and `assets/home/home-tall.jpg` | The welcome artwork |
| `bioluminescent-shore/music-wave-preview.html` and `blender/serious/wave5.mp4` in the same folder | Bioluminescent Tide: the rendered wave with music-driven timing, light and color |

## Local Chrome extension

See [chrome-extension/README.md](chrome-extension/README.md) for building and loading the free local extension. Play music in its browser tab, open the extension, and choose **Start visuals**. The extension opens the artwork and plays the captured music through that tab. Pause the song in its original tab for silence; **Stop listening** ends capture and restores normal audio output in the original tab.

The installed extension was checked with real YouTube music on November 20: Living Watercolor received audio, Tide loaded, and pausing/resuming YouTube removed/restored Chrome’s audio-playing indicator on the artwork. Spotify and SoundCloud have not yet been tested through this extension. The wave video has no audio track, and its players stay muted.

Tide’s latest Pitch choice is option 3 from Claude's color review: the main water stays blue while pitch colors trace foam rims and sand lace, using the same palette as the key. This replaces the rejected stronger crest tint for Pitch. Highlight compression and reduced sparkle preserve detail at the crash. The revision was checked with silent, synthetic low/high pitches; live music still needs a fresh check of the revised look. The wave’s shape remains the same seven-second Blender clip; music changes its timing, speed and light.

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

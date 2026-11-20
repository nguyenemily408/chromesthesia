# The Sound of Color Chrome extension

Build the extension from the current app with `python3 chrome-extension/build.py`.

To try it in desktop Chrome, open `chrome://extensions`, turn on Developer mode, choose **Load unpacked**, and select `chrome-extension/build/sound-of-color`.

Play a song in a browser tab. Click Chrome's Extensions button, choose The Sound of Color, and click **Start visuals**. The artwork opens in a new tab. Control the song in its original tab. **Stop listening** ends capture and restores the music tab's normal audio output.

The extension requests tabCapture, activeTab, and session storage. It reads audio from the tab where you start it, processes it locally, and includes the existing app and assets. A new listening session begins only after clicking Start visuals.

Chrome routes the captured music through the artwork tab so it remains audible. A speaker icon on The Sound of Color means it is playing that captured audio. Pause the song in the original music tab for silence. The bioluminescent wave video has no audio track, and the visual style adds no ocean sounds.

Tested November 20 with real YouTube audio: the extension opened the app, Living Watercolor painted, Tide loaded, and pausing/resuming YouTube removed/restored Chrome’s audio-playing indicator. The updated Tide palette was checked separately with silent synthetic pitches. Spotify and SoundCloud extension capture, and prolonged sessions, remain unchecked.

Local loading is free. Publishing to the Chrome Web Store requires Google's developer registration and store review.

For Spotify, use **Find a song → Spotify → Open Spotify in a new tab**. Play music in the Spotify tab and use the extension’s **Start visuals** button there. YouTube and SoundCloud have their own link fields in the site's chooser.

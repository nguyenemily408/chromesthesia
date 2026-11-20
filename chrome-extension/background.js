const playerPath = 'app/experiments/fable-ink/three-styles-full.html';

async function startVisuals() {
  const [source] = await chrome.tabs.query({active: true, currentWindow: true});
  if (!source?.id || !/^https?:/.test(source.url || '')) {
    return {error: 'Open Spotify, YouTube or SoundCloud in a browser tab, then start the visuals there.'};
  }
  const streamId = await chrome.tabCapture.getMediaStreamId({targetTabId: source.id});
  const viewer = await chrome.tabs.create({url: 'about:blank', active: false});
  try {
    await chrome.storage.session.set({
      ['capture-' + viewer.id]: {streamId, title: source.title || 'Music tab'}
    });
    await chrome.tabs.update(viewer.id, {
      url: chrome.runtime.getURL(playerPath),
      active: true
    });
    return {ok: true};
  } catch (error) {
    await chrome.storage.session.remove('capture-' + viewer.id);
    await chrome.tabs.remove(viewer.id);
    throw error;
  }
}

async function claimStream(sender) {
  if (!sender.tab?.id || sender.url !== chrome.runtime.getURL(playerPath)) return {};
  const key = 'capture-' + sender.tab.id;
  const result = await chrome.storage.session.get(key);
  await chrome.storage.session.remove(key);
  return result[key] || {};
}

chrome.runtime.onMessage.addListener((message, sender, respond) => {
  if (sender.id !== chrome.runtime.id) return;
  let action;
  if (message.type === 'start-music-visuals' &&
      sender.url === chrome.runtime.getURL('popup.html')) {
    action = startVisuals();
  } else if (message.type === 'claim-music-stream') {
    action = claimStream(sender);
  } else {
    return;
  }
  action.then(respond).catch(error => respond({
    error: error.message || 'The music tab could not be captured. Play the song and try again.'
  }));
  return true;
});

chrome.tabs.onRemoved.addListener(tabId => {
  chrome.storage.session.remove('capture-' + tabId);
});

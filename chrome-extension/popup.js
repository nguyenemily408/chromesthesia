const button = document.getElementById('start');
const status = document.getElementById('status');
button.addEventListener('click', async () => {
  button.disabled = true;
  status.textContent = 'Connecting to this music tab…';
  try {
    const response = await chrome.runtime.sendMessage({type: 'start-music-visuals'});
    if (response?.error) throw new Error(response.error);
    window.close();
  } catch (error) {
    status.textContent = error.message || 'Open a music tab and try again.';
    button.disabled = false;
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const guideToggle = document.getElementById('guideToggle');
  const GUIDE_ENABLED_KEY = 'isGuideEnabled';

  // Load the current state from storage and set the toggle
  chrome.storage.local.get(GUIDE_ENABLED_KEY, (result) => {
    guideToggle.checked = !!result[GUIDE_ENABLED_KEY];
  });

  // Save the state when the toggle is changed
  guideToggle.addEventListener('change', () => {
    chrome.storage.local.set({ [GUIDE_ENABLED_KEY]: guideToggle.checked });
  });
});

const CONSENT_KEY = 'hasConsented';

document.body.addEventListener('click', (event) => {
  chrome.storage.local.get(CONSENT_KEY, (result) => {
    if (result[CONSENT_KEY]) {
      const logData = {
        type: 'click',
        target: {
          tagName: event.target.tagName,
          id: event.target.id,
          className: event.target.className,
          textContent: event.target.textContent.slice(0, 50)
        },
        timestamp: new Date().toISOString(),
        url: window.location.href
      };

      console.log('Follow Me! - Captured click event:', logData);
      chrome.runtime.sendMessage(logData);
    }
  });
});
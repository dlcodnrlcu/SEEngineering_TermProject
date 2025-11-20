const LOG_BUFFER_KEY = 'logBuffer';
const CONSENT_KEY = 'hasConsented';
const UPLOAD_ALARM_NAME = 'uploadAlarm';

// 1. On install, check for consent. If not given, open consent page.
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    chrome.storage.local.get(CONSENT_KEY, (result) => {
      if (result[CONSENT_KEY] === undefined) {
        // Consent not yet given, open the consent page
        chrome.tabs.create({ url: 'consent.html' });
      }
    });
    // Create an alarm to periodically send logs
    chrome.alarms.create(UPLOAD_ALARM_NAME, {
      delayInMinutes: 1, // Start after 1 minute
      periodInMinutes: 5 // Repeat every 5 minutes
    });
  }
});

// 2. Listener for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  chrome.storage.local.get(CONSENT_KEY, (result) => {
    if (result[CONSENT_KEY]) {
      // User has consented, buffer the log
      chrome.storage.local.get(LOG_BUFFER_KEY, (data) => {
        const buffer = data[LOG_BUFFER_KEY] || [];
        buffer.push(message);
        chrome.storage.local.set({ [LOG_BUFFER_KEY]: buffer }, () => {
          console.log('Follow Me! - Log buffered.');
        });
      });
    }
  });
  // Return true to indicate you wish to send a response asynchronously
  return true;
});


// 3. Listener for the alarm to send buffered logs
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === UPLOAD_ALARM_NAME) {
    sendBufferedLogs();
  }
});

function sendBufferedLogs() {
  chrome.storage.local.get([LOG_BUFFER_KEY, CONSENT_KEY], (result) => {
    if (!result[CONSENT_KEY]) {
      return; // Do not send if consent is not given
    }

    const buffer = result[LOG_BUFFER_KEY];
    if (buffer && buffer.length > 0) {
      console.log(`Follow Me! - Sending ${buffer.length} buffered logs.`);
      fetch('http://127.0.0.1:5000/api/v1/log_batch', { // Assuming a new batch endpoint
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(buffer),
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          console.log('Follow Me! - Backend response for batch:', data);
          // Clear the buffer after successful sending
          chrome.storage.local.set({ [LOG_BUFFER_KEY]: [] });
        } else {
          console.error('Follow Me! - Backend error for batch:', data.message);
        }
      })
      .catch((error) => {
        console.error('Follow Me! - Error sending batch data to backend:', error);
      });
    }
  });
}
const LOG_BUFFER_KEY = 'logBuffer';
const CONSENT_KEY = 'hasConsented';
const SESSION_ID_KEY = 'sessionId';
const UPLOAD_ALARM_NAME = 'uploadAlarm';

// Function to generate a simple UUID
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// 1. On install, set up session ID, consent, and alarm
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    // Check for consent
    chrome.storage.local.get(CONSENT_KEY, (result) => {
      if (result[CONSENT_KEY] === undefined) {
        chrome.tabs.create({ url: 'consent.html' });
      }
    });

    // Generate and store a session ID
    chrome.storage.local.set({ [SESSION_ID_KEY]: generateUUID() });

    // Create an alarm for periodic uploads
    // Development: 1 minute. Production should be longer (e.g., 5-10 mins)
    chrome.alarms.create(UPLOAD_ALARM_NAME, {
      delayInMinutes: 1,
      periodInMinutes: 1
    });
  }
});

// 2. Listener for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  chrome.storage.local.get([CONSENT_KEY, SESSION_ID_KEY], (result) => {
    if (result[CONSENT_KEY]) {
      // Add session ID to the message
      message.sessionId = result[SESSION_ID_KEY];

      chrome.storage.local.get(LOG_BUFFER_KEY, (data) => {
        const buffer = data[LOG_BUFFER_KEY] || [];
        buffer.push(message);
        chrome.storage.local.set({ [LOG_BUFFER_KEY]: buffer }, () => {
          console.log('Follow Me! - Log buffered.');
          // It's good practice to respond, even if it's just an acknowledgement
          sendResponse({status: "success"});
        });
      });
    } else {
        sendResponse({status: "consent_not_given"});
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
      fetch('http://127.0.0.1:5000/api/v1/log_batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(buffer),
      })
      .then(response => {
        if (response.ok) {
            return response.json();
        }
        // If the response is not ok, throw an error to be caught by the catch block
        throw new Error(`Server responded with status: ${response.status}`);
      })
      .then(data => {
        console.log('Follow Me! - Backend response for batch:', data);
        // Clear the buffer only after successful sending
        chrome.storage.local.set({ [LOG_BUFFER_KEY]: [] });
      })
      .catch((error) => {
        console.error('Follow Me! - Error sending batch data to backend:', error);
        // Optional: Decide on a retry strategy or if logs should be kept or discarded
      });
    }
  });
}
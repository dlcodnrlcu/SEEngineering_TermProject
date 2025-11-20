document.getElementById('agree').addEventListener('click', () => {
  // Set consent status in storage and enable the extension
  chrome.storage.local.set({ hasConsented: true }, () => {
    console.log('User has consented to data collection.');
    // Close the consent tab
    window.close();
  });
});

document.getElementById('disagree').addEventListener('click', () => {
  // Set consent status in storage and disable the extension's data collection
  chrome.storage.local.set({ hasConsented: false }, () => {
    console.log('User has not consented to data collection.');
     // Close the consent tab
    window.close();
  });
});

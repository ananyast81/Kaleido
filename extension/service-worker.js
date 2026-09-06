// Background service worker. Runs persistently (separate from any page),
// and acts as the go-between for detect-article.js (which runs on pages)
// and popup.js (which runs when the toolbar icon is clicked).
//
// Job: remember the most recently detected article for each tab, so that
// whenever the popup asks "what article is on the current tab?", the answer
// is already sitting here — regardless of whether detection happened
// 5 seconds ago or 5 milliseconds ago.

const articleByTab = new Map();

// Listener 1: a content script (detect-article.js) reports an article was found.
chrome.runtime.onMessage.addListener((message, sender) => {
  if (message.type === 'ARTICLE_DETECTED' && sender.tab?.id != null) {
    articleByTab.set(sender.tab.id, message.payload);

    // Visual confirmation in the toolbar that something was detected on this tab.
    chrome.action.setBadgeText({ text: '●', tabId: sender.tab.id });
    chrome.action.setBadgeBackgroundColor({ color: '#5b8def', tabId: sender.tab.id });
  }
});

// Listener 2: the popup asks "what article did we detect on the active tab?"
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_CURRENT_ARTICLE') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tabId = tabs[0]?.id;
      sendResponse(articleByTab.get(tabId) || null);
    });
    return true; // keep the message channel open — chrome.tabs.query is async,
                 // so sendResponse() will be called later, not immediately.
  }
});

// Clean up when a tab closes, so this map doesn't grow forever during a browsing session.
chrome.tabs.onRemoved.addListener((tabId) => {
  articleByTab.delete(tabId);
});
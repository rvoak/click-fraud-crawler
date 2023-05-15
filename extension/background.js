
const port = 3000;
// Attach the debugger to the active tab
chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
  chrome.debugger.attach({tabId: tabs[0].id}, '1.0', function() {
    // Register a listener function for Page events
  chrome.debugger.onEvent.addListener(function(source, method, params) {
    if (source === 'Page' && method === 'windowOpen') {
      console.log('Page.windowOpen event:', params.url);
    }
  });

  // Enable the Page domain
  chrome.debugger.sendCommand({ tabId: tabId }, 'Page.enable', {}, function() {
    console.log('Page domain enabled');
  });
  });
});

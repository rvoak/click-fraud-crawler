const port = 3000;

// Attach the debugger to the active tab
function attachDebugger(tabId) {
  chrome.debugger.attach({tabId: tabId}, '1.0', function() {
    // Enable the Network domain
    chrome.debugger.sendCommand({tabId: tabId}, 'Network.enable', {}, function() {
      // Set up listener for requestWillBeSent event
      chrome.debugger.onEvent.addListener(function(debuggeeId, message, params) {
        if (debuggeeId.tabId === tabId && message === 'Network.requestWillBeSent') {
          fetch(`http://localhost:${port}/request`, {
                  method: "POST",
                  body: JSON.stringify({
                    "type": "NetworkRequest",
                    "http_req": params.request.url,
                    "request_id": params.requestId,
                    "frame_url": params.documentURL,
                    "resource_type": params.type,
                    "header": params.request.headers,
                    "timestamp": new Date().getTime(),
                    "frameId": params.frameId,
                    "hasUserGesture": params.hasUserGesture,
                    "call_stack": params.initiator
                  }),
                  mode: 'cors',
                  headers: {
                      'Access-Control-Allow-Origin': '*',
                      "Content-Type": "application/json"
                  }
      });
        }
      });
    });

    chrome.debugger.sendCommand({tabId: tabId}, 'Page.enable', {}, function() {
      // Set up listener for Page.windowOpen event
      chrome.debugger.onEvent.addListener(function(debuggeeId, message, params) {
        if (debuggeeId.tabId === tabId && message === 'Page.windowOpen') {
          var simplifiedStackTrace = null;
          if (params.stackTrace) {
            simplifiedStackTrace = params.stackTrace.callFrames.map(function(callFrame) {
              return {
                functionName: callFrame.functionName,
                scriptId: callFrame.scriptId,
                url: callFrame.url,
                lineNumber: callFrame.lineNumber,
                columnNumber: callFrame.columnNumber
              };
            });
          }
          fetch(`http://localhost:${port}/pagewindowopen`, {
                  method: "POST",
                  body: JSON.stringify({
                    "type": "Page.windowOpen",
                    "http_req": params.url,
                    "windowName": params.windowName,
                    "windowDisposition": params.disposition,
                    "timestamp": new Date().getTime(),
                    "stackTrace": simplifiedStackTrace,
                    "stack": params.stack,
                    "initiator": params.initiator
                  }),
                  mode: 'cors',
                  headers: {
                      'Access-Control-Allow-Origin': '*',
                      "Content-Type": "application/json"
                  }
      });
        }
      });
    });

    chrome.debugger.sendCommand({tabId: tabId}, 'Page.enable', {}, function() {
      // Set up listener for Page.frameAttached event
      chrome.debugger.onEvent.addListener(function(debuggeeId, message, params) {
        if (debuggeeId.tabId === tabId && message === 'Page.frameAttached') {
          var simplifiedStackTrace = null;
          if (params.stack) {
            simplifiedStackTrace = params.stack.callFrames.map(function(callFrame) {
              return {
                functionName: callFrame.functionName,
                scriptId: callFrame.scriptId,
                url: callFrame.url,
                lineNumber: callFrame.lineNumber,
                columnNumber: callFrame.columnNumber
              };
            });
          }
          fetch(`http://localhost:${port}/pagewindowopen`, {
                  method: "POST",
                  body: JSON.stringify({
                    "type": "Page.frameAttached",
                    "http_req": params.url,
                    "windowName": params.windowName,
                    "windowDisposition": params.disposition,
                    "timestamp": new Date().getTime(),
                    "stackTrace": simplifiedStackTrace
                  }),
                  mode: 'cors',
                  headers: {
                      'Access-Control-Allow-Origin': '*',
                      "Content-Type": "application/json"
                  }
      });
        }
      });
    });

    chrome.debugger.sendCommand({tabId: tabId}, 'DOM.enable', {}, function() {
      // Set up listener for Page.frameAttached event
      chrome.debugger.onEvent.addListener(function(debuggeeId, message, params) {
        if (debuggeeId.tabId === tabId && message === 'DOM.attributeModified' && params == 'href') {
          var simplifiedStackTrace = null;
          if (params.stack) {
            simplifiedStackTrace = params.stack.callFrames.map(function(callFrame) {
              return {
                functionName: callFrame.functionName,
                scriptId: callFrame.scriptId,
                url: callFrame.url,
                lineNumber: callFrame.lineNumber,
                columnNumber: callFrame.columnNumber
              };
            });
          }
          fetch(`http://localhost:${port}/pagewindowopen`, {
                  method: "POST",
                  body: JSON.stringify({
                    "type": "DOM.attributeModified.HREF",
                    "http_req": params.url,
                    "windowName": params.windowName,
                    "windowDisposition": params.disposition,
                    "timestamp": new Date().getTime(),
                    "stackTrace": simplifiedStackTrace
                  }),
                  mode: 'cors',
                  headers: {
                      'Access-Control-Allow-Origin': '*',
                      "Content-Type": "application/json"
                  }
      });
        }
      });
    });

    chrome.debugger.sendCommand({tabId: tabId}, 'DOM.enable', {}, function() {
      // Set up listener for Page.frameAttached event
      chrome.debugger.onEvent.addListener(function(debuggeeId, message, params) {
        if (debuggeeId.tabId === tabId && message === 'DOM.childNodeInserted') {
          var simplifiedStackTrace = null;
          if (params.stack) {
            simplifiedStackTrace = params.stack.callFrames.map(function(callFrame) {
              return {
                functionName: callFrame.functionName,
                scriptId: callFrame.scriptId,
                url: callFrame.url,
                lineNumber: callFrame.lineNumber,
                columnNumber: callFrame.columnNumber
              };
            });
          }
          fetch(`http://localhost:${port}/domevents`, {
                  method: "POST",
                  body: JSON.stringify({
                    "type": "DOM.childNodeInserted",
                    "ParentNode": params.parentNodeId,
                    "PreviousNode": params.previousNodeId,
                    "NodeInserted": params.node,
                    "windowName": params.windowName,
                    "windowDisposition": params.disposition,
                    "timestamp": new Date().getTime(),
                    "stackTrace": simplifiedStackTrace
                  }),
                  mode: 'cors',
                  headers: {
                      'Access-Control-Allow-Origin': '*',
                      "Content-Type": "application/json"
                  }
      });
        }
      });
    });


  });
}

// Listen for new tab created events
chrome.tabs.onCreated.addListener(function(tab) {
  attachDebugger(tab.id);
});

// Attach the debugger to the active tab when the extension is first installed
chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
  attachDebugger(tabs[0].id);
});

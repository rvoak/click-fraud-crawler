
const port = 3000;
// Listen for clicks on the page
document.addEventListener('click', function(event) {
    // Your custom code here
    let targetElement = event.target;
    let simpleTarget = {
    tagName: targetElement.tagName,
    id: targetElement.id,
    classes: targetElement.classList
    };
    console.log("Clicked!", simpleTarget, new Date().getTime());
    fetch(`http://localhost:${port}/clicked`, {
                method: "POST",
                body: JSON.stringify({
                    "CoordinateX": event.clientX,
                    "CoordinateY": event.clientY,
                    "event": "click",
                    "element":simpleTarget,
                    "timestamp": new Date().getTime(),
                    "stack": new Error().stack
                }),
                mode: 'cors',
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    "Content-Type": "application/json"
                }
    });
    console.log("Clicked!", event.target, new Date().getTime());

  });

// Listen for mousedown on the page
document.addEventListener('mousedown', function(event) {
    // Your custom code here
    let targetElement = event.target;
    let simpleTarget = {
    tagName: targetElement.tagName,
    id: targetElement.id,
    classes: targetElement.classList
    };
    fetch(`http://localhost:${port}/clicked`, {
                method: "POST",
                body: JSON.stringify({
                    "CoordinateX": event.clientX,
                    "CoordinateY": event.clientY,
                    "event": "mousedown",
                    "element":simpleTarget,
                    "timestamp": new Date().getTime(),
                    "stack": new Error().stack
                }),
                mode: 'cors',
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    "Content-Type": "application/json"
                }
    });
    console.log("Clicked!", event.target);
  });

  // Listen for mouseup on the page
document.addEventListener('mouseup', function(event) {
    // Your custom code here
    fetch(`http://localhost:${port}/clicked`, {
                method: "POST",
                body: JSON.stringify({
                    "CoordinateX": event.clientX,
                    "CoordinateY": event.clientY,
                    "event": "mouseup",
                    "timestamp": new Date().getTime(),
                    "stack": new Error().stack
                }),
                mode: 'cors',
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    "Content-Type": "application/json"
                }
    });
    console.log("Clicked!", event.target);
  })

let originalFunctionWindowOpen = window.open;
window.open = function(keyName, keyValue) {
      try{
          originalFunctionWindowOpen.apply(this, arguments);
          fetch("http://localhost:3000/pagewindowopen", {
              method: "POST",
              body: JSON.stringify({
                  "top_level_url": window.location.href,
                  "function": "window.open",
                  "timestamp": new Date().getTime(),
                  "stack": new Error().stack
              }),
              mode: 'cors',
              headers: {
                  'Access-Control-Allow-Origin': '*',
                  "Content-Type": "application/json"
              }
          }).then(res => {
              console.log("window open collected");
          });
          return;
      }
      catch(err){
          originalFunctionWindowOpen.apply(this, arguments);
      }
  }

// contentScript.js

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action === "scanEmail") {
    console.log("Scanning email...");
    var list = document.getElementsByClassName("ii");
    var output = "";
    for (var i = 0; i < list.length; i++) {
      output += list[i].innerText + "\n";
    }

    chrome.runtime.sendMessage({ action: "emailScanned", data: output });
  }

  if (request.action === "scanXSS") {
    // Code to scan for XSS
    fetch("http://127.0.0.1:5000/scan/xss", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: window.location.href }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        sendResponse({ action: "scanXSS", data: data });
      })
      .catch((error) => {
        console.error("Error:", error);
        sendResponse({ action: "scanXSS", error: error });
      });
    return true; // Needed to indicate that sendResponse will be called asynchronously
  }

  if (request.action === "scanSQL") {
    chrome.runtime.sendMessage(
      {
        action: "makeRequest",
        url: "http://127.0.0.1:5000/scan/sql",
        method: "POST",
        data: { url: window.location.href },
      },
      function (response) {
        if (response && response.action === "scanSQL") {
          sendResponse(response);
        } else {
          console.error("Scan SQL action not received.");
        }
      }
    );
    return true; // Keep the messaging channel open for sendResponse
  }

  if (request.action === "scanCSRF") {
    // Code to scan for CSRF
    fetch("http://127.0.0.1:5000/scan/csrf", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: window.location.href }),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        // Handle CSRF scan results
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
});

// popup.js

function scanEmail() {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        files: ["contentScript.js"],
      },
      function () {
        chrome.tabs.sendMessage(tabs[0].id, { action: "scanEmail" });
      }
    );
  });
}

function readURLs() {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        files: ["readURLScript.js"],
      },
      function (result) {
        const urlList = result[0].result;
        console.log(urlList);

        if (urlList.length === 0) {
          document.getElementById("serverResponse").innerText =
            "No URLs to process.";
          return;
        }

        // Send the urlList to the server
        fetch("http://127.0.0.1:5000/predict/phishing", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ urls: urlList }),
        })
          .then((response) => response.json())
          .then((data) => {
            console.log(data);
            const goodCount = data.predictions.filter(
              (prediction) => prediction === "good"
            ).length;
            const total = data.predictions.length;
            const emailSafetyPercentage = (goodCount / total) * 100;

            if (isNaN(emailSafetyPercentage)) {
              document.getElementById("serverResponse").innerText =
                "No URLs to process.";
            } else {
              document.getElementById(
                "serverResponse"
              ).innerText = `Email Safety Percentage: ${emailSafetyPercentage.toFixed(
                2
              )}%`;
            }
          })
          .catch((error) => {
            console.error("Error:", error);
          });
      }
    );
  });
}

function scanXSS() {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        files: ["contentScript.js"],
      },
      function () {
        chrome.tabs.sendMessage(
          tabs[0].id,
          { action: "scanXSS" },
          function (response) {
            if (response && response.action === "scanXSS") {
              console.log(response.data);
              displayScanResults(response.data);
            }
          }
        );
      }
    );
  });
}

function scanSQL() {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        files: ["contentScript.js"],
      },
      function () {
        chrome.tabs.sendMessage(
          tabs[0].id,
          { action: "scanSQL" },
          function (response) {
            if (response && response.action === "scanSQL") {
              console.log(response.data);
              if (response.data && response.data.result) {
                displayScanResults(response.data.result);
              } else {
                console.error("Scan SQL result not received or invalid.");
              }
            } else {
              console.error("Scan SQL action not received.");
            }
          }
        );
      }
    );
  });
}

function scanCSRF() {
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        files: ["contentScript.js"],
      },
      function (response) {
        chrome.tabs.sendMessage(tabs[0].id, { action: "scanCSRF" });
        console.log(response.data);
        displayScanResults(response.data);
      }
    );
  });
}

document.addEventListener("DOMContentLoaded", function () {
  document
    .getElementById("scanEmailButton")
    .addEventListener("click", scanEmail);
  document.getElementById("readURLButton").addEventListener("click", readURLs);
  document.getElementById("scanXSSButton").addEventListener("click", scanXSS);
  document.getElementById("scanSQLButton").addEventListener("click", scanSQL);
  document.getElementById("scanCSRFButton").addEventListener("click", scanCSRF);
});

chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  if (request.action === "makeRequest") {
    fetch(request.url, {
      method: request.method,
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request.data),
    })
      .then((response) => response.json())
      .then((data) => sendResponse({ action: "scanSQL", data: data }))
      .catch((error) =>
        sendResponse({ action: "scanSQL", error: error.message })
      );

    return true; // Keep the messaging channel open for sendResponse
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
          console.log(response.data);
          if (response.data && response.data.result) {
            displayScanResults(response.data.result);
          } else {
            console.error("Scan SQL result not received or invalid.");
          }
        } else {
          console.error("Scan SQL action not received.");
        }
      }
    );
  }
  if (request.action === "scanXSS") {
    fetch("http://127.0.0.1:5000/scan/xss", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: window.location.href }),
    })
      .then((response) => response.json())
      .then((data) => {
        const messages = data.result.messages;
        let messageString = messages.join("\n");
        //document.getElementById("serverResponses").innerText = messageString;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
  if (request.action === "scanCSRF") {
    fetch("http://127.0.0.1:5000/scan/csrf", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: window.location.href }),
    })
      .then((response) => response.json())
      .then((data) => {
        const result = data.result;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }

  if (request.action === "emailScanned") {
    const emailData = request.data;

    fetch("http://127.0.0.1:5000/predict/spam", {
      method: "POST",
      body: emailData,
    })
      .then((response) => response.json())
      .then((data) => {
        const prediction = data.prediction;
        const predictionPercentage = data.prediction_percentage;

        document.getElementById(
          "output"
        ).innerText = `Prediction: ${prediction}\nPrediction Percentage: ${predictionPercentage}%`;
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  }
});

function displayScanResults(data) {
  const messages = data.result.messages;
  let messageString = messages.join("\n");
  document.getElementById("serverResponses").innerText = messageString; // Assuming you have a div with id "serverResponses" in popup.html
}

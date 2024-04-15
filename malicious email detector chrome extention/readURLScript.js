// readURLScript.js

var elements = document.querySelectorAll(".adn.ads a");
var urlList = [];

for (var i = 0; i < elements.length; i++) {
  var element = elements[i];

  var href = element.href;
  if (href) {
    urlList.push(href);
  }

  var parentButton = element.closest("button");
  var isButtonImage =
    parentButton && parentButton.querySelector("img") === element;

  if (isButtonImage) {
    var style = window.getComputedStyle(parentButton);
    var backgroundImage = style.getPropertyValue("background-image");

    if (backgroundImage && backgroundImage !== "none") {
      var url = backgroundImage.replace(/url\(['"]?([^'"]+)['"]?\)/i, "$1");
      urlList.push(url);
    }
  }
}

urlList;

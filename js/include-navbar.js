// /js/include-navbar.js
document.addEventListener("DOMContentLoaded", function () {
    fetch("/navbar.html")
      .then(response => response.text())
      .then(data => {
        const navContainer = document.createElement("div");
        navContainer.innerHTML = data;
        document.body.insertBefore(navContainer, document.body.firstChild);
  
        // Add active class to nav and icon links based on current page
        const path = window.location.pathname.split("/").pop().split(".")[0];
  
        document.querySelectorAll("[data-page]").forEach(el => {
          if (el.getAttribute("data-page") === path) {
            if (el.tagName.toLowerCase() === "a" && el.classList.contains("icon-circle")) {
              el.classList.add("active");
            } else {
              el.classList.add("active");
            }
          }
        });
      });
  });
  
document.addEventListener("DOMContentLoaded", () => {
  const email = localStorage.getItem("email");

  if (email) {
    fetch('/get_user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        document.getElementById("user-name").textContent = data.name || "Anonymous";
        document.getElementById("page_title").textContent = data.name || "Profile";
        document.getElementById("page_title").textContent = 'Cinemago - '+ document.getElementById("page_title").textContent;
        document.getElementById("user-email").textContent = data.email || "-";
        document.getElementById("user-class").textContent = data.weight || "-";
        document.getElementById("user-class").textContent += "/3";
        
      } else {
        showGuestMessage();
      }
    })
    .catch(() => showGuestMessage());
  } else {
    showGuestMessage();
  }

  function showGuestMessage() {
    document.querySelector(".profile-header").textContent = "Guest ";
    document.querySelector(".profile-container").innerHTML = `
      <p style="margin-top: 20px; font-weight: bold;">You are viewing as a guest</p>
      <a href="login.html">
        <button class="btn-logout">Log In</button>
      </a>
    `;
    document.getElementById("user-name").textContent = "-";
    document.getElementById("user-email").textContent = "-";
    document.getElementById("user-class").textContent = "-";
  }
});

function logout() {
  localStorage.removeItem("email");
  window.location.href = "login.html";
}

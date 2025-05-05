document.querySelector('form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);
  const email = formData.get("email");

  const response = await fetch('/login', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();

  if (result.status === 'success') {
    localStorage.setItem("email", email); // store login state
    window.location.href = result.redirect;
  } else {
    showPopup(result.message);
  }
});

function showPopup(message) {
  let popup = document.createElement('div');
  popup.textContent = message;
  popup.style.position = 'fixed';
  popup.style.top = '20px';
  popup.style.right = '20px';
  popup.style.padding = '10px 20px';
  popup.style.backgroundColor = '#ff4d4d';
  popup.style.color = 'white';
  popup.style.borderRadius = '8px';
  popup.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
  document.body.appendChild(popup);

  setTimeout(() => popup.remove(), 3000);
}

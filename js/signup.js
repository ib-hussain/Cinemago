document.querySelector('form').addEventListener('submit', async function (e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);

  const response = await fetch('/signup', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();

  if (result.status === 'success') {
    window.location.href = result.redirect; // login.html
  } else {
    showError(result.message);
  }
});

function showError(message) {
  const errorDiv = document.getElementById('error-message');
  errorDiv.textContent = message;
  errorDiv.style.color = 'red';
  errorDiv.style.marginTop = '10px';
}

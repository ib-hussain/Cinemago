// Load all users and make rows clickable
fetch('/get_all_users')
  .then(res => res.json())
  .then(data => {
    if (data.status === 'success') {
      const table = document.getElementById('user-table');
      data.users.forEach(user => {
        const row = document.createElement('tr');
        row.style.cursor = 'pointer';
        row.innerHTML = `<td>${user.name}</td><td>${user.email}</td><td>${user.weight}</td>`;

        // Click = autofill form
        row.addEventListener('click', () => {
          document.querySelector('#update-form input[name="email"]').value = user.email;
          document.querySelector('#update-form input[name="weight"]').value = user.weight;
        });

        table.appendChild(row);
      });
    } else {
      alert("Failed to load users.");
    }
  })
  .catch(err => {
    console.error("Error fetching users:", err);
    alert("Could not load user list.");
  });

// Update user weight
document.getElementById('update-form').addEventListener('submit', async e => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const res = await fetch('/update_weight', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: formData.get('email'),
      weight: parseFloat(formData.get('weight'))
    })
  });

  const result = await res.json();
  alert(result.message);
  location.reload();
});

// Upload new movie with poster
document.getElementById('upload-form').addEventListener('submit', async e => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const res = await fetch('/admin/upload_movie', {
    method: 'POST',
    body: formData
  });

  const result = await res.json();
  alert(result.message);
  e.target.reset();
});

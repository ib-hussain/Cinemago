document.addEventListener('DOMContentLoaded', async function () {
  const grid = document.getElementById('search-grid');
  const searchInput = document.getElementById('movie-search');
  let allMovies = [];

  function renderMovies(movies) {
    grid.innerHTML = '';
    if (movies.length === 0) {
      grid.innerHTML = '<p>No movies found</p>';
      return;
    }

    movies.forEach(movie => {
      const card = document.createElement('a');
      card.className = 'movie-card';
      card.href = `search/movie_template.html?movie_id=${movie.movie_id}`;
      card.innerHTML = `
        <img src="pictures/${movie.poster}.jpg" alt="${movie.movie_name}" class="movie-poster" />
        <span class="movie-title">${movie.movie_name}</span>
      `;
      grid.appendChild(card);
    });
  }

  try {
    const response = await fetch('/get_all_movies');
    const data = await response.json();
    if (data.status === 'success') {
      allMovies = data.movies;
      renderMovies(allMovies);
    } else {
      grid.innerHTML = "<p>No movies available</p>";
    }
  } catch (err) {
    console.error('Error loading movies:', err);
    grid.innerHTML = "<p>Failed to load movies</p>";
  }

  // Live filter logic
  searchInput.addEventListener('input', () => {
    const searchTerm = searchInput.value.toLowerCase();
    const filtered = allMovies.filter(movie =>
      movie.movie_name.toLowerCase().includes(searchTerm)
    );
    renderMovies(filtered);
  });
});

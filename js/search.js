document.addEventListener('DOMContentLoaded', async function () {
    const grid = document.getElementById('search-grid');
    try {
        const response = await fetch('/get_all_movies');
        const data = await response.json();

        if (data.status === 'success') {
            const movies = data.movies;
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
        } else {
            grid.innerHTML = "<p>No movies available</p>";
        }
    } catch (err) {
        console.error('Error loading movies:', err);
        grid.innerHTML = "<p>Failed to load movies</p>";
    }
});
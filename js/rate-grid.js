document.addEventListener('DOMContentLoaded', async function () {
    try {
        const response = await fetch('/get_all_movies');
        const data = await response.json();

        if (data.status === 'success') {
            const movies = data.movies;
            const grid = document.getElementById('rate-grid');

            movies.forEach(movie => {
                const a = document.createElement('a');
                a.className = 'movie-card';
                a.href = `../rate/rate_template.html?movie_id=${movie.movie_id}`;

                a.innerHTML = `
                    <img src="../pictures/${movie.poster}.jpg" alt="${movie.movie_name}" class="movie-poster" />
                    <span class="movie-title">${movie.movie_name}</span>
                `;

                grid.appendChild(a);
            });
        } else {
            console.error('Failed to load movies');
        }
    } catch (err) {
        console.error('Error fetching movie data:', err);
    }
});

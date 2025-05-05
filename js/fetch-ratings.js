document.addEventListener('DOMContentLoaded', async function () {
    try {
        const response = await fetch('/get_all_movies');
        const data = await response.json();

        if (data.status === 'success') {
            const movies = data.movies;

            document.querySelectorAll('.rating').forEach(div => {
                const id = div.getAttribute('data-movie-id');
                const movie = movies.find(m => m.movie_id === id);

                if (movie && movie.num_ratings > 0) {
                    const avg = (parseFloat(movie.total_weighted) / parseInt(movie.num_ratings)).toFixed(1);
                    div.textContent = `${Math.min(avg, 10)}/10`;
                } else {
                    div.textContent = "-/10";
                }
            });
        }
    } catch (err) {
        console.error('Failed to load ratings dynamically', err);
    }
});

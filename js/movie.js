document.addEventListener('DOMContentLoaded', async function () {
    const params = new URLSearchParams(window.location.search);
    const movieID = params.get('movie_id');

    if (!movieID) {
        document.getElementById('movie-container').innerHTML = "<p>Movie not found!</p>";
        return;
    }

    try {
        const response = await fetch('/get_movie', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ movie_id: movieID })
        });
        const data = await response.json();

        if (data.status === 'success') {
            document.title = `Cinemago - ${data.movie_name}`; // Dynamic browser tab title
            document.getElementById('movie-title').textContent = data.movie_name;
            document.getElementById('movie-subinfo').textContent = data.year_genre;
            document.getElementById('movie-poster').src = `../pictures/${data.poster}`;
            document.getElementById('movie-description').textContent = data.description;
            document.getElementById('movie-director').textContent = data.director;
            document.getElementById('movie-writer').textContent = data.writer;
            document.getElementById('movie-stars').textContent = data.stars;
            const avg = (data.total_weighted / data.num_ratings).toFixed(1);
            document.getElementById('movie-rating').textContent = `${Math.min(avg, 10)}/10`;

            // Fix rate link to carry movie_id
            document.getElementById('rate-link').href = `../rate/rate_template.html?movie_id=${movieID}`;
        } else {
            document.getElementById('movie-container').innerHTML = "<p>Movie data not available.</p>";
        }
    } catch (err) {
        console.log("Error fetching movie info");
        document.getElementById('movie-container').innerHTML = "<p>Error loading movie.</p>";
    }
});

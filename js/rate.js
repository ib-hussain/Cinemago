document.addEventListener('DOMContentLoaded', async function () {
    const email = localStorage.getItem('email');
    const rateContainer = document.getElementById('rate-container');
    const avgRatingDisplay = document.getElementById('average-rating');
    const params = new URLSearchParams(window.location.search);
    const movieID = params.get('movie_id');

    const movieTitle = document.getElementById('movie-title');
    const movieSubinfo = document.getElementById('movie-subinfo');
    const moviePoster = document.getElementById('movie-poster');
    const movieDescription = document.getElementById('movie-description');
    const movieDirector = document.getElementById('movie-director');
    const movieWriter = document.getElementById('movie-writer');
    const movieStars = document.getElementById('movie-stars');

    if (!email) {
        loadMovieInfo();
        rateContainer.innerHTML = `
            <p style="margin-top: 0px; color: #171a1f; font-size: 40px; font-weight: bold;">You are viewing as a guest</p>
            <a href="../login.html">
                <button class="btn-logout">Log In</button>
            </a>
        `;
        return;
    }

    let userWeight = 1;
    try {
        const response = await fetch('/get_user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await response.json();
        if (data.status === 'success') {
            userWeight = parseFloat(data.weight) || 1;
        }
    } catch (err) {
        console.error("Error fetching user weight", err);
    }

    async function loadMovieInfo() {
        try {
            const response = await fetch('/get_movie', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ movie_id: movieID })
            });
            const data = await response.json();
            if (data.status === 'success') {
                const avg = (data.total_weighted / data.num_ratings).toFixed(1);
                avgRatingDisplay.textContent = `${Math.min(avg, 10)}/10`;

                moviePoster.src = `../pictures/${data.poster}`;
                moviePoster.alt = `${data.movie_name} Poster`;

                movieTitle.textContent = data.movie_name;
                movieSubinfo.textContent = `${data.year_genre}`;
                movieDescription.textContent = data.description;
                movieDirector.textContent = data.director;
                movieWriter.textContent = data.writer;
                movieStars.textContent = data.stars;
            }
        } catch (err) {
            console.error("Error loading movie info", err);
        }
    }

    await loadMovieInfo();

    rateContainer.innerHTML = `
        <label for="user-rating" style="font-size:18px;font-weight:bold;">Your Rating (0-10):</label>
        <input id="user-rating" type="number" min="0" max="10" step="0.1" style="padding:5px;margin:10px;">
        <button id="submit-rating" class="btn-logout" style="margin-left:10px;">Submit Rating</button>
    `;

    document.getElementById('submit-rating').addEventListener('click', async function () {
        const userRating = parseFloat(document.getElementById('user-rating').value);
        if (isNaN(userRating) || userRating <= -0.1 || userRating >= 10.1) {
            alert('Enter a valid rating between 0 and 10');
            return;
        }

        const weightedRating = userRating * userWeight;

        try {
            const response = await fetch('/rate_movie', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    movie_id: movieID,
                    weighted_rating: weightedRating, 
                    num_rating: userWeight
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                const avg = (data.total_weighted / data.num_ratings).toFixed(1);
                avgRatingDisplay.textContent = `${Math.min(avg, 10)}/10`;
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: 'Your rating has been submitted successfully!',
                    showConfirmButton: false,
                    timer: 1500
                });
                
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error!',
                    text: 'Failed to submit rating. Try again later.',
                    showConfirmButton: false,
                    timer: 1500
                });
                
            }
        } catch (err) {
            console.error("Error submitting rating", err);
            Swal.fire({
                icon: 'error',
                title: 'Server Error!',
                text: 'Please try again later.',
                showConfirmButton: false,
                timer: 1500
            });
            
        }
    });
});

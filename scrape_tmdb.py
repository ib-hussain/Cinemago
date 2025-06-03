import sys
import os
import csv
import sqlite3
import requests
import random

# --- CONFIG ---
API_KEY = os.getenv('TMDB_API_KEY')
DB_FILE = 'data/movies.db'
CSV_FILE = 'data/movies.csv'
POSTER_DIR = 'pictures/movie_posters'
TMDB_API = 'https://api.themoviedb.org/3'

os.makedirs(POSTER_DIR, exist_ok=True)

# --- Helpers ---
def download_poster(url, filename):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"Poster download failed: {e}")
    return False

def format_runtime(minutes):
    h = minutes // 60
    m = minutes % 60
    return f"{h}h {m}m" if h else f"{m}m"

def fetch_movie_details(movie_id):
    r = requests.get(f"{TMDB_API}/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits")
    return r.json() if r.status_code == 200 else {}

def scrape_and_upload(n):
    print("Scraping TMDB popular movies...")
    import random
    page = random.randint(1, 450)  # TMDB supports up to 500 pages
    r = requests.get(f"{TMDB_API}/movie/popular?api_key={API_KEY}&language=en-US&page={page}")
    movies = r.json().get('results', [])[:n]


    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    file_exists = os.path.exists(CSV_FILE)
    csvfile = open(CSV_FILE, 'a', newline='', encoding='utf-8')
    fieldnames = ['movie_id', 'movie_name', 'director', 'writer', 'stars', 'description', 'poster',
                  'year_genre', 'total_weighted', 'num_ratings']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if not file_exists or os.stat(CSV_FILE).st_size == 0:
        csv_writer.writeheader()

    added = 0
    for movie in movies:
        movie_id = str(movie['id'])

        cursor.execute("SELECT 1 FROM movies WHERE movie_id = ?", (movie_id,))
        if cursor.fetchone():
            print(f"Skipped (Duplicate): {movie['title']}")
            continue

        details = fetch_movie_details(movie_id)
        if not details:
            continue

        director = ''
        writer_ = ''
        stars = ''

        crew = details.get('credits', {}).get('crew', [])
        cast = details.get('credits', {}).get('cast', [])

        for person in crew:
            if person['job'] == 'Director':
                director = person['name']
            elif person['department'] == 'Writing':
                writer_ += person['name'] + ", "
        writer_ = writer_.strip(', ')
        stars = ', '.join([a['name'] for a in cast[:3]])

        genre_str = '/'.join([g['name'] for g in details.get('genres', [])])
        year = details.get('release_date', '????')[:4]
        runtime = format_runtime(details.get('runtime', 0))
        year_genre = f"{year} X {genre_str} X {runtime}".replace("X", "|")

        description = details.get('overview', '')
        rating = float(details.get('vote_average') or 8.0)
        num_ratings = 100
        total_weighted = round(rating * num_ratings, 1)

        poster_path = details.get('poster_path', '')
        poster_filename = f"{movie_id}.jpg"
        full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
        poster_local_path = f"movie_posters/{poster_filename}"
        if full_poster_url:
            download_poster(full_poster_url, os.path.join(POSTER_DIR, poster_filename))

        cursor.execute('''
            INSERT INTO movies (movie_id, movie_name, director, writer, stars, description, poster,
                                year_genre, total_weighted, num_ratings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            movie_id,
            movie['title'],
            director,
            writer_,
            stars,
            description,
            poster_local_path,
            year_genre,
            total_weighted,
            num_ratings
        ))
        conn.commit()

        csv_writer.writerow({
            'movie_id': movie_id,
            'movie_name': movie['title'],
            'director': director,
            'writer': writer_,
            'stars': stars,
            'description': description,
            'poster': poster_local_path,
            'year_genre': year_genre,
            'total_weighted': total_weighted,
            'num_ratings': num_ratings
        })

        print(f"Uploaded: {movie['title']}")
        added += 1

    csvfile.close()
    conn.close()
    print(f"\nDone. {added} movie(s) added.")

# --- Run
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scrape_tmdb.py <number_of_movies>")
    else:
        scrape_and_upload(int(sys.argv[1]))

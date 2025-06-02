import sys
import os
import csv
import sqlite3
import requests
from imdb import IMDb

# --- Config ---
DB_FILE = 'movies.db'
CSV_FILE = 'movies.csv'
POSTER_DIR = 'pictures/movie_posters'
os.makedirs(POSTER_DIR, exist_ok=True)

# --- Helpers ---
def clean_filename(name):
    return ''.join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(" ", "_").lower()

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

def format_year_genre_runtime(movie):
    year = str(movie.get('year', ''))
    genres = movie.get('genres', [])
    runtime = movie.get('runtimes', [''])[0]
    runtime_fmt = f"{int(runtime) // 60}h {int(runtime) % 60}m" if runtime.isdigit() else ''
    return f"{year} • {'/'.join(genres)} • {runtime_fmt}"

def scrape_and_upload(n):
    ia = IMDb()
    popular = ia.get_top250_movies()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Prepare CSV writer
    file_exists = os.path.exists(CSV_FILE)
    csvfile = open(CSV_FILE, 'a', newline='', encoding='utf-8')
    fieldnames = ['movie_id', 'movie_name', 'director', 'writer', 'stars', 'description', 'poster',
                  'year_genre', 'total_weighted', 'num_ratings']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if not file_exists or os.stat(CSV_FILE).st_size == 0:
        writer.writeheader()

    added = 0

    from itertools import islice

    for movie in islice(popular, 0, None):  # keep going until added == n
        if added >= n:
            break
        try:
            ia.update(movie)
            movie_id = str(movie.movieID)
            movie_name = movie.get('title')

            # Skip if already in DB
            cursor.execute("SELECT 1 FROM movies WHERE movie_id = ?", (movie_id,))
            if cursor.fetchone():
                print(f"Skipped (Duplicate): {movie_name} [ID: {movie_id}]")
                continue

            director = ', '.join([d['name'] for d in movie.get('director', [])]) if movie.get('director') else ''
            writer_ = ', '.join([w['name'] for w in movie.get('writer', [])]) if movie.get('writer') else ''
            stars = ', '.join([a['name'] for a in movie.get('cast', [])[:3]]) if movie.get('cast') else ''
            description = movie.get('plot', [''])[0].split('::')[0] if movie.get('plot') else ''
            year_genre = format_year_genre_runtime(movie)
            poster_url = movie.get('full-size cover url') or movie.get('cover url')
            poster_name = f"{clean_filename(movie_name)}.jpg"
            poster_path = os.path.join(POSTER_DIR, poster_name)

            # Save poster
            poster_relative_path = f"movie_posters/{poster_name}" if poster_url and download_poster(poster_url, poster_path) else ""

            rating = float(movie.get('rating', 8.0))
            num_ratings = int(movie.get('votes', 1))

            # Insert to DB
            cursor.execute('''
                INSERT INTO movies (movie_id, movie_name, director, writer, stars, description, poster,
                                    year_genre, total_weighted, num_ratings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie_id, movie_name, director, writer_, stars, description, poster_relative_path,
                year_genre, rating, num_ratings
            ))
            conn.commit()

            # Append to CSV
            writer.writerow({
                'movie_id': movie_id,
                'movie_name': movie_name,
                'director': director,
                'writer': writer_,
                'stars': stars,
                'description': description,
                'poster': poster_relative_path,
                'year_genre': year_genre,
                'total_weighted': rating,
                'num_ratings': num_ratings
            })

            print(f"Uploaded: {movie_name}")
            added += 1

        except Exception as e:
            print(f"Error with {movie.get('title')}: {e}")

    csvfile.close()
    conn.close()
    print(f"\nDone. {added} movie(s) added.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scrape.py <number_of_movies>")
    else:
        scrape_and_upload(int(sys.argv[1]))

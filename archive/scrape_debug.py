import sys
import os
import csv
import sqlite3
import requests
from imdb import IMDb

DB_FILE = 'movies.db'
CSV_FILE = 'movies.csv'
POSTER_DIR = 'pictures/movie_posters'
os.makedirs(POSTER_DIR, exist_ok=True)

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
    movies = ia.get_top250_movies()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    file_exists = os.path.exists(CSV_FILE)
    csvfile = open(CSV_FILE, 'a', newline='', encoding='utf-8')
    fieldnames = ['movie_id', 'movie_name', 'director', 'writer', 'stars', 'description', 'poster',
                  'year_genre', 'total_weighted', 'num_ratings']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if not file_exists or os.stat(CSV_FILE).st_size == 0:
        writer.writeheader()

    added = 0
    for movie in movies:
        if added >= n:
            break

        print(f"🔍 Attempting: {movie}")
        try:
            ia.update(movie)

            movie_id = str(movie.movieID)
            movie_name = movie.get('title')
            print(f"🎬 Movie: {movie_name} [ID: {movie_id}]")

            director = ', '.join([d['name'] for d in movie.get('director', [])]) if movie.get('director') else ''
            writer_ = ', '.join([w['name'] for w in movie.get('writer', [])]) if movie.get('writer') else ''
            stars = ', '.join([a['name'] for a in movie.get('cast', [])[:3]]) if movie.get('cast') else ''
            description = movie.get('plot', [''])[0].split('::')[0] if movie.get('plot') else ''
            year_genre = format_year_genre_runtime(movie)
            poster_url = movie.get('full-size cover url') or movie.get('cover url')
            poster_name = f"{clean_filename(movie_name)}.jpg"
            poster_path = os.path.join(POSTER_DIR, poster_name)

            if poster_url:
                print(f"🖼 Poster URL: {poster_url}")
            else:
                print("⚠️ No poster found")

            poster_relative_path = f"movie_posters/{poster_name}" if poster_url and download_poster(poster_url, poster_path) else ""

            rating = float(movie.get('rating', 8.0))
            num_ratings = int(movie.get('votes', 1))

            print(f"📊 Rating: {rating} | Votes: {num_ratings}")
            print(f"📝 Description: {description[:60]}...")
            print(f"🧠 Director: {director} | Writer: {writer_} | Stars: {stars}")

            cursor.execute('''
                INSERT INTO movies (movie_id, movie_name, director, writer, stars, description, poster,
                                    year_genre, total_weighted, num_ratings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                movie_id, movie_name, director, writer_, stars, description, poster_relative_path,
                year_genre, rating, num_ratings
            ))
            conn.commit()

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

            print(f"✅ Uploaded: {movie_name}\n")
            added += 1

        except Exception as e:
            print(f"❌ Error with {movie.get('title') if movie else 'unknown'}: {e}\n")

    csvfile.close()
    conn.close()
    print(f"\n✔ Done. {added} movie(s) added.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scrape_debug.py <number_of_movies>")
    else:
        scrape_and_upload(int(sys.argv[1]))

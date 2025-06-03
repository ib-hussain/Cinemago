import sqlite3
import pandas as pd

CSV_FILE = 'data/movies.csv'
DB_FILE = 'data/movies.db'
TABLE_NAME = 'movies'

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Drop existing table if it has wrong schema
cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")
conn.commit()

# Create fresh table with correct schema
cursor.execute(f'''
CREATE TABLE {TABLE_NAME} (
    movie_id TEXT PRIMARY KEY,
    movie_name TEXT,
    director TEXT,
    writer TEXT,
    stars TEXT,
    description TEXT,
    poster TEXT,
    year_genre TEXT,
    total_weighted REAL,
    num_ratings INTEGER
);
''')
conn.commit()

# Rest of your code remains the same...

# Load and normalize CSV
df = pd.read_csv(CSV_FILE, encoding='ISO-8859-1')
df.columns = df.columns.str.strip().str.lower()

uploaded = 0
for _, row in df.iterrows():
    try:
        cursor.execute(f'''
            INSERT INTO {TABLE_NAME} (movie_id, movie_name, director, writer, stars, description, poster,
                                      year_genre, total_weighted, num_ratings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(row['movie_id']),
            row['movie_name'],
            row['director'],
            row['writer'],
            row['stars'],
            row['description'],
            row['poster'],
            row['year_genre'],
            float(row['total_weighted']),
            int(row['num_ratings'])
        ))
        conn.commit()
        print(f"Uploaded: {row['movie_name']}")
        uploaded += 1
    except sqlite3.IntegrityError:
        print(f"Skipped (Duplicate): {row['movie_name']}")

print(f"\nDone. Uploaded {uploaded} movies.")
conn.close()

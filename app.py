from flask import Flask, request, redirect, send_from_directory, jsonify, session
from werkzeug.utils import secure_filename
import sqlite3
import os
import webbrowser
import csv
from flask import Response
import xml.etree.ElementTree as ET
from flask_sitemap import Sitemap

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = 'something-very-secret'

DATABASE = 'data/movies.db'
users_file = 'data/users.csv'
ADMIN_EMAILS = ['ibrahimbeaconarion@gmail.com', 'i232626@isb.nu.edu.pk', 'captainkrypton123@gmail.com']

ext = Sitemap(app=app)
@app.route('/robots.txt')
def robots_txt():
    lines = [
        "User-Agent: *",
        "Disallow:",
        "Sitemap: https://cinemago.onrender.com/sitemap.xml"
    ]
    return Response("\n".join(lines), mimetype="text/plain")

@app.route('/sitemap.xml')
def sitemap_xml():
    conn = sqlite3.connect('movies.db')
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM movies")
    movies = cursor.fetchall()
    conn.close()

    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Homepage
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = "https://cinemago.onrender.com/"

    # Search page
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = "https://cinemago.onrender.com/search.html"

    # Rate page
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = "https://cinemago.onrender.com/rate.html"

    # Suggest page
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = "https://cinemago.onrender.com/suggest.html"

    # Community page
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = "https://cinemago.onrender.com/user/community.html"

    # Movie entries
    for movie in movies:
        title = movie[0].replace(" ", "-")
        movie_url = f"https://cinemago.onrender.com/movie/{title}"
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = movie_url

    xml_str = ET.tostring(urlset, encoding='utf-8', method='xml')
    return Response(xml_str, mimetype='application/xml')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def open_csv_file(filename, mode='r', encoding='utf-8'):
    try:
        return open(filename, mode, encoding=encoding)
    except:
        return open(filename, mode, encoding='utf-8')

@app.route('/')
def index():
    return redirect('/home.html')

@app.route('/signup', methods=['POST'])
def signup():
    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return jsonify({'status': 'error', 'message': 'Passwords do not match'})

    if os.path.exists(users_file):
        with open_csv_file(users_file) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2 and row[1] == email:
                    return jsonify({'status': 'error', 'message': 'Email already exists'})

    with open_csv_file(users_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow([fullname, email, password, 1])

    return jsonify({'status': 'success', 'redirect': '/login.html'})

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    if os.path.exists(users_file):
        with open_csv_file(users_file) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3 and row[1] == email and row[2] == password:
                    session['email'] = email
                    if email in ADMIN_EMAILS:
                        return jsonify({'status': 'success', 'redirect': '/admin-dashboard.html'})
                    return jsonify({'status': 'success', 'redirect': '/home.html'})
    return jsonify({'status': 'error', 'message': 'Invalid email or password'})

@app.route('/admin/upload_movie', methods=['POST'])
def upload_movie():
    data = request.form
    poster_file = request.files['poster']
    if not poster_file or not data['poster_name']:
        return jsonify({'status': 'error', 'message': 'Poster required'})

    poster_path = os.path.join('pictures/movie_posters', secure_filename(data['poster_name']))
    poster_file.save(poster_path)

    movie_id = str(abs(hash(data['movie_name'] + data['director'] + data['writer'])))[:16]

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO movies (id, title, director, year_genre_time, poster_url, rating, num_ratings)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            movie_id,
            data['movie_name'],
            data['director'],
            data['year_genre'],
            f'movie_posters/{secure_filename(data["poster_name"])}',
            float(data['rating']),
            1
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Movie already exists'})
    conn.close()
    return jsonify({'status': 'success', 'message': 'Movie uploaded successfully'})

@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    users = []
    if os.path.exists(users_file):
        with open_csv_file(users_file) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    users.append({ 'name': row[0], 'email': row[1], 'weight': row[3] })
    return jsonify({'status': 'success', 'users': users})

@app.route('/admin-dashboard.html')
def serve_admin_dashboard():
    if session.get('email') in ADMIN_EMAILS:
        return send_from_directory(app.static_folder, 'admin-dashboard.html')
    return redirect('/home.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/home.html')

@app.route('/update_weight', methods=['POST'])
def update_weight():
    data = request.get_json()
    rows = []
    updated = False
    if os.path.exists(users_file):
        with open_csv_file(users_file) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4 and row[1] == data['email']:
                    row[3] = str(data['weight'])
                    updated = True
                rows.append(row)
    if updated:
        with open_csv_file(users_file, 'w') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        return jsonify({'status': 'success', 'message': 'Weight updated'})
    return jsonify({'status': 'error', 'message': 'User not found'})

@app.route('/get_user', methods=['POST'])
def get_user():
    data = request.get_json()
    if os.path.exists(users_file):
        with open_csv_file(users_file) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4 and row[1] == data['email']:
                    return jsonify({'status': 'success', 'name': row[0], 'email': row[1], 'weight': row[3]})
    return jsonify({'status': 'error', 'message': 'User not found'})

@app.route('/get_all_movies')
def get_all_movies():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT movie_id, movie_name, poster, total_weighted AS total_weighted, num_ratings FROM movies')
    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'status': 'success', 'movies': movies})

@app.route('/get_movie', methods=['POST'])
def get_movie():
    movie_id = request.get_json().get('movie_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({'status': 'success', **dict(row)})
    return jsonify({'status': 'error', 'message': 'Movie not found'})

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    data = request.get_json()
    movie_id = data.get('movie_id')
    weighted_rating = float(data.get('weighted_rating', 0))
    num_rating = int(data.get('num_rating', 1))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT rating, num_ratings FROM movies WHERE movie_id = ?', (movie_id,))
    row = cursor.fetchone()
    if row:
        new_total = row['rating'] + weighted_rating
        new_num = row['num_ratings'] + num_rating
        cursor.execute('UPDATE movies SET rating = ?, num_ratings = ? WHERE movie_id = ?', (new_total, new_num, movie_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'total_weighted': new_total, 'num_ratings': new_num})
    conn.close()
    return jsonify({'status': 'error', 'message': 'Movie not found'})

@app.route('/admin/scrape_movies', methods=['POST'])
def scrape_movies():
    if session.get('email') not in ADMIN_EMAILS:
        return jsonify({'status': 'error', 'message': 'Unauthorized access'})

    data = request.get_json()
    count = int(data.get('count', 0))
    if count <= 0:
        return jsonify({'status': 'error', 'message': 'Invalid count'})

    import subprocess
    try:
        result = subprocess.run(['python', 'scrape_tmdb.py', str(count)], check=True, capture_output=True, text=True)
        return jsonify({'status': 'success', 'message': f"{count} movies scraped and uploaded.\n" + result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'message': 'Scraping failed:\n' + e.stderr})

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    webbrowser.open('http://cinemago.com/')
    app.run(host='0.0.0.0', port=80, debug=True)

# lt --port 80 --subdomain cinemago
# https://whatismyipaddress.com/
# 39.60.199.109

# if __name__ == "__main__":
#     app.run(debug=True)
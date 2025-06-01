from flask import Flask, request, redirect, send_from_directory, jsonify
import csv
import os

app = Flask(__name__, static_folder='.', static_url_path='')

users_file = 'user/users.csv'
movies_file = 'movies.csv'
if True:
    ADMIN_EMAILS = ['ibrahimbeaconarion@gmail.com', 'i232626@isb.nu.edu.pk', 'captainkrypton123@gmail.com']
from flask import session
app.secret_key = 'something-very-secret'

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
        with open(users_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2 and row[1] == email:
                    return jsonify({'status': 'error', 'message': 'Email already exists'})

    # Default weight = 1 if not provided during signup
    with open(users_file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([fullname, email, password, 1])

    return jsonify({'status': 'success', 'redirect': '/login.html'})

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3 and row[1] == email and row[2] == password:
                    session['email'] = email  # ✅ store it server-side!
                    if email in ADMIN_EMAILS:
                        return jsonify({'status': 'success', 'redirect': '/admin-dashboard.html'})
                    return jsonify({'status': 'success', 'redirect': '/home.html'})
    return jsonify({'status': 'error', 'message': 'Invalid email or password'})
from werkzeug.utils import secure_filename
@app.route('/admin/upload_movie', methods=['POST'])
def upload_movie():
    movie_name = request.form['movie_name']
    year_genre = request.form['year_genre']
    rating = request.form['rating']
    description = request.form['description']
    director = request.form['director']
    writer_ = request.form['writer']
    stars = request.form['stars']
    # movie_id = request.form['movie_id']
    poster_name = request.form['poster_name']
    poster_file = request.files['poster']
    if not poster_file or not poster_name:
        return jsonify({'status': 'error', 'message': 'Poster required'})
    # Save poster
    safe_filename = secure_filename(poster_name)
    poster_path = os.path.join('pictures', safe_filename)
    poster_file.save(poster_path)
    # Generate movie_id
    movie_id = str(abs(hash(movie_name + director + writer_)))[:8]
    new_row = {
        'movie_id': movie_id,
        'movie_name': movie_name,
        'director': director,
        'writer': writer_,
        'stars': stars,
        'description': description,
        'poster': f'movie_posters/{safe_filename}',
        'year_genre': year_genre,
        'total_weighted': rating,
        'num_ratings': 1
    }
    # Write to movies.csv
    file_exists = os.path.exists(movies_file)
    with open(movies_file, 'a', newline='') as f:
        fieldnames = new_row.keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if os.stat(movies_file).st_size == 0:  # Write header if file empty
            writer.writeheader()
        writer.writerow(new_row)
    return jsonify({'status': 'success', 'message': 'Movie uploaded successfully'})
@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    users = []
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    users.append({
                        'name': row[0],
                        'email': row[1],
                        'weight': row[3]
                    })
    return jsonify({'status': 'success', 'users': users})

@app.route('/admin-dashboard.html')
def serve_admin_dashboard():
    email = session.get('email')
    if email and email in ADMIN_EMAILS:
        return send_from_directory(app.static_folder, 'admin-dashboard.html')
    return redirect('/home.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/home.html')

@app.route('/update_weight', methods=['POST'])
def update_weight():
    data = request.get_json()
    target_email = data.get('email')
    new_weight = str(data.get('weight'))
    if not target_email or not new_weight:
        return jsonify({'status': 'error', 'message': 'Invalid input'})
    rows = []
    updated = False
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4 and row[1] == target_email:
                    row[3] = new_weight
                    updated = True
                rows.append(row)
    if updated:
        with open(users_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        return jsonify({'status': 'success', 'message': 'Weight updated'})
    else:
        return jsonify({'status': 'error', 'message': 'User not found'})

@app.route('/get_user', methods=['POST'])
def get_user():
    data = request.get_json()
    email = data.get('email')

    if os.path.exists(users_file) and email:
        with open(users_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4 and row[1] == email:
                    return jsonify({
                        'status': 'success',
                        'name': row[0],
                        'email': row[1],
                        'weight': row[3]
                    })

    return jsonify({'status': 'error', 'message': 'User not found'})

@app.route('/get_all_movies', methods=['GET'])
def get_all_movies():
    movies = []
    if os.path.exists(movies_file):
        with open(movies_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                movies.append({
                    'movie_id': row['movie_id'],
                    'movie_name': row['movie_name'],
                    'poster': row['poster'],
                    'total_weighted': row['total_weighted'],
                    'num_ratings': row['num_ratings']
                })
    return jsonify({'status': 'success', 'movies': movies})

@app.route('/get_movie', methods=['POST'])
def get_movie():
    data = request.get_json()
    movie_id = data.get('movie_id')

    if os.path.exists(movies_file) and movie_id:
        with open(movies_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['movie_id'] == movie_id:
                    return jsonify({
                        'status': 'success',
                        'movie_id': row['movie_id'],
                        'movie_name': row['movie_name'],
                        'director': row['director'],
                        'writer': row['writer'],
                        'stars': row['stars'],
                        'description': row['description'],
                        'poster': row['poster'],
                        'year_genre': row['year_genre'],
                        'total_weighted': float(row['total_weighted']),
                        'num_ratings': int(row['num_ratings'])
                    })
    return jsonify({'status': 'error', 'message': 'Movie not found'})

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    data = request.get_json()
    movie_id = data.get('movie_id')
    weighted_rating = float(data.get('weighted_rating', 0))
    num_rating = int(data.get('num_rating', 1))

    if (not movie_id) or (weighted_rating < 0):
        return jsonify({'status': 'error', 'message': 'Invalid data'})

    rows = []
    updated_movie = None

    if os.path.exists(movies_file):
        with open(movies_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['movie_id'] == movie_id:
                    row['total_weighted'] = str(float(row['total_weighted']) + weighted_rating)
                    row['num_ratings'] = str(int(row['num_ratings']) + num_rating)
                    updated_movie = row
                rows.append(row)

    if updated_movie:
        with open(movies_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        return jsonify({
            'status': 'success',
            'total_weighted': float(updated_movie['total_weighted']),
            'num_ratings': int(updated_movie['num_ratings'])
        })
    else:
        return jsonify({'status': 'error', 'message': 'Movie not found'})

# if __name__ == "__main__":
#     webbrowser.open('http://cinemago.com/')
#     app.run(host='127.0.0.1', port=80, debug=True)

import webbrowser
if __name__ == "__main__":
    webbrowser.open('http://cinemago.com/')
    app.run(host='0.0.0.0', port=80, debug=True)
# lt --port 80 --subdomain cinemago
# https://whatismyipaddress.com/
# 39.60.199.109
# if __name__ == "__main__":
#     app.run(debug=True)

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(app.static_folder, path)


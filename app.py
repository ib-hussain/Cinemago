from flask import Flask, request, redirect, send_from_directory, jsonify
import csv
import os

app = Flask(__name__, static_folder='.', static_url_path='')

users_file = 'user/users.csv'
movies_file = 'movies.csv'

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
                    return jsonify({'status': 'success', 'redirect': '/home.html'})

    return jsonify({'status': 'error', 'message': 'Invalid email or password'})

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

import webbrowser
# if __name__ == "__main__":
#     webbrowser.open('http://cinemago.com/')
#     app.run(host='127.0.0.1', port=80, debug=True)

# if __name__ == "__main__":
#     webbrowser.open('http://cinemago.com/')
#     app.run(host='0.0.0.0', port=80, debug=True)
# lt --port 80 --subdomain cinemago
# https://whatismyipaddress.com/
# 39.60.199.109
if __name__ == "__main__":
    app.run(debug=True)

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(app.static_folder, path)


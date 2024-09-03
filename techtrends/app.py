import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import threading
import logging
import sys



active_connections = 0
active_connections_lock = threading.Lock()

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global active_connections
    with active_connections_lock:
        active_connections += 1

    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error('Article with ID: %d did not exist', post_id)
      return render_template('404.html'), 404
    else:
      app.logger.info('Existed post with title: %s', post['title'])
      return render_template('post.html', post=post)

# Define the About Us pagegit s
@app.route('/about')
def about():
    app.logger.info('About page was accessed')    
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('New post created with title: %s', title)

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def status():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    totalPost = connection.execute('SELECT count(*) FROM posts').fetchone()
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count":active_connections,"post_count":totalPost[0]}}),
            status=200,
            mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler("app.log"), logging.StreamHandler(sys.stdout), logging.StreamHandler(sys.stderr)])
   app.run(host='0.0.0.0', port='3111')

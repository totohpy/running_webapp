from flask import Flask, render_template, request, redirect, url_for, session
from bson import ObjectId

from db import init_db
from db import get_all_posts, get_post, get_post_comments
from db import create_post, create_comment, delete_post, update_post
from db import get_user_from_username

from functools import wraps

app = Flask(__name__)
app.config.from_object('settings')

init_db(app.config['DB_HOST'],
        app.config['DB_NAME'],
        app.config['DB_USER'],
        app.config['DB_PASSWORD'])

def get_user_from_session():
    if 'username' in session:
        return get_user_from_username(session['username'])
    else:
        return None

def login_required(f):
    @wraps(f)
    def view(*args, **kwargs):
        user = get_user_from_session()
        if user:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
    return view

@app.route("/")
def index():
    user = get_user_from_session()
    posts = get_all_posts()
    return render_template("index.html", 
                           posts=posts,
                           user=user)

def check_password(username, password):
    import hashlib

    user = get_user_from_username(username)
    if user:
        hashed_password = hashlib.sha1((user['salt'] + password).encode()).hexdigest()
        return hashed_password == user['hashed_password']
    else:
        return False

@app.route("/login/", methods=['GET','POST'])
def login():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if check_password(username, password):
            session['username'] = username
            return redirect(url_for('index'))
        
        error_message = 'Incorrect password'

    return render_template('login.html',
                           error_message=error_message)

@app.route("/logout/")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
    
@app.route("/posts/new/", methods=['GET','POST'])
@login_required
def new_post():
    user = get_user_from_session()
    if request.method == 'POST':
        title = request.form['date']
        body1 = request.form['distance']
        body2 = request.form['time']

        owner = user

        create_post(title, body1, body2, owner)

        return redirect(url_for('index'))

    return render_template("new_post.html")

@app.route("/posts/<post_id>/")
def show_post(post_id):
    object_id = ObjectId(post_id)
    post = get_post(object_id)
    comments = get_post_comments(object_id)

    return render_template('show_post.html', 
        post=post, 
        comments=comments)

@app.route("/posts/<post_id>/delete/")
def del_post(post_id):
    object_id = ObjectId(post_id)
    delete_post(object_id)
    return redirect(url_for('index'))

@app.route("/posts/<post_id>/edit/", methods=['GET','POST'])
@login_required
def edit_post(post_id):
    object_id = ObjectId(post_id)

    user = get_user_from_session()
    post = get_post(object_id)
    if ('owner_id' not in post) or (post['owner_id'] != user['_id']):
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['date']
        body1 = request.form['distance']
        body2 = request.form['time']

        update_post(object_id, title, body1, body2)

        return redirect("/posts/" + post_id + "/")

    return render_template("edit_post.html", post=post)

@app.route("/posts/<post_id>/comments/new/", methods=['POST'])
@login_required
def add_comment(post_id):
    message = request.form['message']
    post_object_id = ObjectId(post_id)
    create_comment(post_object_id, message)

    return redirect("/posts/" + post_id + "/")

app.run(debug=True, port=8000)
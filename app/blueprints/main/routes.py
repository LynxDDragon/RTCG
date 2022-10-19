import imghdr
import os
from config import Config
from . import bp as app
from flask import Flask ,render_template, request, redirect, url_for, flash, abort, send_from_directory
from app.blueprints.main.models import User, Post
from app import db
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename


# Routes that return/display HTML

@app.route('/')
@login_required
def home():
    posts = Post.query.all()
    return render_template('home.html', user=current_user, posts=posts)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.all()
    return render_template('profile.html', user=user, posts=posts)

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

@app.route('/post', methods=['POST'])
@login_required
def create_post():
    post_title = request.form['title']
    post_body = request.form['body']
    
    new_post = Post(title=post_title, body=post_body, user_id=current_user.id)

    db.session.add(new_post)
    db.session.commit()

    flash('Post added successfully', 'success')
    return redirect(url_for('main.home'))

@app.route('/post/<id>')
def post(id):
    single_post = Post.query.get(id)
    return render_template('single-post.html', post=single_post)





def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('home.html', files=files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def upload(filename):

    return send_from_directory(app.config['UPLOAD_PATH'], filename)
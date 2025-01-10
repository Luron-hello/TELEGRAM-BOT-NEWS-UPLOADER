from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, News, Comment
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///news.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/flask_app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask app startup')

with app.app_context():
    db.create_all()

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error('Server Error: %s', (error))
    return "Internal Server Error", 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error('Unhandled Exception: %s', (e))
    return "Internal Server Error", 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Username and password are required')
            return redirect(url_for('register'))

        app.logger.debug(f'Received registration data - Username: {username}, Password: {password}')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('You are now registered and can log in')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/')
def home():
    news_list = News.query.all()
    return render_template('index.html', news_list=news_list, username=session.get('username'))

@app.route('/news/<news_id>', methods=['GET', 'POST'])
def news_detail(news_id):
    news_item = News.query.get_or_404(news_id)

    if request.method == 'POST':
        comment_text = request.form.get('comment')
        user_id = session.get('user_id')
        if user_id and comment_text:
            new_comment = Comment(news_id=news_id, user_id=user_id, comment=comment_text)
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added successfully')
        else:
            flash('Failed to add comment')

    comments = Comment.query.filter_by(news_id=news_id).all()
    return render_template('news_detail.html', news=news_item, comments=comments, username=session.get('username'))

@app.route('/edit_comment/<comment_id>', methods=['POST'])
def edit_comment(comment_id):
    new_comment_text = request.form.get('comment')
    user_id = session.get('user_id')

    comment = Comment.query.filter_by(id=comment_id, user_id=user_id).first()
    if comment:
        comment.comment = new_comment_text
        db.session.commit()
        flash('Comment updated successfully')
    else:
        flash('Comment not found or you do not have permission to edit this comment')

    return redirect(request.referrer)

@app.route('/delete_comment/<comment_id>', methods=['POST'])
def delete_comment(comment_id):
    user_id = session.get('user_id')

    comment = Comment.query.filter_by(id=comment_id, user_id=user_id).first()
    if comment:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully')
    else:
        flash('Comment not found or you do not have permission to delete this comment')

    return redirect(request.referrer)

@app.route('/add_news', methods=['POST'])
def add_news():
    news_id = request.form['id']
    news_title = request.form['title']
    news_description = request.form['description']
    news_text = request.form['text']
    photo = request.files['photo']
    photo_filename = f"{news_id}_photo"
    photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    new_news = News(id=news_id, title=news_title, description=news_description, text=news_text, photo_filename=photo_filename)
    db.session.add(new_news)
    db.session.commit()

    return '', 204

@app.route('/update_news', methods=['POST'])
def update_news():
    news_id = request.form['id']
    new_text = request.form['text']

    news_item = News.query.get_or_404(news_id)
    news_item.text = new_text
    db.session.commit()

    return '', 204

@app.route('/delete_news', methods=['POST'])
def delete_news():
    news_id = request.form['id']

    news_item = News.query.get_or_404(news_id)
    db.session.delete(news_item)
    db.session.commit()

    return '', 204

if __name__ == '__main__':
    app.run(debug=True)

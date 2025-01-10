# import telebot
# import requests
# import random
# import string
# from telebot import types
#
# bot = telebot.TeleBot("6491224773:AAGxNAVpDNxm6nUms2l-3IjMghZ0AzNitD8")
# flask_server_url = "http://127.0.0.1:5000"
#
# @bot.message_handler(commands=['start'])
# def start_message(message):
#     markup = types.ReplyKeyboardMarkup()
#     btn_1 = types.KeyboardButton('Добавление новости')
#     btn_2 = types.KeyboardButton('Редактирование новости')
#     btn_3 = types.KeyboardButton('Удаление новости')
#     markup.row(btn_1, btn_2, btn_3)
#     bot.send_message(message.chat.id, 'Здравствуйте! Я бот для загрузки новостей на наш сайт. Для продолжения выберите команду и напишите ваш текст новости.', reply_markup=markup)
#
# @bot.message_handler(func=lambda message: True)
# def handle_message(message):
#     user_text = message.text
#     if user_text.lower() == "добавление новости":
#         bot.send_message(message.chat.id, "Введите название новости:")
#         bot.register_next_step_handler(message, get_news_title)
#     elif user_text.lower() == "редактирование новости":
#         bot.send_message(message.chat.id, "Введите ID новости, которую нужно отредактировать:")
#         bot.register_next_step_handler(message, edit_news)
#     elif user_text.lower() == "удаление новости":
#         bot.send_message(message.chat.id, "Введите ID новости, которую нужно удалить:")
#         bot.register_next_step_handler(message, delete_news)
#     else:
#         bot.reply_to(message, f"Принято: {user_text}")
#
# def get_news_title(message):
#     news_title = message.text
#     bot.send_message(message.chat.id, "Отправьте фото для новости:")
#     bot.register_next_step_handler(message, get_news_photo, news_title)
#
# def get_news_photo(message, news_title):
#     if message.photo:
#         file_info = bot.get_file(message.photo[-1].file_id)
#         photo = bot.download_file(file_info.file_path)
#         bot.send_message(message.chat.id, "Введите краткое описание новости:")
#         bot.register_next_step_handler(message, get_news_description, news_title, photo)
#     else:
#         bot.send_message(message.chat.id, "Пожалуйста, отправьте фото.")
#         bot.register_next_step_handler(message, get_news_photo, news_title)
#
# def get_news_description(message, news_title, photo):
#     news_description = message.text
#     bot.send_message(message.chat.id, "Введите полный текст новости:")
#     bot.register_next_step_handler(message, get_news_text, news_title, photo, news_description)
#
# def get_news_text(message, news_title, photo, news_description):
#     news_text = message.text
#     news_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
#     response = requests.post(flask_server_url + '/add_news', data={'id': news_id, 'title': news_title, 'description': news_description, 'text': news_text}, files={'photo': photo})
#     if response.status_code == 204:
#         bot.send_message(message.chat.id, f"Новость добавлена с ID: {news_id}")
#     else:
#         bot.send_message(message.chat.id, "Произошла ошибка при добавлении новости")
#
# def edit_news(message):
#     news_id = message.text
#     bot.send_message(message.chat.id, "Введите новый текст новости:")
#     bot.register_next_step_handler(message, update_news, news_id)
#
# def update_news(message, news_id):
#     new_text = message.text
#     requests.post(flask_server_url + '/update_news', data={'id': news_id, 'text': new_text})
#     bot.send_message(message.chat.id, f"Новость с ID {news_id} успешно отредактирована")
#
# def delete_news(message):
#     news_id = message.text
#     requests.post(flask_server_url + '/delete_news', data={'id': news_id})
#     bot.send_message(message.chat.id, f"Новость с ID {news_id} успешно удалена")
#
# bot.polling()
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
from flask import Flask, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash

app = Flask(__name__)

@app.route('/create_admin', methods=['GET'])
def create_admin():
    username = "Admin"
    password = "admin_password"  # Убедитесь, что это сложный пароль
    hashed_password = generate_password_hash(password, method='sha256')
    admin_user = User(username=username, password=hashed_password)
    db.session.add(admin_user)
    db.session.commit()
    return "Admin created"

if __name__ == "__main__":
    app.run(debug=True)

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

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get('username') != 'Admin':
        abort(403)
    users = User.query.all()
    news = News.query.all()
    return render_template('admin_dashboard.html', users=users, news=news)

@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('username') != 'Admin':
        abort(403)

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('admin'))

@app.route('/delete_news/<news_id>', methods=['POST'])
def admin_delete_news(news_id):
    if session.get('username') != 'Admin':
        abort(403)

    news_item = News.query.get_or_404(news_id)
    db.session.delete(news_item)
    db.session.commit()

    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)

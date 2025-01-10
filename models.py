# from flask_sqlalchemy import SQLAlchemy
#
# db = SQLAlchemy()
#
# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     comments = db.relationship('Comment', backref='user', lazy=True)
#
# class News(db.Model):
#     id = db.Column(db.String(8), primary_key=True)
#     title = db.Column(db.String(120), nullable=False)
#     description = db.Column(db.String(250), nullable=False)
#     text = db.Column(db.Text, nullable=False)
#     photo_filename = db.Column(db.String(100), nullable=True)
#     comments = db.relationship('Comment', backref='news', lazy=True)
#
# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     news_id = db.Column(db.String(8), db.ForeignKey('news.id'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     comment = db.Column(db.Text, nullable=False)
#
#
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    comments = db.relationship('Comment', backref='user', lazy=True)

class News(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    text = db.Column(db.Text, nullable=False)
    photo_filename = db.Column(db.String(100), nullable=False)
    comments = db.relationship('Comment', backref='news', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.String(10), db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)



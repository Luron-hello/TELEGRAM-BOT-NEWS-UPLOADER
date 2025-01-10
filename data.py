# import sqlite3
#
# def init_db():
#     conn = sqlite3.connect('news.db')
#     cursor = conn.cursor()
#
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS user (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         username TEXT NOT NULL UNIQUE,
#         password TEXT NOT NULL
#     )
#     ''')
#
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS news (
#         id TEXT PRIMARY KEY,
#         title TEXT NOT NULL,
#         description TEXT NOT NULL,
#         text TEXT NOT NULL,
#         photo_filename TEXT NOT NULL
#     )
#     ''')
#
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS comments (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         news_id TEXT NOT NULL,
#         user_id INTEGER NOT NULL,
#         comment TEXT NOT NULL,
#         FOREIGN KEY (news_id) REFERENCES news (id),
#         FOREIGN KEY (user_id) REFERENCES user (id)
#     )
#     ''')
#
#     conn.commit()
#     conn.close()
#
# if __name__ == '__main__':
#     init_db()
#
#
import requests

flask_server_url = "http://127.0.0.1:5000"

def delete_news(news_id):
    response = requests.post(f"{flask_server_url}/delete_news", data={"id": news_id})
    return response.status_code == 204

def delete_user(user_id):
    response = requests.post(f"{flask_server_url}/delete_user/{user_id}")
    return response.status_code == 204

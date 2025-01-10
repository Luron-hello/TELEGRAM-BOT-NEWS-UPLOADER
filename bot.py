import telebot
import requests
import random
import string
from telebot import types

bot = telebot.TeleBot("YOUR_BOT_API_KEY")
flask_server_url = "http://127.0.0.1:5000"

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup()
    btn_1 = types.KeyboardButton('Добавление новости')
    btn_2 = types.KeyboardButton('Редактирование новости')
    btn_3 = types.KeyboardButton('Удаление новости')
    markup.row(btn_1, btn_2, btn_3)
    bot.send_message(message.chat.id, 'Здравствуйте! Я бот для загрузки новостей на наш сайт. Для продолжения выберите команду и напишите ваш текст новости.', reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_text = message.text
    if user_text.lower() == "добавление новости":
        bot.send_message(message.chat.id, "Введите название новости:")
        bot.register_next_step_handler(message, get_news_title)
    elif user_text.lower() == "редактирование новости":
        bot.send_message(message.chat.id, "Введите ID новости, которую нужно отредактировать:")
        bot.register_next_step_handler(message, get_news_id_for_edit)
    elif user_text.lower() == "удаление новости":
        bot.send_message(message.chat.id, "Введите ID новости, которую нужно удалить:")
        bot.register_next_step_handler(message, get_news_id_for_delete)
    else:
        bot.send_message(message.chat.id, "Я не понимаю эту команду. Попробуйте снова.")

def get_news_title(message):
    news_title = message.text
    bot.send_message(message.chat.id, "Введите описание новости:")
    bot.register_next_step_handler(message, get_news_description, news_title)

def get_news_description(message, news_title):
    news_description = message.text
    bot.send_message(message.chat.id, "Введите текст новости:")
    bot.register_next_step_handler(message, get_news_text, news_title, news_description)

def get_news_text(message, news_title, news_description):
    news_text = message.text
    bot.send_message(message.chat.id, "Отправьте фото новости:")
    bot.register_next_step_handler(message, get_news_photo, news_title, news_description, news_text)

def get_news_photo(message, news_title, news_description, news_text):
    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    photo_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + ".jpg"
    with open(f"static/uploads/{photo_filename}", 'wb') as new_file:
        new_file.write(downloaded_file)

    news_data = {
        "id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
        "title": news_title,
        "description": news_description,
        "text": news_text,
        "photo_filename": photo_filename
    }

    response = requests.post(f"{flask_server_url}/add_news", data=news_data)
    if response.status_code == 204:
        bot.send_message(message.chat.id, "Новость успешно добавлена!")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при добавлении новости.")

def get_news_id_for_edit(message):
    news_id = message.text
    bot.send_message(message.chat.id, "Введите новый текст новости:")
    bot.register_next_step_handler(message, edit_news_text, news_id)

def edit_news_text(message, news_id):
    new_text = message.text
    response = requests.post(f"{flask_server_url}/update_news", data={"id": news_id, "text": new_text})
    if response.status_code == 204:
        bot.send_message(message.chat.id, "Новость успешно отредактирована!")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при редактировании новости.")

def get_news_id_for_delete(message):
    news_id = message.text
    response = requests.post(f"{flask_server_url}/delete_news", data={"id": news_id})
    if response.status_code == 204:
        bot.send_message(message.chat.id, "Новость успешно удалена!")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при удалении новости.")

bot.polling()

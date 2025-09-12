from telebot import *
from dotenv import load_dotenv
import re
import os
import wikipedia
import requests

wikipedia.set_lang('ru')

load_dotenv()

BOT_API = os.getenv('BOT_API')
NASA_API = os.getenv('NASA_API')
NASA_URL = os.getenv('NASA_URL')

def get_apod(count):
    try:
        response = requests.get(NASA_URL, params={'api_key': NASA_API, 'hd': True, 'count': (count if count <= 5 else 5)})
        response.raise_for_status()
        data = response.json()
        print(data)
        return data
    except requests.exceptions.HTTPError as err:
        print(err)
        return None

bot = TeleBot(BOT_API)

instance = dict()

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
keyboard.row(types.KeyboardButton('Космос'), types.KeyboardButton('Калькулятор'), types.KeyboardButton('Википедия'))

exit_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
exit_keyboard.row(types.KeyboardButton('Назад'))

@bot.message_handler(commands=['start'])
def start(message):
    instance[message.chat.id] = 'menu'
    bot.send_message(message.chat.id, 'Привет! Выбери режим: ', reply_markup=keyboard)

@bot.message_handler()
def text(message):
    try:
        if message.text == 'Назад':
            instance[message.chat.id] = 'menu'
            bot.send_message(message.chat.id, 'Выбери режим: ', reply_markup=keyboard)
            return
        elif instance[message.chat.id] == 'space':
            try:
                for item in get_apod(int(message.text)):
                    bot.send_message(message.chat.id, item['title'])
                    bot.send_message(message.chat.id, item['explanation'])
                    bot.send_photo(message.chat.id, item['hdurl'])
            except:
                bot.send_message(message.chat.id, 'Что-то пошло не так', reply_markup=exit_keyboard)
        elif instance[message.chat.id] == 'calc':
            try:
                bot.send_message(message.chat.id, eval(message.text), reply_markup=exit_keyboard)
            except:
                bot.send_message(message.chat.id, 'Что-то пошло не так', reply_markup=exit_keyboard)
        elif instance[message.chat.id] == 'wiki':
            try:
                bot.send_message(message.chat.id, wikipedia.summary(message.text), reply_markup=exit_keyboard)
            except:
                bot.send_message(message.chat.id, 'Что-то пошло не так', reply_markup=exit_keyboard)
        elif message.text == 'Космос':
            instance[message.chat.id] = 'space'
            bot.send_message(message.chat.id, 'Включён режим "Космос". Введите количество изображений (1-5):', reply_markup=exit_keyboard)
        elif message.text == 'Калькулятор':
            instance[message.chat.id] = 'calc'
            bot.send_message(message.chat.id, 'Включён режим "Калькулятор". Введите выражение:', reply_markup=exit_keyboard)
        elif message.text == 'Википедия':
            instance[message.chat.id] = 'wiki'
            bot.send_message(message.chat.id, 'Включён режим "Википедия". Введите термин:', reply_markup=exit_keyboard)
        else:
            bot.send_message(message.chat.id, 'Выбери режим: ', reply_markup=keyboard)
    except:
        instance[message.chat.id] = 'menu'
        bot.send_message(message.chat.id, 'Выбери режим: ', reply_markup=keyboard)
        

bot.polling(none_stop = True)
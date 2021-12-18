from aiogram.types import *

max_price_question_kb = InlineKeyboardMarkup()
max_price_question_kb.add(InlineKeyboardButton('Да', callback_data='max_price_question_yes'))
max_price_question_kb.add(InlineKeyboardButton('Нет', callback_data='max_price_question_no'))

guessed_city_kb = InlineKeyboardMarkup()
guessed_city_kb.add(InlineKeyboardButton('Да', callback_data='guessed_city_yes'))
guessed_city_kb.add(InlineKeyboardButton('Нет', callback_data='guessed_city_no'))

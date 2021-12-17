from aiogram.types import *


max_price_question_yes = InlineKeyboardButton('Да', callback_data='max_price_question_yes')
max_price_question_no = InlineKeyboardButton('Нет', callback_data='max_price_question_no')
max_price_question_kb = InlineKeyboardMarkup()
max_price_question_kb.add(max_price_question_yes)
max_price_question_kb.add(max_price_question_no)

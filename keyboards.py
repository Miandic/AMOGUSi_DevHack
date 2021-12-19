from aiogram.types import *

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.row(KeyboardButton('Добавить в отслеживаемое'))
main_kb.row(KeyboardButton('Просмотреть список отслеживаемого'))

max_price_question_kb = InlineKeyboardMarkup()
max_price_question_kb.add(InlineKeyboardButton('Да', callback_data='max_price_question_yes'))
max_price_question_kb.add(InlineKeyboardButton('Нет', callback_data='max_price_question_no'))

guessed_city_kb = InlineKeyboardMarkup()
guessed_city_kb.add(InlineKeyboardButton('Да', callback_data='guessed_city_yes'))
guessed_city_kb.add(InlineKeyboardButton('Нет', callback_data='guessed_city_no'))

def shops_kb(shops):
    kb = InlineKeyboardMarkup()
    for i in range(0, len(shops), 2):
        kb.row(InlineKeyboardButton(f'{shops[i][0]} {"✅" if shops[i][2] else "❌"}', callback_data=f'shops_{shops[i][1]}_switch'),
               InlineKeyboardButton(f'{shops[i + 1][0]} {"✅" if shops[i + 1][2] else "❌"}', callback_data=f'shops_{shops[i + 1][1]}_switch'))
    kb.row(InlineKeyboardButton('Продолжить', callback_data='shops_continue'))
    return kb

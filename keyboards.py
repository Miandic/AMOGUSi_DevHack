from aiogram.types import *
import json


with open('cities.json', encoding='utf-8') as f:
    cities_orig = json.loads(f.read())
    cities = [i.lower() for i in cities_orig]

SHOP_NAMES = {
    'dns': 'ДНС',
    'regard': 'Регард',
    'citilink': 'Ситилинк',
    'eldorado': 'Эльдорадо'
}

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


def watchlist_kb(watchlist):
    kb = InlineKeyboardMarkup()
    for item in watchlist:
        if item[3] == 1000000000:
            text = f'{item[1]} — [{SHOP_NAMES[item[4]]}, {cities_orig[cities.index(item[2])]}]'
        else:
            text = f'{item[1]} — [{SHOP_NAMES[item[4]]}, {cities_orig[cities.index(item[2])]}, {item[3]}р.]'
        kb.row(InlineKeyboardButton(text, callback_data=f'remove_{item[1]}_{item[2]}_{item[3]}_{item[4]}'))
    return kb


def confirm_remove_kb(data):
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton('Удалить!', callback_data=data))
    kb.row(InlineKeyboardButton('Отменить', callback_data='cancel_remove'))
    return kb


"""def watchlist_cities_kb(watchlist):
    kb = InlineKeyboardMarkup()
    cities = set(i[2] for i in watchlist)
    print(cities)
    for city in cities:
        kb.row(InlineKeyboardButton(city, callback_data=f'watchlist_city_{cities.index(city)}'), InlineKeyboardButton('❌', callback_data=f'remove_city_{cities.index(city)}'))
    return kb


def watchlist_shops_kb(watchlist):
    kb = InlineKeyboardMarkup()
    shops = set(i[4] for i in watchlist)
    print(shops)
    for shop in shops:
        kb.row(InlineKeyboardButton(SHOP_NAMES[shop], callback_data=f'watchlist_city_{shop}'), InlineKeyboardButton('❌', callback_data=f'remove_shop_{shop}'))
    return kb


def watchlist_items_kb(watchlist):
    kb = InlineKeyboardMarkup()
    items = [i[1] for i in watchlist]
    print(items)
    for item in items:
        kb.row(InlineKeyboardButton(f'{item} [MAX {}]', callback_data=f'watchlist_city_{cities.index(city)}'), InlineKeyboardButton('❌', callback_data=f'remove_city_{cities.index(city)}'))
    return kb"""

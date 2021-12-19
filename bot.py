import logging
import sqlite3
import json
from aiogram import Bot, Dispatcher, executor, types
from difflib import SequenceMatcher
from keyboards import *


API_TOKEN = '5072037847:AAEjOjkfrfrDtPqvr-o5adqlNTgb3NdPY2U'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

con = sqlite3.connect('users.db')
cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Users
               (id INTEGER, item TEXT, city TEXT, max_price INTEGER, shop TEXT)''')

users = {}

SHOPS = [
    ['ДНС', 'dns', True], ['Регард', 'regard', True],
    ['Ситилинк', 'citilink', True], ['Эльдорадо', 'eldorado', True],
]

with open('cities.json', encoding='utf-8') as f:
    cities = json.loads(f.read())

with open('dns_cities.json', encoding='utf-8') as f:
    dns_cities = json.loads(f.read())


def find_similar(s):
    most_similar = 0
    city = ''

    s = s.lower()

    for i in cities:
        if s == i.lower():
            return True
        if most_similar < SequenceMatcher(lambda x: x==" ", i.lower(), s).ratio():
            most_similar = SequenceMatcher(lambda x: x==" ", i.lower(), s).ratio()
            city = i

    if SequenceMatcher(lambda x: x==" ", city.lower(), s).ratio() < 0.8:
        return False
    return city


def send_json():
    cur.execute(f'SELECT city from Users')
    cities = cur.fetchall()
    j = {}

    for city in cities:
        cur.execute(f'SELECT item from Users WHERE city = "{city[0]}"')
        items = list(set([i[0] for i in cur.fetchall()]))
        j[city[0]] = items

    print(j)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(j, f, ensure_ascii=False)


def add_watching(id, item, city, max_price, shop):
    cur.execute(f'INSERT INTO Users VALUES ({id}, "{item}", "{city}", {max_price}, "{shop}")')
    send_json()


@dp.message_handler(commands=['start', 'cancel'])
async def send_welcome(msg: types.Message):
    await msg.answer('Привет, я парсер Bot!')
    await msg.answer('Укажите город в котором вы ищите видеокарту (или ближаший крупный к вам).')
    users[msg['from']['id']] = ['city', '', '', None]


@dp.message_handler()
async def echo(msg: types.Message):
    id, tx = msg['from'].id, msg.text
    print(id, tx)

    if id not in users:
        await send_welcome(msg)
        return

    user = users[id]

    if user[0] == 'city':
        city = find_similar(tx)
        if city == False:
            await msg.answer('Я не могу найти такой город. Попробуйте еще раз!\nНачать заново: /cancel')
        elif city == True:
            if tx.lower() in dns_cities:
                await msg.answer('Какую видеокарту вы ищите?\nНачать заново: /cancel')
                user[0] = 'item'
                user[2] = tx.lower()
            else:
                await msg.answer('Я не могу найти такой ААА АДНС КТ ДНС НЕТУ В ДНС. Попробуйте еще раз!\nНачать заново: /cancel')
        else:
            await msg.answer(f'Вы хотели ввести этот город: {city}\nВерно?\nНачать заново: /cancel', reply_markup=guessed_city_kb)
            user[2] = city.lower()

    elif user[0] == 'item':
        await msg.answer('Если нужно, выберите предпочтительные сети магазинов', reply_markup=shops_kb(SHOPS))
        user[3] = SHOPS[:]
        user[1] = tx

    elif user[0] == 'max_price':
        if set(tx) <= set('0123456789') and int(tx) < 10000000:
            for i in user[3]:
                if i[2]:
                    add_watching(id, user[1], user[2], int(tx), i[1])
            await msg.answer('Мы начали поиски вашей видеокарты.(^_^)\nНачать заново: /start')
            users[id] = ['', '', '', None]
        else:
            await msg.answer('Некорректно введена стоимость.')


@dp.callback_query_handler()
async def handle_callback(query: types.CallbackQuery):
    id = query.from_user.id
    user = users[id]
    print(query.data)

    if query.data == 'max_price_question_yes':
        await bot.send_message(id, 'Введите максимальную допуcтимую стоимость (в рублях)\nНачать заново: /cancel')
        user[0] = 'max_price'
        await query.answer()

    elif query.data == 'max_price_question_no':
        for i in user[3]:
            if i[2]:
                add_watching(id, user[1], user[2], 1000000000, i[1])
        await bot.send_message(id, 'Мы начали поиски вашей видеокарты.(^_^)\nНачать заново: /start')
        users[id] = ['', '', '', None]

    elif query.data == 'guessed_city_yes':
        if user[2].lower() in dns_cities:
            await bot.send_message(id, 'Какую видеокарту вы ищите?\nНачать заново: /cancel')
            user[0] = 'item'
        else:
            await bot.send_message(id, 'Я не могу найти такой ААА АДНС КТ ДНС НЕТУ В ДНС. Попробуйте еще раз!\nНачать заново: /cancel')

    elif query.data == 'guessed_city_no':
        await bot.send_message(id, 'Попробуйте еще раз!\nНачать заново: /cancel')
        user[2] = ''

    elif query.data == 'shops_continue':
        print(id, query.message.message_id)
        await bot.edit_message_text('Хотели бы вы выстовить ограничение на максимальную стоимость видеокарты?\nНачать заново: /cancel', id, query.message.message_id, reply_markup=max_price_question_kb)
        user[0] = ''

    elif query.data.startswith('shops_'):
        shop, status = query.data.split('_')[1:]
        for i in range(len(user[3])):
            if user[3][i][1] == shop:
                user[3][i][2] = not user[3][i][2]
                break
        print(query)
        await bot.edit_message_reply_markup(id, query.message.message_id, reply_markup=shops_kb(user[3]))



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

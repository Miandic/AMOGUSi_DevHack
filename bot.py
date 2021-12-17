import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types


API_TOKEN = '5072037847:AAEjOjkfrfrDtPqvr-o5adqlNTgb3NdPY2U'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

con = sqlite3.connect('users.db')
cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Users
               (id INTEGER, item TEXT, city TEXT, max_price INTEGER)''')

users = {}


def add_watching(id, item, city, max_price):
    cur.execute(f'INSERT INTO Users VALUES ({id}, `{item}`, `{city}`, {max_price})')


@dp.message_handler(commands=['start', 'cancel'])
async def send_welcome(msg: types.Message):
    await msg.answer('Привет, я парсер Bot!')
    await msg.answer('Укажите город в котором вы ищите видеокарту (или ближаший крупный к вам).')
    users[msg['from']['id']] = ['city', '', '']


@dp.message_handler()
async def echo(msg: types.Message):
    id, tx = msg['from'].id, msg.text
    print(id, tx)

    if id not in users:
        await send_welcome(msg)
        return

    user = users[id]

    if user[0] == 'city':
        await msg.answer('Какую видеокарту вы ищите?\nНачать заново: /cancel')
        user[0] = 'item'
        user[1] = tx

    elif user[0] == 'item':
        await msg.answer('Хотели бы вы выстовить ограничение на максимальную стоимость видеокарты?\nНачать заново: /cancel')
        user[0] = 'max_price_question'
        user[2] = tx

    elif user[0] == 'max_price_question':
        await msg.answer('Введите максимальную допуcтимую стоимость (в рублях)\nНачать заново: /cancel')
        user[0] = 'max_price'

    elif user[0] == 'max_price':
        if set(tx) <= set('0123456789') and int(tx) < 10000000:
            add_watching(id, user[1], user[2], int(tx))
            await msg.answer('Мы начали поиски вашей видеокарты.(^_^)\nНачать заново: /cancel')
        else:
            await msg.answer('Некорректно введена стоимость.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
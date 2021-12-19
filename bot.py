import logging
import sqlite3
import json
from aiogram import Bot, Dispatcher, executor, types
from difflib import SequenceMatcher
from keyboards import *


API_TOKEN = '5031794729:AAFJxxgyXcozo8nGm57ti-y8raMMMOVBj-o'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

con = sqlite3.connect('users.db')
cur = con.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS Filters
               (id INTEGER, item TEXT, city TEXT, max_price INTEGER, shop TEXT)''')

users = {}

SHOPS = [
    ['ДНС', 'dns', True], ['Регард', 'regard', True],
    ['Ситилинк', 'citilink', True], ['Эльдорадо', 'eldorado', True],
]

with open('cities.json', encoding='utf-8') as f:
    cities_orig = json.loads(f.read())
    cities = [i.lower() for i in cities_orig]


with open('dns_cities.json', encoding='utf-8') as f:
    dns_cities = json.loads(f.read())


async def send_notifications():
    with open('sendedData.json', encoding='utf-8') as f:
        sended_data = json.load(f)
    for city in sended_data:
        for item in sended_data[city]:
            cur.execute(f'SELECT * FROM Filters WHERE shop = "{item["market"]}" AND item = "{item["name"]}" AND max_price >= {item["price"]}')

            for notification in cur.fetchall():
                if notification[3] == 1000000000:
                    text = f'{notification[1]} — [{SHOP_NAMES[notification[4]]}, {cities_orig[cities.index(notification[2])]}]'
                else:
                    text = f'{notification[1]} — [{SHOP_NAMES[notification[4]]}, {cities_orig[cities.index(notification[2])]}, {notification[3]}р.]'
                text = text.replace("-", "\\-")
                notification = list(notification)
                notification[2] = notification[2].replace("-", "\\-")
                await bot.send_message(notification[0], f'Ваш фильтр\n`{text}`\nСработал\\!\n\nВидеокарта *{notification[1]}* доступна в *{notification[2]}* \\({SHOP_NAMES[notification[4]]}\\) по цене *{item["price"]}*р\\.', parse_mode='MarkdownV2')
                cur.execute(f'DELETE FROM Filters WHERE id = {notification[0]} AND item = "{notification[1]}" AND max_price = {notification[3]} AND city = "{notification[2]}" AND shop = "{notification[4]}"')
                con.commit()


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
    cur.execute(f'SELECT city FROM Filters')
    cities = cur.fetchall()
    j = {}

    for city in cities:
        cur.execute(f'SELECT item FROM Filters WHERE city = "{city[0]}"')
        items = list(set([i[0] for i in cur.fetchall()]))
        j[city[0]] = items

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(j, f, ensure_ascii=False)


def add_watching(id, item, city, max_price, shop):
    cur.execute(f'SELECT * FROM Filters WHERE id = {id} AND item = "{item}" AND city = "{city}" AND shop = "{shop}"')
    items = cur.fetchall()
    if items:
        return False
    cur.execute(f'INSERT INTO Filters VALUES ({id}, "{item}", "{city}", {max_price}, "{shop}")')
    con.commit()
    send_json()
    return True


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    await msg.answer('Здравствуйте, я Бот, который уведомит вас о появлении нужных вам видеокарт в продаже, а также их снижении цен😁!\nИспользуйте кнопки из меню для добавления видеокарты в список отслеживаемого😉!', reply_markup=main_kb)
    users[msg['from']['id']] = ['', '', '', None]


@dp.message_handler()
async def handler(msg: types.Message):
    await send_notifications()

    id, tx = msg['from'].id, msg.text

    if id not in users:
        await send_welcome(msg)
        return

    user = users[id]

    if user[0] == 'city':
        city = find_similar(tx)
        if city == False:
            await msg.answer('Я не могу найти такой город😭. Попробуйте еще раз😉!\nНачать заново: /start')
        elif city == True:
            if tx.lower() in dns_cities:
                await msg.answer('Какую видеокарту вы ищите🙃?\nНачать заново: /start')
                user[0] = 'item'
                user[2] = tx.lower()
            else:
                await msg.answer('К сожалению в вашем городе нет подходящих магазинов😭!\nНачать заново: /start')
        else:
            await msg.answer(f'Я правильно понял город который вы хотели ввести: {cities_orig[cities.index(city)]}\n🤨?\nНачать заново: /start', reply_markup=guessed_city_kb)
            user[2] = city.lower()

    elif user[0] == 'item':
        await msg.answer('Выберите магазины которые я буду прверять😉!', reply_markup=shops_kb(SHOPS))
        user[3] = [shop[:] for shop in SHOPS]
        user[1] = tx

    elif user[0] == 'max_price':
        if set(tx) <= set('0123456789') and int(tx) < 10000000:
            wrong = total = 0
            for i in user[3]:
                if i[2]:
                    total += 1
                    if not add_watching(id, user[1], user[2], int(tx), i[1]):
                        wrong += 1
            if wrong == total:
                # Не получилось добавить ни одной карты
                await msg.answer('Вы уже добовляли запрос с такими параметрами😠!')
            else:
                if wrong > 0:
                    # Часть карт не получилось добавить
                    await msg.answer('Часть фильтров уже есть у вас в списке отслеживаемого, поэтому я не стал их дублировать.\nНовые фильтры были успешно добавлены😉!')
                await msg.answer('Я начал поиски вашей видеокарты😉!')
            users[id] = ['', '', '', None]
        else:
            await msg.answer('Некорректно введена стоимость😠!')

    elif tx == 'Добавить в отслеживаемое':
        await msg.answer('Укажите город в котором вы ищите видеокарту (или ближаший крупный к вам)🤗!\nНачать заново: /start')
        users[msg['from']['id']] = ['city', '', '', None]

    elif tx == 'Просмотреть список отслеживаемого':
        cur.execute(f'SELECT * FROM Filters WHERE id = {id}')
        watchlist = cur.fetchall()
        await msg.answer('Вот ваш список отслеживаемого😜!\nНажмите на ненужный фильтр чтобы удалить его😜!', reply_markup=watchlist_kb(watchlist))


@dp.callback_query_handler()
async def handle_callback(query: types.CallbackQuery):
    id = query.from_user.id
    user = users[id]

    if query.data == 'max_price_question_yes':
        await bot.send_message(id, 'Введите максимально допуcтимую стоимость (в рублях)😎!\nНачать заново: /start')
        user[0] = 'max_price'
        await query.answer()

    elif query.data == 'max_price_question_no':
        wrong = total = 0
        for i in user[3]:
            if i[2]:
                total += 1
                if not add_watching(id, user[1], user[2], 1000000000, i[1]):
                    wrong += 1
        if wrong == total:
            # Не получилось добавить ни одной карты
            await bot.send_message(id, 'У вас уже есть такие же фильтры в списке отслеживаемого😝!')
        else:
            if wrong > 0:
                # Часть карт не получилось добавить
                await bot.send_message(id, 'Часть фильтров уже есть у вас в списке отслеживаемого, поэтому я не стал их дублировать😎!\nНовые фильтры были успешно добавлены😝!')
            await bot.send_message(id, 'Мы начали поиски вашей видеокарты🙂!')
        users[id] = ['', '', '', None]

    elif query.data == 'guessed_city_yes':
        if user[2].lower() in dns_cities:
            await bot.send_message(id, 'Какую видеокарту вы ищите🤨?\nНачать заново: /start')
            user[0] = 'item'
        else:
            await bot.send_message(id, 'К сожалению в вашем городе нет подходящих магазинов😭!\nНачать заново: /start')

    elif query.data == 'guessed_city_no':
        await bot.send_message(id, 'Попробуйте еще раз😝!\nНачать заново: /start')
        user[2] = ''

    elif query.data == 'shops_continue':
        await bot.edit_message_text('Хотели бы вы выставить ограничение на максимальную стоимость видеокарты🤨?\nНачать заново: /start', id, query.message.message_id, reply_markup=max_price_question_kb)
        user[0] = ''

    elif query.data.startswith('shops_'):
        shop, status = query.data.split('_')[1:]
        for i in range(len(user[3])):
            if user[3][i][1] == shop:
                user[3][i][2] = not user[3][i][2]
                break
        await bot.edit_message_reply_markup(id, query.message.message_id, reply_markup=shops_kb(user[3]))

    elif query.data.startswith('remove_'):
        d = 'confirm_' + query.data
        item = query.data.split('_')
        item[0] = id
        item[3] = int(item[3])
        if item[3] == 1000000000:
            text = f'{item[1]} — [{SHOP_NAMES[item[4]]}, {cities_orig[cities.index(item[2])]}]'
        else:
            text = f'{item[1]} — [{SHOP_NAMES[item[4]]}, {cities_orig[cities.index(item[2])]}, {item[3]}р.]'
        await bot.edit_message_text(f'Вы уверены что хотите удалить следующий фильтр🤨?\n{text}', id, query.message.message_id, reply_markup=confirm_remove_kb(d))

    elif query.data.startswith('confirm_remove_'):
        item = query.data.split('_')[1:]
        item[0] = id
        item[3] = int(item[3])
        cur.execute(f'DELETE FROM Filters WHERE id = {item[0]} AND item = "{item[1]}" AND max_price = {item[3]} AND city = "{item[2]}" AND shop = "{item[4]}"')
        con.commit()
        cur.execute(f'SELECT * FROM Filters WHERE id = {id}')
        watchlist = cur.fetchall()
        await bot.edit_message_text('Вот ваш список отслеживаемого😜!\nНажмите на ненужный фильтр чтобы удалить его😜!', id, query.message.message_id, reply_markup=watchlist_kb(watchlist))
        await bot.send_message(id, 'Фильтр удален!')

    elif query.data.startswith('cancel_remove'):
        cur.execute(f'SELECT * FROM Filters WHERE id = {id}')
        watchlist = cur.fetchall()
        await bot.edit_message_text('Вот ваш список отслеживаемого😜!\nНажмите на ненужный фильтр чтобы удалить его😜!', id, query.message.message_id, reply_markup=watchlist_kb(watchlist))

    await query.answer()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

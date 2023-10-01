import asyncio
import json
import logging
from parser import get_car
from aiogram import Bot, Dispatcher, executor, types
from config import token, user_id
from aiogram.dispatcher.filters import Text

logging.basicConfig(level=logging.ERROR, filename='bot_errors.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    try:
        start_buttons = ["Последние 10 авто", "Свежие авто"]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*start_buttons)
        await message.answer(
            'Вас приветствует Турбо.аз-бот. Дальше вам будет удобнее пользоваться вспомогательными кнопками.',
            reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка в обработчике команды /start: {e}")


@dp.message_handler(Text(equals='Свежие авто'))
async def new_auto(message: types.Message):
    try:
        await message.answer('Поиск новых авто....')
        fresh_cars = get_car()
        if len(fresh_cars) > 0:
            for k, v in fresh_cars.items():
                last_cars = f'<b>{v["name"]}</b>\n' \
                            f'{v["price"]}\n' \
                            f'{v["year"]}, {v["run"]}, {v["engine"]}\n' \
                            f'{v["url"]}\n'
                await message.answer(last_cars)
        else:
            await message.answer('Новых авто пока нет.')
    except Exception as e:
        logger.error(f"Ошибка в обработчике команды 'Свежие авто': {e}")


@dp.message_handler(Text(equals='Последние 10 авто'))
async def get_last_autos(message: types.Message):
    try:
        with open('db.json', encoding='utf-8') as file:
            db = json.load(file)

        for k, v in sorted(db.items())[-10:]:
            last_cars = f'<b>{v["name"]}</b>\n' \
                        f'{v["price"]}\n' \
                        f'{v["year"]}, {v["run"]}, {v["engine"]}\n' \
                        f'{v["url"]}\n'
            await message.answer(last_cars)
    except Exception as e:
        logger.error(f"Ошибка в обработчике команды 'Последние 10 авто': {e}")

@dp.message_handler(commands=['dbdown'])
async def download_db(message: types.Message):
    try:
        with open('db.json', 'rb') as db_file:
            await bot.send_document(message.chat.id, db_file)
    except Exception as e:
        logger.error(f"Ошибка при отправке файла db.json: {e}")

@dp.message_handler(commands=['parslog'])
async def download_parser_errors(message: types.Message):
    try:
        with open('parser_errors.log', 'rb') as parser_errors_file:
            await bot.send_document(message.chat.id, parser_errors_file)
    except Exception as e:
        logger.error(f"Ошибка при отправке файла parser_errors.log: {e}")

@dp.message_handler(commands=['botlog'])
async def download_bot_errors(message: types.Message):
    try:
        with open('bot_errors.log', 'rb') as bot_errors_file:
            await bot.send_document(message.chat.id, bot_errors_file)
    except Exception as e:
        logger.error(f"Ошибка при отправке файла bot_errors.log: {e}")


async def scan_every_minute():
    while True:
        try:
            fresh_cars = get_car()
            if len(fresh_cars) > 0:
                for k, v in fresh_cars.items():
                    new_car = f'<b>{v["name"]}</b>\n' \
                              f'{v["price"]}\n' \
                              f'{v["year"]}, {v["run"]}, {v["engine"]}\n' \
                              f'{v["url"]}\n'
                    await bot.send_message(user_id, new_car, disable_notification=True)

            await asyncio.sleep(600)
        except Exception as e:
            logger.error(f"Ошибка в процессе сканирования: {e}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(scan_every_minute())
    executor.start_polling(dp)

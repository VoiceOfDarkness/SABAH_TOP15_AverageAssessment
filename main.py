import logging
import sys
import os
import asyncio

from uuid import uuid1
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command


# Получение значения переменной окружения
load_dotenv()

username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
token = os.getenv('TELEGRAM_TOKEN')

# Остальной код...
cluster = MongoClient(f"mongodb+srv://{username}:{password}@database.iirfppa.mongodb.net/?retryWrites=true&w=majority")

db = cluster['TOP15']
collection = db['telegrambot']

data_router = Router()


async def add_data(student_ratings, student_name):
    collection.insert_one({
        '_id': str(uuid1()),
        "ratings": student_ratings,
        "name": student_name,
    })


class Data(StatesGroup):
    means_credit = State()
    ratings = State()
    names = State()
    results = State()


# Команда /start
@data_router.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    await state.set_state(Data.means_credit)    
    await message.reply("Vergüllə ayrılmış kreditlər üçün dəyərləri daxil edin:")


@data_router.message(Data.means_credit)
async def process_means_kredit(message: types.Message, state: FSMContext):
    means_kredit = [int(num.strip()) for num in message.text.split(",")]       
    await state.update_data(means_kredit=means_kredit)
    await state.set_state(Data.ratings)
    await message.reply('Qiymətlər üçün dəyərlər daxil edin')


@data_router.message(Data.ratings)
async def set_ratings(message: types.Message, state: FSMContext):
    await state.set_state(Data.names)
    ratings = [int(num.strip()) for num in message.text.split(",")]
    data = await state.get_data()
    means_credit = data.get('means_kredit')
    credits = len(means_credit)

    # Разбиваем оценки на строки (ряды) по количеству кредитов
    # rows = [ratings[i:i+credits] for i in range(0, len(ratings), credits)]
    for i in range(0, len(ratings), credits):
        rows = ratings[i:i+credits]

    await state.update_data(ratings=rows)
    await message.reply("Adinizi əlavə edin")


@data_router.message(Data.names)
async def set_names(message: types.Message, state: FSMContext):
    await state.set_state(Data.results)
    await state.update_data(names=message.text)
    data = await state.get_data()
    await add_data(data.get('ratings'), message.text)
    await message.reply("Qiymətləndirmə məlumatları qeyd edildi! hesablama aparılır")
    await calculate(message=message, state=state)


@data_router.message(Data.results)
async def calculate(message: types.Message, state: FSMContext):
    data = await state.get_data()
    means_kredit = data.get("means_kredit", [])
    cursor_ratings = collection.find({}, {"ratings": 1})
    cursor_names = collection.find({}, {"name": 1})
    ratings = [doc["ratings"] for doc in cursor_ratings]
    names = {i + 1: doc["name"] for i, doc in enumerate(cursor_names)}

    if means_kredit and ratings:
        lst = []
        result = [[rating[i] * means_kredit[i]
                for i in range(len(rating))] for rating in ratings]

        data_names = dict(zip(names.values(), ratings))

        for name in names.values():
            grade = data_names[name]
            if all(num >= 91 for num in grade):
                lst.append(name)

        sorted_ratings = [(names[i+1], result[i]) for i in range(len(result))]
        sorted_ratings.sort(key=lambda x: sum(x[1]), reverse=True)

        response = ""
        for i, (name, ratings) in enumerate(sorted_ratings):
            if name in lst:
                response += f"{i+1}. {name}: {round(sum(ratings) / sum(means_kredit), 3)}, A\n"
            else:
                response += f"{i+1}. {name}: {round(sum(ratings) / sum(means_kredit), 3)}\n"

        await message.answer(response)
    else:
        await message.reply("Lütfən, vasitələrin_krediti, reytinqlər və adlar üçün dəyərlər təyin edin.")


async def main():
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(data_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

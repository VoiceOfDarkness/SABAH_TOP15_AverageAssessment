import logging
import sys
import os
import asyncio
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command


# Получение значения переменной окружения
load_dotenv()

token = os.getenv('TELEGRAM_TOKEN')

data_router = Router()


class Data(StatesGroup):
    means_credit = State()
    ratings = State()
    results = State()


# Команда /start
@data_router.message(Command('start'))
async def start(message: types.Message, state: FSMContext):
    await state.set_state(Data.means_credit)
    await message.reply("Введите значения для means_kredit через запятую:")


@data_router.message(Data.means_credit)
async def process_means_kredit(message: types.Message, state: FSMContext):
    means_kredit = [int(num.strip()) for num in message.text.split(",")]
    await state.update_data(means_kredit=means_kredit)
    await state.set_state(Data.ratings)
    await message.reply('Введите значения для оценок')


@data_router.message(Data.ratings)
async def set_ratings(message: types.Message, state: FSMContext):
    await state.set_state(Data.results)
    ratings = [int(num.strip()) for num in message.text.split(",")]
    data = await state.get_data()
    means_credit = data.get('means_kredit')
    credits = len(means_credit)

    # Разбиваем оценки на строки (ряды) по количеству кредитов
    rows = [ratings[i:i+credits] for i in range(0, len(ratings), credits)]

    await state.update_data(ratings=rows)
    await message.reply("Данные оценок записаны! идет рассчет")
    await calculate(message=message, state=state)

@data_router.message(Data.results)
async def calculate(message: types.Message, state: FSMContext):
    data = await state.get_data()
    means_kredit = data.get("means_kredit", [])
    ratings = data.get("ratings", [])
    names = {
        1: "leyla",
        2: "murad",
        3: "adil",
        4: "samir",
        5: "nihad",
        6: "teymur",
        7: "nurane",
        8: "maga",
        9: "semender",
        10: "yaqut",
        11: "aysu",
        12: "abil",
        13: "ramin",
        14: "ehmed",
        15: "qabil",
        16: "ibrahim",
        17: "xaliq",
        18: "kanan",
        19: "rovlan",
        20: "subhan",
        21: "ferid(buludlu)",
        22: "sefer",
        23: "aqil",
        24: "esli",
        25: "ferid(memmedzade)",
        26: "ismayil",
        27: "alpay",
        28: "aysel",
        29: "rufet"
    }

    if means_kredit and ratings:
        # Ваш код для расчета и вывода рейтингов
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
        await message.reply("Пожалуйста, установите значения для means_kredit, ratings и names.")


async def main():
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(data_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from config import collection
from data_handler import DataHandler
from states import Data

data_handler = DataHandler(collection)
data_router = Router()


@data_router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.set_state(Data.top_list)
    await message.answer(
        "movcud olan TOP15 baxmaq isteyirsiz?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Bəli"),
                    KeyboardButton(text="Xeyr"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@data_router.message(Data.top_list)
async def top_list(message: types.Message, state: FSMContext):
    user_response = message.text
    try:
        if user_response == "Bəli":
            await data_handler.calculate(message=message, state=state)
        else:
            await state.set_state(Data.delete)
            await message.answer(
                "movcud olan melumatinizi silmek isteyirsiz?",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Bəli"),
                            KeyboardButton(text="Xeyr"),
                        ]
                    ],
                    resize_keyboard=True,
                ),
            )
    except:
        await message.answer("TOP15 siyahisi bosdur")


@data_router.message(Data.delete)
async def delete_data(message: types.Message, state: FSMContext):
    user_response = message.text
    try:
        if user_response == "Bəli":
            await data_handler.delete_student_data(message.from_user.id)
            await message.reply("Məlumtlariniz uğurla silindi")
        else:
            await state.set_state(Data.means_credit)
            await message.reply("Kreditləri vergül ilə daxil edin")
    except:
        await message.reply("Sizin haqqında məlumat yoxdur")


@data_router.message(Data.means_credit)
async def process_means_kredit(message: types.Message, state: FSMContext):
    means_kredit = [int(num.strip()) for num in message.text.split(",")]
    await state.update_data(means_credit=means_kredit)
    await state.set_state(Data.ratings)
    await message.answer("Qiymətlər üçün dəyərlər daxil edin")


@data_router.message(Data.ratings)
async def set_ratings(message: types.Message, state: FSMContext):
    await state.set_state(Data.names)
    ratings = [int(num.strip()) for num in message.text.split(",")]
    data = await state.get_data()
    means_credit = data.get("means_credit")
    credits = len(means_credit)

    # Разбиваем оценки на строки (ряды) по количеству кредитов
    # rows = [ratings[i:i+credits] for i in range(0, len(ratings), credits)]
    for i in range(0, len(ratings), credits):
        rows = ratings[i : i + credits]

    await state.update_data(ratings=rows)
    await message.answer("Adinizi əlavə edin")


@data_router.message(Data.names)
async def set_names(message: types.Message, state: FSMContext):
    await state.update_data(names=message.text)
    data = await state.get_data()
    await data_handler.add_data(
        message.from_user.id,
        data.get("means_credit"),
        data.get("ratings"),
        data.get("names"),
    )
    await message.reply("Qiymətləndirmə məlumatları qeyd edildi! hesablama aparılır")
    await data_handler.calculate(message=message, state=state)

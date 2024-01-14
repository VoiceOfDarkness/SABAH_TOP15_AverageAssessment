from aiogram.fsm.state import State, StatesGroup


class Data(StatesGroup):
    means_credit = State()
    ratings = State()
    names = State()
    delete = State()
    top_list = State()

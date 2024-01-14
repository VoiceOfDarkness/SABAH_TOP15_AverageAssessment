import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher

from config import token
from routers import data_router


async def main():
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(data_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

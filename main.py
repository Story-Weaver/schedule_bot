import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import TOKEN_API
from app.handlers import router


bot = Bot(token=TOKEN_API)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
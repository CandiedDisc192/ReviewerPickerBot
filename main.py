import asyncio
from aiogram import Bot, Dispatcher
from config import bot_token
from app.handlers import router
from app.db.models import async_main


async def main():
    await async_main()
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')

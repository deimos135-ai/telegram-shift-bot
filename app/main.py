import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import BOT_TOKEN
from app.handlers import router
from app.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    print("=== BOT MAIN STARTED ===")
    print(f"BOT_TOKEN exists: {bool(BOT_TOKEN)}")

    dp.include_router(router)
    print("=== ROUTER INCLUDED ===")

    start_scheduler(bot)
    print("=== SCHEDULER STARTED ===")

    me = await bot.get_me()
    print(f"=== BOT CONNECTED: @{me.username} ===")

    print("=== START POLLING ===")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

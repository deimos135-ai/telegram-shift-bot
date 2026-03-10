import asyncio

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from app.config import BOT_TOKEN
from app.handlers import router
from app.scheduler import start_scheduler

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(router)


async def on_startup():

    start_scheduler(bot)


async def main():

    await on_startup()

    app = web.Application()

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    ).register(app, path="/webhook")

    setup_application(app, dp, bot=bot)

    return app


if __name__ == "__main__":

    web.run_app(main(), port=8080)

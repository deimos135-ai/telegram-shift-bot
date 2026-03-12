import asyncio
import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot

from app.config import BOT_TOKEN, GROUP_CHAT_ID, TIMEZONE
from app.messages import build_schedule_message
from app.sheets import get_today_schedule

logging.basicConfig(level=logging.INFO)


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    if not GROUP_CHAT_ID:
        raise RuntimeError("GROUP_CHAT_ID is not set")

    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)
    logging.info("send_once started at %s", now.isoformat())

    data = get_today_schedule()
    logging.info("schedule data: %s", data)

    text = build_schedule_message(data, title="Графік на сьогодні")

    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id=int(GROUP_CHAT_ID), text=text)
        logging.info("message sent to chat_id=%s", GROUP_CHAT_ID)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logging.exception("send_once failed")
        sys.exit(1)

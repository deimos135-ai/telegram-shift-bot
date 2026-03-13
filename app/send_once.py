import asyncio
import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot

from app.config import BOT_TOKEN, GROUP_CHAT_ID, TIMEZONE
from app.messages import build_schedule_message
from app.sheets import get_today_schedule

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


async def main():
    logging.info("CRON JOB STARTED")

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set")

    if not GROUP_CHAT_ID:
        raise RuntimeError("GROUP_CHAT_ID is not set")

    tz = ZoneInfo(TIMEZONE)
    now = datetime.now(tz)

    logging.info("SEND_ONCE: local time = %s", now.isoformat())
    logging.info("SEND_ONCE: TIMEZONE = %s", TIMEZONE)
    logging.info("SEND_ONCE: chat_id = %s", GROUP_CHAT_ID)

    data = get_today_schedule()
    logging.info("SEND_ONCE: schedule data = %s", data)

    text = build_schedule_message(data, title="Графік на сьогодні")
    logging.info("SEND_ONCE: message text built successfully")

    bot = Bot(token=BOT_TOKEN)

    try:
        logging.info("SEND_ONCE: sending message...")
        await bot.send_message(chat_id=int(GROUP_CHAT_ID), text=text)
        logging.info("SEND_ONCE: message sent successfully")
    finally:
        await bot.session.close()
        logging.info("SEND_ONCE: bot session closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        logging.exception("SEND_ONCE: failed")
        sys.exit(1)

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from app.config import SEND_TIME, TIMEZONE, GROUP_CHAT_ID
from app.sheets import get_today_shift
from app.messages import build_shift_message

scheduler = AsyncIOScheduler(timezone=ZoneInfo(TIMEZONE))


def start_scheduler(bot):

    hour, minute = SEND_TIME.split(":")

    scheduler.add_job(
        send_shift,
        CronTrigger(hour=int(hour), minute=int(minute)),
        args=[bot]
    )

    scheduler.start()


async def send_shift(bot):

    data = get_today_shift()

    text = build_shift_message(data)

    await bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=text
    )

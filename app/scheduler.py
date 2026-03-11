from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from datetime import datetime

from app.config import GROUP_CHAT_ID, SEND_TIME, TIMEZONE
from app.messages import build_schedule_message
from app.sheets import get_today_schedule

scheduler = AsyncIOScheduler(timezone=ZoneInfo(TIMEZONE))


async def send_daily_schedule(bot):
    print(f"DEBUG: send_daily_schedule triggered at {datetime.now()}")
    data = get_today_schedule()
    print(f"DEBUG: schedule data = {data}")

    text = build_schedule_message(data, title="Графік на сьогодні")
    print(f"DEBUG: sending message to chat_id={GROUP_CHAT_ID}")

    await bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
    print("DEBUG: daily message sent")


def start_scheduler(bot):
    hour, minute = SEND_TIME.split(":")

    scheduler.add_job(
        send_daily_schedule,
        CronTrigger(hour=int(hour), minute=int(minute)),
        args=[bot],
        id="daily_schedule_job",
        replace_existing=True,
        misfire_grace_time=3600,
        coalesce=True,
    )

    print(f"DEBUG: scheduler started, daily send at {SEND_TIME} {TIMEZONE}")
    scheduler.start()

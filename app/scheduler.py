from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo

from app.config import GROUP_CHAT_ID, SEND_TIME, TIMEZONE
from app.messages import build_schedule_message
from app.sheets import get_today_schedule

scheduler = AsyncIOScheduler(timezone=ZoneInfo(TIMEZONE))


async def send_daily_schedule(bot):
    data = get_today_schedule()
    text = build_schedule_message(data, title="Графік на сьогодні")
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=text)


def start_scheduler(bot):
    hour, minute = SEND_TIME.split(":")

    scheduler.add_job(
        send_daily_schedule,
        CronTrigger(hour=int(hour), minute=int(minute)),
        args=[bot],
        id="daily_schedule_job",
        replace_existing=True,
    )

    scheduler.start()

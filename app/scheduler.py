from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.config import GROUP_CHAT_ID, SEND_TIME, TIMEZONE
from app.messages import build_schedule_message
from app.sheets import get_today_schedule

kyiv_tz = ZoneInfo(TIMEZONE)
scheduler = AsyncIOScheduler(timezone=kyiv_tz)


async def send_daily_schedule(bot):
    now = datetime.now(kyiv_tz)
    print(f"DEBUG: send_daily_schedule triggered at {now.isoformat()}")

    data = get_today_schedule()
    print(f"DEBUG: schedule data = {data}")

    text = build_schedule_message(data, title="Графік на сьогодні")
    print(f"DEBUG: sending message to chat_id={GROUP_CHAT_ID}")

    await bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
    print("DEBUG: daily message sent")


def start_scheduler(bot):
    hour, minute = map(int, SEND_TIME.split(":"))

    trigger = CronTrigger(
        hour=hour,
        minute=minute,
        timezone=kyiv_tz,
    )

    scheduler.add_job(
        send_daily_schedule,
        trigger=trigger,
        args=[bot],
        id="daily_schedule_job",
        replace_existing=True,
        misfire_grace_time=7200,
        coalesce=True,
    )

    scheduler.start()

    job = scheduler.get_job("daily_schedule_job")
    print(f"DEBUG: scheduler started with TIMEZONE={TIMEZONE}, SEND_TIME={SEND_TIME}")
    if job:
        print(f"DEBUG: next run time = {job.next_run_time}")

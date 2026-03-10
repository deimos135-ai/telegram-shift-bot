from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.messages import build_schedule_message
from app.sheets import get_today_schedule, get_tomorrow_schedule

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привіт 👋\n\n"
        "Доступні команди:\n"
        "/today — графік на сьогодні\n"
        "/tomorrow — графік на завтра\n"
        "/admin — черговий адміністратор"
    )


@router.message(Command("today"))
async def cmd_today(message: Message):
    data = get_today_schedule()
    text = build_schedule_message(data, title="Графік на сьогодні")
    await message.answer(text)


@router.message(Command("tomorrow"))
async def cmd_tomorrow(message: Message):
    data = get_tomorrow_schedule()
    text = build_schedule_message(data, title="Графік на завтра")
    await message.answer(text)


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    data = get_today_schedule()

    if not data:
        await message.answer("⚠️ Не вдалося знайти дані в таблиці.")
        return

    duty_admin = data.get("duty_admin")
    admins_working = data.get("admins_working", [])

    admins_text = "\n".join(f"• {name}" for name in admins_working) if admins_working else "• —"
    duty_text = f"• {duty_admin}" if duty_admin else "• —"

    await message.answer(
        f"🧑‍💼 Адміністратори на сьогодні ({data['date']}):\n"
        f"{admins_text}\n\n"
        f"🚨 Черговий адміністратор:\n"
        f"{duty_text}"
    )


@router.message()
async def fallback(message: Message):
    await message.answer(
        "Я працюю 👌\n"
        "Спробуй команди:\n"
        "/today\n"
        "/tomorrow\n"
        "/admin"
    )

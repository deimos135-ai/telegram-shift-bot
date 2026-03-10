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
        "/tomorrow — графік на завтра"
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

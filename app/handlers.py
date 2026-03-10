from aiogram import Router
from aiogram.types import Message

from app.sheets import get_today_shift
from app.messages import build_shift_message

router = Router()


@router.message()
async def today(message: Message):

    if message.text == "/today":

        data = get_today_shift()

        text = build_shift_message(data)

        await message.answer(text)

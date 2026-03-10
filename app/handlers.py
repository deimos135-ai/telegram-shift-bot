from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    print("=== /start RECEIVED ===")
    await message.answer("Привіт 👋 Бот живий")


@router.message(Command("ping"))
async def cmd_ping(message: Message):
    print("=== /ping RECEIVED ===")
    await message.answer("pong 🏓")


@router.message()
async def echo_all(message: Message):
    print(f"=== MESSAGE RECEIVED: {message.text} ===")
    await message.answer("Я тебе чую 👀")

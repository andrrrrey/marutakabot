from __future__ import annotations
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import main_menu_kb
from db import DB

router = Router()

WELCOME_TEXT = (
    "Привет! 👋\n\n"
    "Я бот-помощник. Здесь будет ваш текст о пользе бота.\n"
    "А здесь — кратко про сценарии: ИИ / Тест / Менеджер.\n\n"
    "Выберите действие в меню ниже ⬇️"
)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, db: DB):
    u = message.from_user
    await db.upsert_user(user_id=u.id, first_name=u.first_name, username=u.username)
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())

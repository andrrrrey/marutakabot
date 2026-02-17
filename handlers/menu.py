from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import main_menu_kb, back_to_menu_kb
from states import MainStates
from test_engine import show_question

router = Router()

@router.message(F.text == "🏠 Главное меню")
async def go_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Главное меню", reply_markup=main_menu_kb())

@router.message(F.text == "🤖 Задать вопрос ИИ")
async def go_ai(message: Message, state: FSMContext):
    await state.set_state(MainStates.AI_CHAT)
    await message.answer(
        "🤖 Режим ИИ-диалога включён. Пишите вопрос.\n"
        "Чтобы выйти — нажмите «🏠 Главное меню».",
        reply_markup=back_to_menu_kb(),
    )

@router.message(F.text == "🧪 Пройти тест")
async def go_test(message: Message, state: FSMContext):
    await state.set_state(MainStates.TEST)
    await state.update_data(test_step=0, test_answers={})
    await message.answer("🧪 Начинаем тест!", reply_markup=back_to_menu_kb())
    await show_question(message, state)

@router.message(F.text == "🧑‍💼 Отправить запрос менеджеру")
async def go_manager(message: Message, state: FSMContext):
    await state.set_state(MainStates.MANAGER_TEXT)
    await message.answer(
        "🧑‍💼 Опишите ваш запрос одним сообщением.\n"
        "После этого я попрошу контакт для связи.",
        reply_markup=back_to_menu_kb(),
    )

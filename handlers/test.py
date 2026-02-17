from __future__ import annotations
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from states import MainStates
from keyboards import main_menu_kb
from test_engine import load_test, show_question, finish_test

router = Router()

@router.callback_query(StateFilter(MainStates.TEST), F.data.startswith("test:"))
async def test_callback(call: CallbackQuery, state: FSMContext):
    test = load_test()
    data = await state.get_data()
    step = int(data.get("test_step", 0))
    answers: dict = data.get("test_answers", {})
    questions = test.get("questions", [])

    if call.data == "test:menu":
        await state.clear()
        await call.message.answer("🏠 Главное меню", reply_markup=main_menu_kb())
        await call.answer()
        return

    if step >= len(questions):
        await call.answer()
        await finish_test(call.message, state, test)
        return

    q = questions[step]
    idx = int(call.data.split(":")[-1])
    opt = q["options"][idx]
    answers[q["id"]] = opt

    await state.update_data(test_answers=answers, test_step=step + 1)
    await call.answer(f"Выбрано: {opt}")
    await show_question(call.message, state)

@router.message(StateFilter(MainStates.TEST))
async def test_message(message: Message, state: FSMContext):
    await show_question(message, state)

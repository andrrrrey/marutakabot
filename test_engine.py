from __future__ import annotations
import json
from pathlib import Path
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import test_options_kb, main_menu_kb

DATA_PATH = Path(__file__).resolve().parent / "tests" / "questions.json"

def load_test() -> dict:
    with open(DATA_PATH, "r", encoding="utf-8") as fp:
        return json.load(fp)

async def show_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    step = int(data.get("test_step", 0))
    test = load_test()
    questions = test.get("questions", [])
    if step >= len(questions):
        await finish_test(message, state, test)
        return
    q = questions[step]
    await message.answer(q["text"], reply_markup=test_options_kb(q["options"]))

async def finish_test(message: Message, state: FSMContext, test: dict) -> None:
    data = await state.get_data()
    answers: dict = data.get("test_answers", {})
    result = test.get("default_result", {})
    for r in test.get("results", []):
        match = r.get("match", {})
        if all(answers.get(qid) == expected for qid, expected in match.items()):
            result = r
            break

    lines = [f"✅ Результат: {result.get('text','')}".strip()]
    links = result.get("links") or []
    if links:
        lines.append("")
        lines.append("Рекомендуем:")
        lines.extend([f"• {x}" for x in links])

    await state.clear()
    await message.answer("\n".join([ln for ln in lines if ln != ""]), reply_markup=main_menu_kb())

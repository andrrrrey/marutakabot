from __future__ import annotations
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from config import Config
from db import DB
from keyboards import admin_panel_kb
from states import MainStates
from openai_client import OpenAIService, OpenAISettings

router = Router()

def _is_admin(cfg: Config, user_id: int) -> bool:
    return user_id in set(cfg.admin_ids)

@router.message(Command("admin"))
async def admin_cmd(message: Message, state: FSMContext, cfg: Config, db: DB):
    if not _is_admin(cfg, message.from_user.id):
        await message.answer("⛔️ Доступ запрещён.")
        return
    await state.clear()
    await message.answer("⚙️ Админ-панель настроек:", reply_markup=admin_panel_kb())

@router.callback_query(F.data.startswith("admin:"))
async def admin_actions(call: CallbackQuery, state: FSMContext, cfg: Config, db: DB):
    if not _is_admin(cfg, call.from_user.id):
        await call.answer("⛔️ Нет доступа", show_alert=True)
        return

    action = call.data.split("admin:", 1)[1]

    if action == "set_key":
        await state.set_state(MainStates.ADMIN_WAIT_OPENAI_KEY)
        await call.message.answer("Пришлите OpenAI API key одним сообщением (сохраню в БД).")
        await call.answer()
        return

    if action == "set_assistant":
        await state.set_state(MainStates.ADMIN_WAIT_ASSISTANT_ID)
        await call.message.answer("Пришлите OpenAI Assistant ID (например: asst_...).")
        await call.answer()
        return

    if action == "set_vector_store":
        await state.set_state(MainStates.ADMIN_WAIT_VECTOR_STORE_ID)
        await call.message.answer("Пришлите Vector Store ID (например: vs_...).")
        await call.answer()
        return

    if action == "show":
        s = await db.get_settings()
        text = (
            "📋 Текущие настройки (из БД):\n"
            f"- OPENAI_API_KEY: {'✅ задан' if s.get('openai_api_key') else '❌ нет'}\n"
            f"- OPENAI_ASSISTANT_ID: {s.get('openai_assistant_id') or '—'}\n"
            f"- OPENAI_VECTOR_STORE_ID: {s.get('openai_vector_store_id') or '—'}\n\n"
            "Если чего-то нет в БД, бот возьмёт значение из .env (если оно там задано)."
        )
        await call.message.answer(text, reply_markup=admin_panel_kb())
        await call.answer()
        return

    if action == "bind_vs":
        s = await db.get_settings()
        key = s.get("openai_api_key") or cfg.openai_api_key
        asst = s.get("openai_assistant_id") or cfg.openai_assistant_id
        vs = s.get("openai_vector_store_id") or cfg.openai_vector_store_id
        if not key or not asst or not vs:
            await call.message.answer("⚠️ Нужны API key, Assistant ID и Vector Store ID.")
            await call.answer()
            return
        service = OpenAIService(OpenAISettings(api_key=key, assistant_id=asst, vector_store_id=vs))
        ok, msg = await service.bind_vector_store_to_assistant()
        await call.message.answer(msg, reply_markup=admin_panel_kb())
        await call.answer()
        return

    await call.answer("Неизвестная команда", show_alert=True)

@router.message(StateFilter(MainStates.ADMIN_WAIT_OPENAI_KEY))
async def admin_set_key(message: Message, state: FSMContext, cfg: Config, db: DB):
    if not _is_admin(cfg, message.from_user.id):
        return
    key = (message.text or "").strip()
    if not key:
        await message.answer("Пустое значение. Пришлите ключ ещё раз.")
        return
    await db.update_settings(openai_api_key=key)
    await state.clear()
    await message.answer("✅ OpenAI API key сохранён.", reply_markup=admin_panel_kb())

@router.message(StateFilter(MainStates.ADMIN_WAIT_ASSISTANT_ID))
async def admin_set_asst(message: Message, state: FSMContext, cfg: Config, db: DB):
    if not _is_admin(cfg, message.from_user.id):
        return
    asst = (message.text or "").strip()
    if not asst:
        await message.answer("Пустое значение. Пришлите Assistant ID ещё раз.")
        return
    await db.update_settings(openai_assistant_id=asst)
    await state.clear()
    await message.answer("✅ Assistant ID сохранён.", reply_markup=admin_panel_kb())

@router.message(StateFilter(MainStates.ADMIN_WAIT_VECTOR_STORE_ID))
async def admin_set_vs(message: Message, state: FSMContext, cfg: Config, db: DB):
    if not _is_admin(cfg, message.from_user.id):
        return
    vs = (message.text or "").strip()
    if not vs:
        await message.answer("Пустое значение. Пришлите Vector Store ID ещё раз.")
        return
    await db.update_settings(openai_vector_store_id=vs)
    await state.clear()
    await message.answer("✅ Vector Store ID сохранён.", reply_markup=admin_panel_kb())

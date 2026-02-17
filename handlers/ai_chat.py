from __future__ import annotations
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from states import MainStates
from db import DB
from openai_client import OpenAIService, OpenAISettings
from config import Config

router = Router()

def _settings_from_db_or_env(db_settings: dict, cfg: Config) -> OpenAISettings | None:
    key = db_settings.get("openai_api_key") or cfg.openai_api_key
    asst = db_settings.get("openai_assistant_id") or cfg.openai_assistant_id
    vs = db_settings.get("openai_vector_store_id") or cfg.openai_vector_store_id
    if not key or not asst:
        return None
    return OpenAISettings(api_key=key, assistant_id=asst, vector_store_id=vs)

@router.message(StateFilter(MainStates.AI_CHAT))
async def ai_dialog(message: Message, state: FSMContext, db: DB, cfg: Config):
    text = (message.text or "").strip()
    if not text:
        return

    db_settings = await db.get_settings()
    settings = _settings_from_db_or_env(db_settings, cfg)
    if not settings:
        await message.answer(
            "⚠️ ИИ не настроен.\n"
            "Админ должен задать OpenAI API key и Assistant ID через /admin."
        )
        return

    service = OpenAIService(settings)
    user_id = message.from_user.id

    thread_id = await db.get_user_thread(user_id)
    thread_id = await service.ensure_thread(thread_id)
    await db.set_user_thread(user_id, thread_id)

    await message.chat.do("typing")
    try:
        answer = await service.ask_assistant(thread_id, text)
    except Exception as e:
        answer = f"⚠️ Ошибка при обращении к ИИ: {e}"

    await message.answer(answer)

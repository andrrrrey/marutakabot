from __future__ import annotations
import re
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from states import MainStates
from keyboards import main_menu_kb, back_to_menu_kb
from config import Config
from bitrix import BitrixClient, BitrixSettings

router = Router()

def _parse_contact(text: str) -> tuple[str | None, str | None]:
    t = text.strip()
    email = None
    phone = None
    if re.search(r"@[A-Za-z0-9\.-]+\.[A-Za-z]{2,}", t):
        email = t
    if re.search(r"\+?\d[\d\s\-\(\)]{7,}", t):
        phone = re.sub(r"[^\d\+]", "", t)
    return phone, email

@router.message(StateFilter(MainStates.MANAGER_TEXT))
async def manager_text(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("Напишите запрос текстом одним сообщением.", reply_markup=back_to_menu_kb())
        return

    await state.update_data(manager_text=text)
    await state.set_state(MainStates.MANAGER_CONTACT)
    await message.answer(
        "Спасибо! Теперь укажите контакт для связи (телефон или email).\n"
        "Либо напишите «мой телеграм», чтобы мы связались здесь.",
        reply_markup=back_to_menu_kb(),
    )

@router.message(StateFilter(MainStates.MANAGER_CONTACT))
async def manager_contact(message: Message, state: FSMContext, cfg: Config):
    contact_raw = (message.text or "").strip()
    if not contact_raw:
        await message.answer("Укажите телефон или email.", reply_markup=back_to_menu_kb())
        return

    phone = email = None
    if contact_raw.lower() in ("мой телеграм", "telegram", "tg"):
        u = message.from_user
        contact_raw = f"Telegram: @{u.username}" if u.username else f"Telegram ID: {u.id}"
    else:
        phone, email = _parse_contact(contact_raw)

    data = await state.get_data()
    req_text = data.get("manager_text", "")

    if not cfg.bitrix_webhook_base:
        await state.clear()
        await message.answer(
            "⚠️ Bitrix24 не настроен (BITRIX_WEBHOOK_BASE пустой).\n"
            "Заявка не отправлена. Админу нужно добавить webhook в .env",
            reply_markup=main_menu_kb(),
        )
        return

    client = BitrixClient(BitrixSettings(webhook_base=cfg.bitrix_webhook_base))
    u = message.from_user
    title = f"Заявка из Telegram-бота (user {u.id})"
    comments = (
        f"Запрос:\n{req_text}\n\n"
        f"Контакт:\n{contact_raw}\n\n"
        f"Пользователь:\n{u.full_name} (@{u.username})"
    )

    ok, info = await client.create_lead(
        title=title,
        name=u.full_name,
        phone=phone,
        email=email,
        comments=comments,
    )

    await state.clear()
    if ok:
        await message.answer(f"✅ Заявка отправлена менеджеру. Номер лида: {info}", reply_markup=main_menu_kb())
    else:
        await message.answer(f"⚠️ Не удалось отправить заявку в Bitrix24: {info}", reply_markup=main_menu_kb())

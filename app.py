from __future__ import annotations
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import load_config, Config
from db import DB

from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.ai_chat import router as ai_router
from handlers.test import router as test_router
from handlers.manager import router as manager_router
from handlers.admin import router as admin_router

async def main():
    cfg: Config = load_config()
    logging.basicConfig(level=getattr(logging, cfg.log_level.upper(), logging.INFO))
    log = logging.getLogger("bot")

    bot = Bot(token=cfg.bot_token)
    dp = Dispatcher(storage=MemoryStorage())

    db = DB(cfg.db_path)
    await db.connect()

    dp["cfg"] = cfg
    dp["db"] = db

    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(ai_router)
    dp.include_router(test_router)
    dp.include_router(manager_router)

    log.info("Bot started")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

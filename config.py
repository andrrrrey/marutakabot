from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

def _csv_ints(value: str | None) -> list[int]:
    if not value:
        return []
    out: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except ValueError:
            pass
    return out

@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: list[int]
    bitrix_webhook_base: str | None
    db_path: str
    log_level: str
    openai_api_key: str | None
    openai_assistant_id: str | None
    openai_vector_store_id: str | None

def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("BOT_TOKEN is empty. Put it into .env")
    return Config(
        bot_token=token,
        admin_ids=_csv_ints(os.getenv("ADMIN_IDS")),
        bitrix_webhook_base=(os.getenv("BITRIX_WEBHOOK_BASE") or "").strip() or None,
        db_path=(os.getenv("DB_PATH") or "bot.sqlite3").strip(),
        log_level=(os.getenv("LOG_LEVEL") or "INFO").strip(),
        openai_api_key=(os.getenv("OPENAI_API_KEY") or "").strip() or None,
        openai_assistant_id=(os.getenv("OPENAI_ASSISTANT_ID") or "").strip() or None,
        openai_vector_store_id=(os.getenv("OPENAI_VECTOR_STORE_ID") or "").strip() or None,
    )

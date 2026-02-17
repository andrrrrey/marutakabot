from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from openai import AsyncOpenAI

@dataclass
class OpenAISettings:
    api_key: str
    assistant_id: str
    vector_store_id: str | None = None

class OpenAIService:
    def __init__(self, settings: OpenAISettings):
        self.settings = settings
        self.client = AsyncOpenAI(api_key=settings.api_key)

    async def ensure_thread(self, thread_id: Optional[str]) -> str:
        if thread_id:
            return thread_id
        thread = await self.client.beta.threads.create()
        return thread.id

    async def ask_assistant(self, thread_id: str, user_text: str) -> str:
        await self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_text,
        )

        run = await self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.settings.assistant_id,
        )

        while run.status in ("queued", "in_progress", "requires_action"):
            run = await self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status != "completed":
            return f"⚠️ Не удалось получить ответ (status={run.status}). Попробуйте ещё раз."

        msgs = await self.client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=10)
        for m in msgs.data:
            if m.role == "assistant":
                parts = []
                for c in m.content:
                    if getattr(c, "type", None) == "text":
                        parts.append(c.text.value)
                text = "\n".join([p.strip() for p in parts if p.strip()]).strip()
                return text or "🤖 (пустой ответ)"
        return "🤖 (ответ не найден)"

    async def bind_vector_store_to_assistant(self) -> tuple[bool, str]:
        if not self.settings.vector_store_id:
            return False, "Vector Store ID не задан."
        try:
            await self.client.beta.assistants.update(
                assistant_id=self.settings.assistant_id,
                tool_resources={"file_search": {"vector_store_ids": [self.settings.vector_store_id]}},
            )
            return True, "✅ Vector Store привязан к Assistant."
        except Exception as e:
            return False, f"⚠️ Ошибка привязки: {e}"

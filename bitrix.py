from __future__ import annotations
import httpx
from dataclasses import dataclass

@dataclass
class BitrixSettings:
    webhook_base: str

class BitrixClient:
    def __init__(self, settings: BitrixSettings):
        self.settings = settings

    async def create_lead(
        self,
        *,
        title: str,
        name: str | None,
        phone: str | None,
        email: str | None,
        comments: str
    ) -> tuple[bool, str]:
        url = self.settings.webhook_base.rstrip("/") + "/crm.lead.add.json"
        fields: dict = {"TITLE": title, "COMMENTS": comments}
        if name:
            fields["NAME"] = name
        if phone:
            fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "WORK"}]
        if email:
            fields["EMAIL"] = [{"VALUE": email, "VALUE_TYPE": "WORK"}]

        payload = {"fields": fields, "params": {"REGISTER_SONET_EVENT": "Y"}}

        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, json=payload)
            if r.status_code != 200:
                return False, f"HTTP {r.status_code}: {r.text}"
            data = r.json()
            if "error" in data:
                return False, f"{data.get('error')}: {data.get('error_description')}"
            lead_id = data.get("result")
            return True, str(lead_id) if lead_id else "ok"

import asyncio
import logging
import httpx
from app.config import Settings
from app.models.sheet import SheetRow
from app.utils.hashing import dataset_hash

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(self, sheets, settings: Settings):
        self.sheets = sheets
        self.settings = settings
        self.last_hash: str | None = None
        self.task: asyncio.Task | None = None

    async def broadcast(self, rows: list[SheetRow]) -> None:
        if not self.settings.backend_api_key:
            logger.warning("Realtime broadcast skipped: BACKEND_API_KEY is unset")
            return
        payload = {"event": "sheet_updated", "data": [row.model_dump() for row in rows]}
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.post(
                    f"{self.settings.realtime_service_url.rstrip('/')}/internal/broadcast",
                    json=payload, headers={"X-Backend-Key": self.settings.backend_api_key},
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Realtime service unavailable: %s", exc)

    async def check_once(self) -> bool:
        rows = await asyncio.to_thread(self.sheets.get_rows)
        current_hash = dataset_hash(rows)
        if self.last_hash == current_hash:
            return False
        self.last_hash = current_hash
        await self.broadcast(rows)
        return True

    async def run(self) -> None:
        while True:
            try:
                await self.check_once()
            except Exception:
                logger.exception("Sheet polling failed")
            await asyncio.sleep(self.settings.sync_interval_seconds)

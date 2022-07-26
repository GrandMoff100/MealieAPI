from datetime import datetime

from mealieapi.model import InteractiveModel


class Backup(InteractiveModel):
    name: str
    date: datetime | None = None

    async def download(self) -> bytes:
        return await self._client.download_backup(self.name)

    async def delete(self) -> None:
        await self._client.delete_backup(self.name)

from dataclasses import dataclass


@dataclass()
class Auth:
    client: "MealieClient"
    token: str
    token_type: str = None

    async def refresh(self):
        resp = await self.client.request("auth/refresh")
        self.token = resp['access_token']
        self.token_type = resp['token_type']

    @property
    def header(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }
from mealieapi.raw import _RawClient
from mealieapi.auth import Auth


class MealieClient(_RawClient):
    def __init__(self, url, auth: Auth = None) -> None:
        super().__init__(url)
        self.auth = auth

    async def get_token(self, username: str, password: str) -> Auth:
        resp = await self.request(
            'auth/token',
            method="POST",
            data={
                "username": username,
                "password": password
            }
        )
        return Auth(self, resp['access_token'], resp['token_type'])

    async def login(self, username: str, password: str) -> None:
        self.auth = await self.get_token(
            username,
            password
        )

    def authorize(self, token: str):
        self.auth = Auth(
            self,
            token
        )

    def _headers(self):
        headers = super()._headers()
        if self.auth is not None:
            headers.update(self.auth.header)
        return headers


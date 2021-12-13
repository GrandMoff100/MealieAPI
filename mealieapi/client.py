from mealieapi.raw import _RawClient
from mealieapi.auth import Auth
from mealieapi.recipes import Recipe


class MealieClient(_RawClient):
    def __init__(self, url, auth: Auth = None) -> None:
        super().__init__(url)
        self.auth = auth

    # Authorization Methods
    def _headers(self):
        """Updates the Raw Client headers with the Authorization header."""
        headers = super()._headers()
        if self.auth is not None:
            headers.update(self.auth.header)
        return headers

    async def _get_token(self, username: str, password: str) -> Auth:
        """Exchanges the login credentials of a user for a temporary API token."""
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
        """Makes the Client authorize with the login credentials of a user."""
        self.auth = await self._get_token(
            username,
            password
        )

    def authorize(self, token: str):
        """Makes the Client authorize with an API token."""
        self.auth = Auth(
            self,
            token
        )

    # Recipe Methods
    async def fetch_recipe(self, recipe_slug: str) -> Recipe:
        resp = await self.request(f'recipes/{recipe_slug}')
        
        resp['slug'] = recipe_slug
        resp['org_url'] = resp.get('org_u_r_l')
        if "org_u_r_l" in resp:
            del resp["org_u_r_l"]
        
        
        return Recipe(self, **resp)


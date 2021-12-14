import io
import typing as t

from mealieapi.raw import _RawClient
from mealieapi.auth import Auth
from mealieapi.recipes import Recipe


class MealieClient(_RawClient):
    def __init__(self, url, auth: Auth = None) -> None:
        super().__init__(url)
        self.auth = auth

    # Authorization Methods
    def _headers(self) -> dict:
        """Updates the Raw Client headers with the Authorization header."""
        headers = super()._headers()
        if self.auth is not None:
            headers.update(self.auth.header)
        return headers

    async def _get_token(self, username: str, password: str) -> Auth:
        """Exchanges the login credentials of a user for a temporary API token."""
        resp = await self.request(
            "auth/token",
            method="POST",
            data={
                "username": username,
                "password": password
            }
        )
        return Auth(self, resp["access_token"], resp["token_type"])

    async def login(self, username: str, password: str) -> None:
        """Makes the Client authorize with the login credentials of a user."""
        self.auth = await self._get_token(
            username,
            password
        )

    def authorize(self, token: str) -> None:
        """Makes the Client authorize with an API token."""
        self.auth = Auth(
            self,
            token
        )

    # Recipe Methods
    async def fetch_recipe(self, recipe_slug: str) -> Recipe:
        resp = await self.request(f"recipes/{recipe_slug}")
        
        resp["slug"] = recipe_slug
        resp["org_url"] = resp.get("org_u_r_l")
        if "org_u_r_l" in resp:
            del resp["org_u_r_l"]
        return Recipe(self, **resp)

    async def delete_recipe(self, recipe_slug: str) -> Recipe:
        resp = await self.request(f"recipes/{recipe_slug}", method="DELETE")
        resp["slug"] = recipe_slug
        resp["org_url"] = resp.get("org_u_r_l")
        if "org_u_r_l" in resp:
            del resp["org_u_r_l"]
        return Recipe(self, **resp)

    async def patch_recipe(self, recipe: Recipe) -> Recipe:
        resp = await self.request(f"recipes/{recipe.slug}", method="PATCH")
        resp["slug"] = recipe.slug
        resp["org_url"] = resp.get("org_u_r_l")
        if "org_u_r_l" in resp:
            del resp["org_u_r_l"]
        return Recipe(self, **resp)

    async def fetch_recipe_zip(self, recipe_slug: str):
        # Auth = false
        pass

    async def create_recipe(self, recipe: Recipe) -> Recipe:
        slug = await self.request(
            "recipes/create",
            data=recipe.json(),
            method="POST"
        )
        return await self.fetch_recipe(slug)

    async def create_recipe_from_url(self, url: str) -> Recipe:
        slug = await self.request(
            "recipes/create-url",
            method="POST",
            data=dict(url=url)
        )
        return await self.fetch_recipe(slug)

    async def create_recipe_from_zip(self, file: io.BytesIO):
        pass

    async def fetch_recipes(self, start=0, limit=9999) -> t.List[Recipe]:
        resp = await self.request(
            "recipes/summary",
            params={"start": start, "limit": limit}
        )
        return [Recipe(self, **data) for data in resp]

    async def fetch_untagged_recipes(self) -> t.List[Recipe]:
        resp = await self.request("recipes/summary/untagged")

    async def fetch_uncategorized_recipes(self, start=0, limit=9999) -> t.List[Recipe]:
        resp = await self.request(
            "recipes/summary/uncategorized",
            params={"start": start, "limit": limit}
        )
    
    # Debug
    

    # Utils
    async def download_file(self, file_token: str):
        content = await self.request(
            "utils/download",
            params={"token": file_token}
        )



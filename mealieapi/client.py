import aiohttp
import io
import typing as t

from datetime import datetime
from zipfile import ZipFile

from mealieapi.raw import _RawClient
from mealieapi.auth import Auth
from mealieapi.recipes import Recipe, RecipeComment
from mealieapi.misc import (
    File,
    DebugInfo,
    DebugStatistics,
    DebugVersion
)
from mealieapi.const import DATE_ADDED_FORMAT, DATE_UPDATED_FORMAT


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
        data = await self.request(
            "auth/token",
            method="POST",
            data={
                "username": username,
                "password": password
            }
        )
        return Auth(self, data["access_token"], data["token_type"])

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

    # Query All Recipes
    async def get_recipes(self, start=0, limit=9999) -> t.List[Recipe]:
        data = await self.request(
            "recipes/summary",
            params={"start": start, "limit": limit}
        )
        return [Recipe(self, **data) for data in data]

    async def get_untagged_recipes(self) -> t.List[Recipe]:
        data = await self.request("recipes/summary/untagged")
        return [Recipe(self, **recipe) for recipe in data]

    async def get_uncategorized_recipes(self) -> t.List[Recipe]:
        data = await self.request("recipes/summary/uncategorized")
        return [Recipe(self, **recipe) for recipe in data]

    # Recipe Methods
    def process_recipe_data(self, data: dict) -> Recipe:
        del data['slug']
        data["org_url"] = data.get("org_u_r_l")
        if "org_u_r_l" in data:
            del data["org_u_r_l"]
        if data["comments"]:
            data["comments"] = [RecipeComment(self, recipe_slug, **comment) for comment in data["comments"]]
        if data["date_added"]:
            data["date_added"] = datetime.strptime(data["date_added"], DATE_ADDED_FORMAT)
        if data["date_updated"]:
            data["date_updated"] = datetime.strptime(data["date_updated"], DATE_UPDATED_FORMAT)
        return Recipe(self, **data)

    async def get_recipe(self, recipe_slug: str) -> Recipe:
        data = await self.request(f"recipes/{recipe_slug}")
        return self.process_recipe_data(data)

    async def delete_recipe(self, recipe_slug: str) -> Recipe:
        data = await self.request(f"recipes/{recipe_slug}", method="DELETE")
        return self.process_recipe_data(data)

    async def patch_recipe(self, recipe: Recipe) -> Recipe:
        data = await self.request(f"recipes/{recipe.slug}", method="PATCH")
        return self.process_recipe_data(data)

    async def get_recipe_zip(self, recipe_slug: str) -> ZipFile:
        data = await self.request(
            f'recipes/{recipe_slug}/zip',
            use_auth=False
        )
        return ZipFile(io.BytesIO(data))

    async def create_recipe(self, recipe: Recipe) -> Recipe:
        slug = await self.request(
            "recipes/create",
            json=recipe.json(),
            method="POST"
        )
        return await self.get_recipe(slug)

    async def create_recipe_from_url(self, url: str) -> Recipe:
        slug = await self.request(
            "recipes/create-url",
            method="POST",
            json=dict(url=url)
        )
        return await self.get_recipe(slug)

    async def create_recipe_from_zip(self, file: io.BytesIO):
        # TODO: Look into zip file encoding to fix OSError: [Errno 22] Invalid Argument from Server logs
        data = await self.request(
            'recipes/create-from-zip',
            method="POST",
            data={'archive': file}
        )
        return data

    # Recipe Images
    async def update_recipe_image(self):
        pass

    async def update_recipe_image_from_url(self, url: str):
        pass

    async def upload_recipe_asset(self):
        pass

    # Recipe Tags
    
    # Recipe Categories
        
    # Recipe Comments
    async def create_recipe_comment(self, recipe_slug: str, text: str):
        data = await self.request(
            f'recipes/{recipe_slug}/comments',
            method="POST",
            data=dict(text=text)
        )
        return RecipeComment(self, **data)

    async def update_recipe_comment(self, recipe_slug: str, comment_id: int, text: str):
        data = await self.request(
            f'recipes/{recipe_slug}/comments/{comment_id}',
            method="PUT",
            data=dict(text=text)
        )
        return RecipeComment(self, **data)

    async def delete_recipe_comment(self, recipe_slug: str, comment_id: int):
        await self.request(
            f'recipes/{recipe_slug}/comments/{comment_id}',
            method="DELETE",
            data=dict(text=text)
        )

    # Site Media
    async def get_asset(self, recipe_slug: str, file_name: str):
        return await self._client.request(f'media/recipes/{recipe_slug}/assets/{file_name}')

    async def get_image(self, recipe_slug: str, type='original') -> bytes:
        """
        Gets the image for the recipe.
        Valid types are :code:`original`, :code:`min-original`, and :code:`tiny-original`
        """
        return await self._client.request(f'media/recipes/{recipe_slug}/images/{type}.webp')

    # Users

    # Groups
    async def get_current_group(self):
        data = await self.request(
            'groups/self'
        )
        data['users'] = [User(**info) for info in data['users']]
        return Group(**data)

    # Debug
    async def get_log_file(self) -> File:
        data = await self.request('debug/log')
        return File(self, data.get('file_token'))

    async def get_debug(self):
        data = await self.request('debug')
        return DebugInfo(**data)
    
    async def get_debug_version(self):
        data = await self.request('debug/version', use_auth=False)
        return DebugVersion(**data)
    
    async def get_debug_statistics(self):
        data = await self.request('debug/statistics')
        return DebugStatistics(**data)

    # Misc
    async def download_file(self, file_token: str):
        content = await self.request(
            "utils/download",
            params={"token": file_token},
            use_auth=False
        )
        return content

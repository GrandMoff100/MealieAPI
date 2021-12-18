import aiohttp
import io
import typing as t

from datetime import datetime
from zipfile import ZipFile

from mealieapi.raw import _RawClient
from mealieapi.auth import Auth
from mealieapi.recipes import (
    Recipe,
    RecipeComment,
    RecipeImage,
    RecipeAsset,
    RecipeCategory,
    RecipeTag
)
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

    # Authorization
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
            },
            use_auth=False
        )
        return Auth(self, **data)
    
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

    # User API Keys
    async def create_api_key(self, name: str) -> str:
        data = await self.request(
            f"users/api-tokens",
            method="POST",
            json=dict(name=name)
        )
        return data["token"]

    async def delete_api_key(self, id: int) -> None:
        await self.request(
            f"users/api-tokens/{id}",
            method="DELETE"
        )

    # User Signups
    async def signup_with_token(self):
        "Use auth = false"

    async def delete_signup_key(self):
        pass

    async def get_open_signups(self):
        pass

    async def create_signup_key(self):
        pass

    # Users
    async def get_user_image(self):
        pass

    async def update_user_image(self):
        pass
    
    async def get_user(self):
        pass

    async def update_user(self):
        pass

    async def delete_user(self):
        pass

    async def reset_password(self):
        pass

    async def update_password(self):
        pass

    async def get_favorites(self):
        pass

    async def add_favorite(self):
        pass

    async def remote_favorite(self):
        pass

    async def get_all_users(self):
        pass

    async def create_user(self):
        pass

    # Groups
    async def get_groups(self):
        pass

    async def create_group(self):
        pass

    async def update_group(self):
        pass

    async def delete_group(self):
        pass

    # Current User
    async def get_current_user(self):
        pass

    async def get_current_group(self) -> Group:
        data = await self.request(
            "groups/self"
        )
        data["users"] = [User(**info) for info in data["users"]]
        return Group(**data)

        
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
    def process_recipe_json(self, data: dict) -> Recipe:
        del data["slug"]
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
        return self.process_recipe_json(data)

    async def delete_recipe(self, recipe_slug: str) -> Recipe:
        data = await self.request(f"recipes/{recipe_slug}", method="DELETE")
        return self.process_recipe_json(data)

    async def update_recipe(self, recipe: Recipe) -> Recipe:
        data = await self.request(
            f"recipes/{recipe.slug}",
            method="PUT",
            json=recipe.json()
        )
        return self.process_recipe_json(data)

    async def get_recipe_zip(self, recipe_slug: str) -> ZipFile:
        data = await self.request(
            f"recipes/{recipe_slug}/zip",
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
        slug = await self.request(
            "recipes/create-from-zip",
            method="POST",
            data={"archive": file}
        )
        return await self.get_recipe(slug)

    # Recipe Images
    async def update_recipe_image(self, recipe_slug: str, file: io.BytesIO, extension: str) -> RecipeImage:
        data = await self.request(
            f"recipes/{recipe_slug}/image",
            data={"image": file, "extension": extension},
            method="PUT"
        )
        return RecipeImage(self, recipe_slug, **data)

    async def update_recipe_image_from_url(self, recipe_slug: str, url: str) -> None:
        await self.request(
            f"recipes/{recipe_slug}/image",
            method="POST",
            json=dict(url=url)
        )

    async def upload_recipe_asset(
        self,
        recipe_slug: str,
        name: str,
        icon: str,
        extension: str,
        file: io.BytesIO
    ) -> RecipeAsset:
        data = await self.requst(
            f"recipes/{recipe_slug}/assets",
            data=dict(name=name, icon=icon, extension=extension, file=file),
            method="POST"
        )
        return RecipeAsset(recipe_slug, **data)

    # Recipe Tags
    def process_tag_json(self, data: dict) -> RecipeTag:
        data['recipes'] = [self.process_recipe_json(recipe) for recipe in data['recipes']]
        if data.get('slug'):
            del data['slug']
        return RecipeTag(self **data)

    async def get_tags(self) -> t.List[RecipeTag]:
        tags = await self.request(
            "tags",
            use_auth=False
        )
        return [self.process_tag_json(data) for data in tags]

    async def create_tag(self, name: str) -> RecipeTag:
        data = await self.request(
            "tags",
            method="POST",
            json=dict(name=name)
        )
        return self.process_tag_json(data)

    async def get_empty_tags(self) -> t.List[RecipeTag]:
        tags = await self.request(
            "tags/empty",
            use_auth=False
        )
        return [self.process_tag_json(data) for data in tags]

    async def get_tag_recipes(self, tag_slug: str) -> t.List[Recipe]:
        data = await self.request(
            f'tags/{tag_slug}'
        )
        return [self.process_recipe_json(recipe) for recipe in data['recipes']]

    async def update_tag(self, tag_slug: str, new_name: str) -> RecipeTag:
        data = await self.request(
            f'tags/{tag_slug}',
            method="PUT",
            json=dict(name=new_name)
        )
        return self.process_tag_json(data)

    async def delete_tag(self, tag_slug: str) -> None:
        await self.request(
            f'tags/{tag_slug}',
            method="DELETE"
        )

    
    # Recipe Categories
    def process_category_json(self, data: dict) -> RecipeCategory:
        data['recipes'] = [self.process_recipe_json(recipe) for recipe in data['recipes']]
        if data.get('slug'):
            del data['slug']
        return RecipeCategory(self **data)

    async def get_categories(self) -> t.List[RecipeCategory]:
        categories = await self.request(
            "categories",
            use_auth=False
        )
        return [self.process_category_json(data) for data in categories]

    async def create_category(self, name: str) -> RecipeCategory:
        data = await self.request(
            "categories",
            method="POST",
            json=dict(name=name)
        )
        return self.process_category_json(data)

    async def get_empty_categories(self) -> t.List[RecipeCategory]:
        categories = await self.request(
            "categories/empty",
            use_auth=False
        )
        return [self.process_category_json(data) for data in categories]

    async def get_category_recipes(self, category_slug: str) -> t.List[Recipe]:
        data = await self.request(
            f'categories/{category_slug}'
        )
        return [self.process_recipe_json(recipe) for recipe in data['recipes']]

    async def update_category(self, category_slug: str, new_name: str) -> RecipeCategory:
        data = await self.request(
            f'categories/{category_slug}',
            method="PUT",
            json=dict(name=new_name)
        )
        return self.process_category_json(data)

    async def delete_category(self, category_slug: str) -> None:
        await self.request(
            f'categories/{category_slug}',
            method="DELETE"
        )

    # Recipe Comments
    async def create_recipe_comment(self, recipe_slug: str, text: str) -> RecipeComment:
        data = await self.request(
            f"recipes/{recipe_slug}/comments",
            method="POST",
            data=dict(text=text)
        )
        return RecipeComment(self, **data)

    async def update_recipe_comment(self, recipe_slug: str, comment_id: int, text: str) -> RecipeComment:
        data = await self.request(
            f"recipes/{recipe_slug}/comments/{comment_id}",
            method="PUT",
            data=dict(text=text)
        )
        return RecipeComment(self, **data)

    async def delete_recipe_comment(self, recipe_slug: str, comment_id: int):
        await self.request(
            f"recipes/{recipe_slug}/comments/{comment_id}",
            method="DELETE",
            data=dict(text=text)
        )

    # Shopping List
    async def create_shopping_list(self):
        pass

    async def get_shopping_list(self):
        pass

    async def update_shopping_list(self):
        pass

    async def delete_shopping_list(self):
        pass

    # Meal Plans
    async def get_mealplans_all(self):
        pass

    async def get_mealplans_this_week(self):
        pass

    async def get_todays_mealplan(self):
        pass

    async def get_mealplan(self):
        pass

    async def update_mealplan(self):
        pass

    async def create_mealplan(self):
        pass

    async def get_todays_meal_image(self):
        pass
    
    async def get_mealplan_shopping_list(self):
        pass

    # Site Media
    async def get_asset(self, recipe_slug: str, file_name: str) -> bytes:
        return await self._client.request(f"media/recipes/{recipe_slug}/assets/{file_name}")

    async def get_image(self, recipe_slug: str, type="original") -> bytes:
        """
        Gets the image for the recipe.
        Valid types are :code:`original`, :code:`min-original`, and :code:`tiny-original`
        """
        return await self._client.request(f"media/recipes/{recipe_slug}/images/{type}.webp")

    # Debug
    async def get_log_file(self) -> File:
        data = await self.request("debug/log")
        return File(self, data.get("file_token"))

    async def get_debug(self) -> DebugInfo:
        data = await self.request("debug")
        return DebugInfo(**data)
    
    async def get_debug_version(self) -> DebugVersion:
        data = await self.request("debug/version", use_auth=False)
        return DebugVersion(**data)
    
    async def get_debug_statistics(self) -> DebugStatistics:
        data = await self.request("debug/statistics")
        return DebugStatistics(**data)

    # Misc
    async def download_file(self, file_token: str) -> bytes:
        content = await self.request(
            "utils/download",
            params=dict(token=file_token),
            use_auth=False
        )
        return content

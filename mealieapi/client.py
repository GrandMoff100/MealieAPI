import io
import posixpath
import typing as t
from datetime import datetime
from zipfile import ZipFile

from mealieapi.auth import Token
from mealieapi.backup import Backup
from mealieapi.const import YEAR_MONTH_DAY, YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
from mealieapi.meals import Ingredient, Meal, MealPlan, MealPlanDay, ShoppingList
from mealieapi.misc import AppVersion, DebugInfo, DebugStatistics, DebugVersion, File
from mealieapi.raw import RawClient
from mealieapi.recipes import (
    Recipe,
    RecipeAsset,
    RecipeCategory,
    RecipeComment,
    RecipeImage,
    RecipeNutrition,
    RecipeTag,
)
from mealieapi.users import Group, User, UserSignup


class MealieClient(RawClient):
    # App About
    async def get_app_info(self) -> AppVersion:
        data = await self.request("app/about", use_auth=False)
        return AppVersion(**data)

    # User API Keys
    def process_token_json(self, data: dict[str, t.Any]) -> Token:
        return Token(_client=self, **data)

    async def create_api_key(self, name: str) -> Token:
        data = await self.request(
            "users/api-tokens", method="POST", json=dict(name=name)
        )
        return self.process_token_json(data)

    async def delete_api_key(self, token_id: int) -> None:
        await self.request(f"users/api-tokens/{token_id}", method="DELETE")

    # User Signups
    async def signup_with_token(self, token: str, user: User) -> User:
        data = await self.request(
            f"users/sign-ups/{token}", method="POST", json=user.dict(), use_auth=False
        )
        return self.process_user_json(data)

    async def delete_signup_token(self, token: str | None) -> None:
        if token is None:
            await self.request(f"users/sign-ups/{token}", method="DELETE")
        else:
            raise ValueError("Token string cannot be NoneType must be string")

    async def get_open_signups(self) -> list[UserSignup]:
        data = await self.request("users/sign-ups")
        return [UserSignup(_client=self, **signup) for signup in data]

    async def create_signup_token(self, name: str, admin: bool = False) -> UserSignup:
        data = await self.request(
            "users/sign-ups", method="POST", json=dict(name=name, admin=admin)
        )
        return UserSignup(_client=self, **data)

    # Users
    def process_user_json(self, data: dict[str, t.Any]) -> User:
        if data.get("favorite_recipes"):
            data["favorite_recipes"] = [
                self.process_recipe_json(recipe) for recipe in data["favorite_recipes"]
            ]
        if data.get("tokens"):
            data["tokens"] = [
                self.process_token_json(token_data) for token_data in data["tokens"]
            ]
        return User(_client=self, **data)

    async def get_user_image(self, user_id: int) -> bytes:
        return await self.request(f"users/{user_id}/image", use_auth=False)

    async def update_user_image(self, user_id: int, file: io.BytesIO) -> bytes:
        return await self.request(
            f"users/{user_id}/image", json=dict(profile_image=file)  # type: ignore[arg-type]
        )

    async def get_user(self, user_id: int) -> User:
        data = await self.request(f"users/{user_id}")
        return self.process_user_json(data)

    async def update_user(self, user_id: int, user: User) -> User:
        data = await self.request(f"users/{user_id}", method="PUT", json=user.dict())
        return self.process_user_json(data)

    async def delete_user(self, user_id: int) -> None:
        await self.request(f"users/{user_id}", method="DELETE")

    async def reset_password(self, user_id: int) -> None:
        await self.request(f"users/{user_id}/reset-password", method="PUT")

    async def update_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> None:
        await self.request(
            f"users/{user_id}/password",
            method="PUT",
            json=dict(current_password=current_password, new_password=new_password),
        )

    async def get_favorites(self, user_id: int) -> list[Recipe] | None:
        data = await self.request(f"users/{user_id}/favorites")
        user = self.process_user_json(data)
        return user.favorite_recipes

    async def add_favorite(self, user_id: int, recipe_slug: str) -> None:
        await self.request(f"users/{user_id}/favorites/{recipe_slug}", method="POST")

    async def remove_favorite(self, user_id: int, recipe_slug: str):
        await self.request(f"users/{user_id}/{recipe_slug}", method="DELETE")

    async def get_all_users(self) -> list[User]:
        data = await self.request("users")
        return [self.process_user_json(user) for user in data]

    async def create_user(self, user: User) -> User:
        data = await self.request("users", method="POST", json=user.dict())
        return self.process_user_json(data)

    # Groups
    def process_group_json(self, data: dict[str, t.Any]) -> Group:
        data["users"] = [self.process_user_json(info) for info in data["users"]]
        return Group(_client=self, **data)

    async def get_groups(self) -> list[Group]:
        data = await self.request("groups")
        return [self.process_group_json(group) for group in data]

    async def create_group(self, group: Group) -> Group:
        data = await self.request("groups", method="POST", json=group.dict())
        return self.process_group_json(data)

    async def update_group(self, id: int, group: Group) -> Group:
        data = await self.request(f"groups/{id}", method="PUT", json=group.dict())
        return self.process_group_json(data)

    async def delete_group(self, id: int) -> None:
        await self.request(f"groups/{id}", method="DELETE")

    # Current User
    async def get_current_user(self) -> User:
        data = await self.request("users/self")
        return self.process_user_json(data)

    async def get_current_group(self) -> Group:
        data = await self.request("groups/self")
        return self.process_group_json(data)

    # Query All Recipes
    async def get_recipes(self, start=0, limit=9999) -> list[Recipe]:
        data = await self.request(
            "recipes/summary", params={"start": start, "limit": limit}
        )
        return [Recipe(_client=self, **data) for data in data]

    async def get_untagged_recipes(self) -> list[Recipe]:
        data = await self.request("recipes/summary/untagged")
        return [Recipe(_client=self, **recipe) for recipe in data]

    async def get_uncategorized_recipes(self) -> list[Recipe]:
        data = await self.request("recipes/summary/uncategorized")
        return [Recipe(_client=self, **recipe) for recipe in data]

    # Recipe Methods
    def process_comment_json(self, data: dict[str, t.Any]) -> RecipeComment:
        data["date_added"] = datetime.strptime(
            data["date_added"], YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
        )
        data["user"] = self.process_user_json(data["user"])
        return RecipeComment(self, **data)

    def process_nutrition_json(self, data: dict[str, t.Any]) -> RecipeNutrition:
        return RecipeNutrition(**data)

    def process_recipe_json(self, data: dict[str, t.Any]) -> Recipe:
        data["org_url"] = data.get("org_u_r_l")
        if "org_u_r_l" in data:
            del data["org_u_r_l"]
        if data["comments"]:
            data["comments"] = [
                self.process_comment_json(comment) for comment in data["comments"]
            ]
        if data["date_added"]:
            data["date_added"] = datetime.strptime(data["date_added"], YEAR_MONTH_DAY)
        if data["date_updated"]:
            data["date_updated"] = datetime.strptime(
                data["date_updated"], YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
            )
        del data["slug"]
        return Recipe(_client=self, **data)

    async def get_recipe(self, recipe_slug: str) -> Recipe:
        data = await self.request(f"recipes/{recipe_slug}")
        return self.process_recipe_json(data)

    async def delete_recipe(self, recipe_slug: str) -> Recipe:
        data = await self.request(f"recipes/{recipe_slug}", method="DELETE")
        return self.process_recipe_json(data)

    async def update_recipe(self, recipe: Recipe) -> Recipe:
        data = await self.request(
            f"recipes/{recipe.slug}", method="PUT", json=recipe.dict()
        )
        return self.process_recipe_json(data)

    async def get_recipe_zip(self, recipe_slug: str) -> ZipFile:
        data = await self.request(f"recipes/{recipe_slug}/zip", use_auth=False)
        return ZipFile(io.BytesIO(data))

    async def create_recipe(self, recipe: Recipe) -> Recipe:
        slug = await self.request("recipes/create", json=recipe.dict(), method="POST")
        return await self.get_recipe(slug)

    async def create_recipe_from_url(self, url: str) -> Recipe:
        slug = await self.request(
            "recipes/create-url", method="POST", json=dict(url=url)
        )
        return await self.get_recipe(slug)

    async def create_recipe_from_zip(self, file: io.BytesIO):
        slug = await self.request(
            "recipes/create-from-zip", method="POST", json={"archive": file}  # type: ignore[arg-type]
        )
        return await self.get_recipe(slug)

    # Recipe Images
    async def update_recipe_image(
        self, recipe_slug: str, file: io.BytesIO, extension: str
    ) -> RecipeImage:
        data = await self.request(
            f"recipes/{recipe_slug}/image",
            json={"image": file, "extension": extension},  # type: ignore[arg-type]
            method="PUT",
        )
        return RecipeImage(self, recipe_slug, **data)

    async def update_recipe_image_from_url(self, recipe_slug: str, url: str) -> None:
        await self.request(
            f"recipes/{recipe_slug}/image", method="POST", json=dict(url=url)
        )

    async def upload_recipe_asset(
        self, recipe_slug: str, name: str, icon: str, extension: str, file: io.BytesIO
    ) -> RecipeAsset:
        data = await self.request(
            f"recipes/{recipe_slug}/assets",
            json=dict(name=name, icon=icon, extension=extension, file=file),  # type: ignore[arg-type]
            method="POST",
        )
        return RecipeAsset(self, recipe_slug, **data)

    # Recipe Tags
    def process_tag_json(self, data: dict[str, t.Any]) -> RecipeTag:
        if data.get("recipes"):
            data["recipes"] = [
                self.process_recipe_json(recipe) for recipe in data["recipes"]
            ]
        if data.get("slug"):
            del data["slug"]
        return RecipeTag(self, **data)

    async def get_tags(self) -> list[RecipeTag]:
        tags = await self.request("tags", use_auth=False)
        return [self.process_tag_json(data) for data in tags]

    async def create_tag(self, name: str) -> RecipeTag:
        data = await self.request("tags", method="POST", json=dict(name=name))
        return self.process_tag_json(data)

    async def get_empty_tags(self) -> list[RecipeTag]:
        tags = await self.request("tags/empty", use_auth=False)
        return [self.process_tag_json(data) for data in tags]

    async def get_tag_recipes(self, tag_slug: str) -> list[Recipe]:
        data = await self.request(f"tags/{tag_slug}")
        return [self.process_recipe_json(recipe) for recipe in data["recipes"]]

    async def update_tag(self, tag_slug: str, new_name: str) -> RecipeTag:
        data = await self.request(
            f"tags/{tag_slug}", method="PUT", json=dict(name=new_name)
        )
        return self.process_tag_json(data)

    async def delete_tag(self, tag_slug: str) -> None:
        await self.request(f"tags/{tag_slug}", method="DELETE")

    # Recipe Categories
    def process_category_json(self, data: dict[str, t.Any]) -> RecipeCategory:
        if data.get("recipes"):
            data["recipes"] = [
                self.process_recipe_json(recipe) for recipe in data["recipes"]
            ]
        if data.get("slug"):
            del data["slug"]
        return RecipeCategory(self, **data)

    async def get_categories(self) -> list[RecipeCategory]:
        categories = await self.request("categories", use_auth=False)
        return [self.process_category_json(data) for data in categories]

    async def create_category(self, name: str) -> RecipeCategory:
        data = await self.request("categories", method="POST", json=dict(name=name))
        return self.process_category_json(data)

    async def get_empty_categories(self) -> list[RecipeCategory]:
        categories = await self.request("categories/empty", use_auth=False)
        return [self.process_category_json(data) for data in categories]

    async def get_category_recipes(self, category_slug: str) -> list[Recipe]:
        data = await self.request(f"categories/{category_slug}")
        return [self.process_recipe_json(recipe) for recipe in data["recipes"]]

    async def update_category(
        self, category_slug: str, new_name: str
    ) -> RecipeCategory:
        data = await self.request(
            f"categories/{category_slug}", method="PUT", json=dict(name=new_name)
        )
        return self.process_category_json(data)  # type: ignore[arg-type]

    async def delete_category(self, category_slug: str) -> None:
        await self.request(f"categories/{category_slug}", method="DELETE")

    # Recipe Comments
    async def create_recipe_comment(
        self, recipe_slug: str, comment: RecipeComment
    ) -> RecipeComment:
        data = await self.request(
            f"recipes/{recipe_slug}/comments", method="POST", json=comment.dict()  # type: ignore[arg-type]
        )
        return self.process_comment_json(data)  # type: ignore[arg-type]

    async def update_recipe_comment(
        self, recipe_slug: str, comment_id: int, comment: RecipeComment
    ) -> RecipeComment:
        data = await self.request(
            f"recipes/{recipe_slug}/comments/{comment_id}",
            method="PUT",
            json=comment.dict(),  # type: ignore[arg-type]
        )
        return self.process_comment_json(data)  # type: ignore[arg-type]

    async def delete_recipe_comment(self, recipe_slug: str, comment_id: int):
        await self.request(
            f"recipes/{recipe_slug}/comments/{comment_id}", method="DELETE"
        )

    # Shopping List
    def process_shopping_list_json(self, data: dict[str, t.Any]) -> ShoppingList:
        data["items"] = [Ingredient(self, **item) for item in data["items"]]
        return ShoppingList(self, **data)

    async def create_shopping_list(self, shopping_list: ShoppingList) -> ShoppingList:
        data = await self.request(
            "shopping-lists", method="POST", json=shopping_list.dict()
        )
        return self.process_shopping_list_json(data)  # type: ignore[arg-type]

    async def get_shopping_list(self, id: int) -> ShoppingList:
        data = await self.request(f"shoppings-list/{id}")
        return self.process_shopping_list_json(data)  # type: ignore[arg-type]

    async def update_shopping_list(
        self, id: int, shopping_list: ShoppingList
    ) -> ShoppingList:
        data = await self.request(
            f"shopping-lists/{id}", method="PUT", json=shopping_list.dict()
        )
        return self.process_shopping_list_json(data)  # type: ignore[arg-type]

    async def delete_shopping_list(self, id: int) -> None:
        await self.request(f"shopping-lists/{id}", method="DELETE")

    # Meal Plans
    def process_meal_json(self, data: dict[str, t.Any]) -> Meal:
        return Meal(self, **data)

    def process_mealplanday_json(self, data: dict[str, t.Any]) -> MealPlanDay:
        data["date"] = datetime.strptime(data["date"], YEAR_MONTH_DAY)
        data["meals"] = [self.process_meal_json(meal) for meal in data["meals"]]
        return MealPlanDay(self, **data)

    def process_mealplan_json(self, data: dict[str, t.Any]) -> MealPlan:
        data["end_date"] = datetime.strptime(data["end_date"], YEAR_MONTH_DAY)
        data["start_date"] = datetime.strptime(data["end_date"], YEAR_MONTH_DAY)
        data["plan_days"] = [
            self.process_mealplanday_json(day) for day in data["plan_days"]
        ]
        return MealPlan(self, **data)

    async def get_mealplans_all(self) -> list[MealPlan]:
        data = await self.request("meal-plans/all")
        return [self.process_mealplan_json(mealplan) for mealplan in data]  # type: ignore[arg-type]

    async def get_mealplan_this_week(self) -> MealPlan:
        data = await self.request("meal-plans/this-week")
        return self.process_mealplan_json(data)  # type: ignore[arg-type]

    async def get_todays_meal(self) -> Recipe:
        data = await self.request("meal-plans/today")
        return await self.get_recipe(data.decode())  # type: ignore[arg-type]

    async def get_mealplan(self, id: int) -> MealPlan:
        data = await self.request(f"meal-plans/{id}")
        return self.process_mealplan_json(data)  # type: ignore[arg-type]

    async def update_mealplan(self, id: int, mealplan: MealPlan) -> MealPlan:
        data = await self.request(
            f"meal-plans/{id}", method="PUT", json=mealplan.dict()
        )
        return self.process_mealplan_json(data)  # type: ignore[arg-type]

    async def create_mealplan(self, mealplan: MealPlan) -> MealPlan:
        data = await self.request("meal-plans", method="POST", json=mealplan.dict())
        return self.process_mealplan_json(data)  # type: ignore[arg-type]

    async def delete_mealplan(self, id: int) -> None:
        await self.request(f"meal-plans/{id}", method="DELETE")

    async def get_todays_meal_image(self) -> bytes:
        return await self.request("meal-plans/today/image")  # type: ignore[arg-type]

    async def get_mealplan_shopping_list(self, id: int) -> ShoppingList:
        data = await self.request(f"meal-plans/{id}")
        return self.process_shopping_list_json(data)  # type: ignore[arg-type]

    # Site Media
    async def get_asset(self, recipe_slug: str, file_name: str) -> bytes:
        return await self.request(f"media/recipes/{recipe_slug}/assets/{file_name}", use_auth=False)  # type: ignore[arg-type]

    async def get_image(self, recipe_slug: str, type="original") -> bytes:
        """
        Gets the image for the recipe.
        Valid types are :code:`original`, :code:`min-original`, and :code:`tiny-original`
        """
        return await self.request(f"media/recipes/{recipe_slug}/images/{type}.webp", use_auth=False)  # type: ignore[arg-type]

    # Debug
    async def get_log_file(self) -> File:
        data = await self.request("debug/log")
        return File(_client=self, file_token=str(data.get("file_token")))  # type: ignore[arg-type]

    async def get_debug(self) -> DebugInfo:
        data = await self.request("debug")
        return DebugInfo(**data)  # type: ignore[arg-type]

    async def get_debug_version(self) -> DebugVersion:
        data = await self.request("debug/version", use_auth=False)
        return DebugVersion(**data)  # type: ignore[arg-type]

    async def get_debug_statistics(self) -> DebugStatistics:
        data = await self.request("debug/statistics")
        return DebugStatistics(**data)  # type: ignore[arg-type]

    # Misc
    async def download_file(self, file_token: str) -> bytes:
        content = await self.request(
            "utils/download", params=dict(token=file_token), use_auth=False
        )
        return content  # type: ignore[arg-type]

    # Backup Endpoints
    async def get_available_backups(self) -> list[Backup]:
        data = await self.request("backups/available")
        return [
            Backup(_client=self, **backup_data)
            for backup_data in data.get("imports", [])
        ]

    async def create_backup(
        self,
        name: str,
        include_recipes: bool = True,
        include_settings: bool = True,
        include_pages: bool = True,
        include_themes: bool = True,
        include_groups: bool = True,
        include_users: bool = True,
        include_notifications: bool = True,
    ) -> Backup:
        data = await self.request(
            "backups/export/database",
            json={
                "tag": name,
                "options": {
                    "recipes": include_recipes,
                    "settings": include_settings,
                    "pages": include_pages,
                    "themes": include_themes,
                    "groups": include_groups,
                    "users": include_users,
                    "notifications": include_notifications,
                },
                "template": [],
            },
            method="POST",
        )
        return Backup(
            _client=self, name=posixpath.split(data.get("export_path", ""))[1]
        )

    async def download_backup(self, file_name: str) -> bytes:
        data = await self.request(f"backups/{file_name}/download")
        return await File(_client=self, file_token=data.get("fileToken", "")).download()

    async def delete_backup(self, file_name: str) -> None:
        await self.request(f"backups/{file_name}/download")

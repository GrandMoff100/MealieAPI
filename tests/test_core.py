import typing as t
from mealieapi import MealieClient
from mealieapi.auth import Token
from mealieapi.users import User


URL = "https://demo.mealie.io"
USER = "changeme@email.com"
PASSW = "demo"
CLIENT = MealieClient(URL)
KEY_NAME = 'MealieAPI Test Suite Key'


class TestAuth:
    async def test_login(self):
        await CLIENT.login(USER, PASSW)

    async def test_api_key(self):
        token = await CLIENT.create_api_key(KEY_NAME)
        CLIENT.authorize(token.token)

    async def test_refresh_token(self):
        await CLIENT.auth.refresh()

    async def test_get_user_tokens_and_clean_up(self):
        user = await CLIENT.get_current_user()
        assert True in [token.name == KEY_NAME for token in user.tokens]
        
        for token in user.tokens:
            if token.name == KEY_NAME:
                break
        await CLIENT.delete_api_key(token.id)


class TestGroups:
    async def test_create_group(self):
        pass

    async def test_get_groups(self):
        pass

    async def test_update_group(self):
        pass

    async def test_delete_group(self):
        pass

    async def test_get_current_group(self):
        pass


class TestUser:
    async def test_create_user(self):
        pass

    async def test_get_user(self):
        pass

    async def test_get_all_users(self):
        pass

    async def test_update_user(self):
        pass

    async def test_get_user_image(self):
        pass

    async def test_update_user_image(self):
        pass

    async def test_delete_user(self):
        pass


class TestUserSignup:
    async def test_create_signup_token(self):
        pass

    async def test_get_open_signups(self):
        pass

    async def test_signup_with_token(self):
        pass

    async def test_reset_password(self):
        pass

    async def test_update_password(self):
        pass

    async def test_delete_signup_token(self):
        pass


class TestDebug:
    async def test_get_debug(self):
        pass

    async def test_get_debug_statistics(self):
        pass

    async def test_get_debug_version(self):
        pass

    async def test_get_log_file(self):
        pass

    async def test_download_file(self):
        pass


class TestTagsAndCategories:
    async def test_create_tag(self):
        pass

    async def test_create_category(self):
        pass

    async def test_update_tag(self):
        pass

    async def test_update_category(self):
        pass

    async def test_get_tags(self):
        pass

    async def test_get_categories(self):
        pass

    async def test_create_recipe(self):
        pass

    async def test_create_recipe_comment(self):
        pass

    async def test_update_recipe_comment(self):
        pass

    async def test_delete_recipe_comment(self):
        pass

    async def test_get_tag_recipes(self):
        pass

    async def test_get_category_recipes(self):
        pass

    async def test_delete_recipe(self):
        pass

    async def test_get_empty_categories(self):
        pass

    async def test_get_empty_tags(self):
        pass

    async def test_delete_category(self):
        pass

    async def test_delete_tag(self):
        pass


class TestCreateRecipe:
    async def test_create_recipe_from_url(self):
        pass

    async def test_get_recipe(self):
        pass

    async def test_get_recipes(self):
        pass

    async def test_get_uncategorized_recipes(self):
        pass

    async def test_get_untagged_recipes(self):
        pass

    async def test_upload_recipe_asset(self):
        pass

    async def test_get_asset(self):
        pass

    async def test_delete_recipe(self):
        pass

    async def test_create_recipe_from_zip(self):
        pass

    async def test_add_favorite(self):
        pass

    async def test_get_favorites(self):
        pass

    async def test_get_recipe_zip(self):
        pass

    async def test_remove_favorite(self):
        pass

    async def test_delete_recipe(self):
        pass

class TestMealplans:
    async def test_create_group(self):
        pass

    async def test_create_mealplan(self):
        pass

    async def test_get_mealplan(self):
        pass

    async def test_update_mealplan(self):
        pass

    async def test_get_mealplans_all(self):
        pass

    async def test_get_mealplan_this_week(self):
        pass

    async def test_get_todays_meal(self):
        pass

    async def test_get_todays_meal_image(self):
        pass

    async def test_update_recipe_image(self):
        pass

    async def test_update_recipe_image_from_url(self):
        pass

    async def test_get_mealplan_shopping_list(self):
        pass

    async def test_delete_mealplan(self):
        pass

    async def test_delete_group(self):
        pass


class TestShoppingList:
    async def test_create_shopping_list(self):
        pass

    async def test_get_shopping_list(self):
        pass

    async def test_update_shopping_list(self):
        pass

    async def test_delete_shopping_list(self):
        pass


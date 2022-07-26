import sys

from mealieapi import MealieClient

URL = "https://demo.mealie.io"
USER = "changeme@email.com"
PASSW = "demo"


CLIENT = MealieClient(URL)


class TestAuth:
    def test_login(self):
        pass

    def test_refresh_token(self):
        pass

    def test_create_api_key(self):
        pass

    def test_authorize(self):
        pass

    def test_delete_api_key(self):
        pass


class TestGroups:
    def test_create_group(self):
        pass

    def test_get_groups(self):
        pass

    def test_update_group(self):
        pass

    def test_delete_group(self):
        pass

    def test_get_current_group(self):
        pass


class TestUser:
    def test_get_current_user(self):
        pass

    def test_create_user(self):
        pass

    def test_get_user(self):
        pass

    def test_get_all_users(self):
        pass

    def test_update_user(self):
        pass

    def test_get_user_image(self):
        pass

    def test_update_user_image(self):
        pass

    def test_delete_user(self):
        pass


class TestUserSignup:
    def test_create_signup_token(self):
        pass

    def test_get_open_signups(self):
        pass

    def test_signup_with_token(self):
        pass

    def test_reset_password(self):
        pass

    def test_update_password(self):
        pass

    def test_delete_signup_token(self):
        pass


class TestDebug:
    def test_get_debug(self):
        pass

    def test_get_debug_statistics(self):
        pass

    def test_get_debug_version(self):
        pass

    def test_get_log_file(self):
        pass

    def test_download_file(self):
        pass


class TestTagsAndCategories:
    def test_create_tag(self):
        pass

    def test_create_category(self):
        pass

    def test_update_tag(self):
        pass

    def test_update_category(self):
        pass

    def test_get_tags(self):
        pass

    def test_get_categories(self):
        pass

    def test_create_recipe(self):
        pass

    def test_create_recipe_comment(self):
        pass

    def test_update_recipe_comment(self):
        pass

    def test_delete_recipe_comment(self):
        pass

    def test_get_tag_recipes(self):
        pass

    def test_get_category_recipes(self):
        pass

    def test_delete_recipe(self):
        pass

    def test_get_empty_categories(self):
        pass

    def test_get_empty_tags(self):
        pass

    def test_delete_category(self):
        pass

    def test_delete_tag(self):
        pass


class TestCreateRecipe:
    def test_create_recipe_from_url(self):
        pass

    def test_get_recipe(self):
        pass

    def test_get_recipes(self):
        pass

    def test_upload_recipe_asset(self):
        pass

    def test_get_asset(self):
        pass

    def test_delete_recipe(self):
        pass

    def test_create_recipe_from_zip(self):
        pass

    def test_add_favorite(self):
        pass

    def test_get_recipe_zip(self):
        pass

    def test_remove_favorite(self):
        pass

    def test_delete_recipe(self):
        pass


##### Method Bank
# create_group
# create_mealplan

# create_shopping_list
# delete_mealplan
# delete_shopping_list

# get_favorites
# get_mealplan
# get_mealplan_shopping_list
# get_mealplan_this_week
# get_mealplans_all

# get_shopping_list
# get_todays_meal
# get_todays_meal_image
# get_uncategorized_recipes
# get_untagged_recipes
# update_recipe
# update_recipe_image
# update_recipe_image_from_url
# update_shopping_list
# update_mealplan

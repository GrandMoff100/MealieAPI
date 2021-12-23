![mealie-image](https://hay-kot.github.io/mealie/assets/img/home_screenshot.png)

# Mealie API
If you are running a self-hosted [Mealie](https://hay-kot.github.io/mealie/) server you can use this library to authenticate yourself with and intereact with it!
Create mealplans, import recipes, remove users, modify user groups, upload recipe images.
All with MealieAPI.

## Installation


## Usage


### Authentication
To start you need your Mealie server url, and your login credentials or an API key (which you can create at `https://[YOUR_MEALIE_SERVER]/admin/profile`).
MealieAPI uses the `async`/`await` syntax so you must run it inside an async function or event loop like so (if you are not familiar with async applications already.)


```py
import asyncio
from mealieapi import MealieClient


client = MealieClient("<YOUR_MEALIE_SERVER_ADDRESS>")
```
This next part depends on whether you have an API key, or your login credentials.

If you want to use your username and password you must use `await client.login("<USERNAME_OR_EMAIL>", "<PASSWORD>")` or if you are using an API key you need to use `client.authorize("<API_KEY>")` (Note: without the await).

```
async def main():
    await client.login("<USERNAME_OR_EMAIL>", "<PASSWORD>")
    # OR
    client.authorize("<API_KEY>")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```



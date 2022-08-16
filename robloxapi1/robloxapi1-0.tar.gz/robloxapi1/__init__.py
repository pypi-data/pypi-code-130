import aiohttp

class gamepass:
    def __init__(self, gamepass_id: int) -> None:
        self.gamepass_id = gamepass_id

    async def find_gamepass_user(self, user_id) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://www.roblox.com/users/inventory/list-json?assetTypeId=34&cursor=&itemsPerPage=10000000&pageNumber=1&userId={user_id}") as response:
                response_json = await response.json()
                for data in response_json["Data"]["Items"]:
                    if data["Item"]["AssetId"] == self.gamepass_id:
                        return True
                return False
from .client import web_client

from ..models.user import UserRead
from ..models.subscription import SubscriptionRead
from ..app.config import settings

class SeafiAPI():
    def __init__(self):
        self.auth_header = {"X-Api-Key": settings.APP_API_TOKEN}

    async def init_client(self):
        await web_client.init_client()
    async def close_client(self):
        await web_client.close_client()

    # ------------ users ------------

    async def create_user(self, telegram_id: int, username: str) -> UserRead | int:
        response = await web_client.fetch(
            url="/api/v1/users",
            method="POST",
            headers=self.auth_header,
            json={"username": username, "telegram_id": telegram_id}
        )
        if response.status_code == 201:
            return UserRead(**response.data)
        return response.status_code
    
    async def get_user(self, telegram_id: int) -> UserRead | int:
        response = await web_client.fetch(
            url=f"/api/v1/users/{telegram_id}",
            headers=self.auth_header
        )
        if response.status_code == 200:
            return UserRead(**response.data)
        return response.status_code

    async def patch_user(self, telegram_id: int, **kwargs) -> bool | int:
        response = await web_client.fetch(
            url=f"/api/v1/users/{telegram_id}",
            method="PATCH",
            headers=self.auth_header,
            json=kwargs
        )
        return response.status_code

    # ------------ subscriptions ------------

    async def get_subscriptions(self) -> list[SubscriptionRead] | None:
        """
        Return list of Subscriptions, at error - None
        """
        response = await web_client.fetch(
            url=f"/api/v1/subscriptions",
            headers=self.auth_header
        )
        
        if response.status_code == 200:
            subscriptions = [SubscriptionRead(**sub) for sub in response.data]
            return subscriptions
        
        return None

seafi_api = SeafiAPI()
from .client import web_client

from ..models.user import UserRead
from ..models.subscription import SubscriptionRead, SubscriptionCreate
from ..models.payment import PaymentSchema
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

    async def create_subscription(self, admin_id: str, data: SubscriptionCreate) -> SubscriptionRead | None:
        response = await web_client.fetch(
            url=f"/api/v1/subscriptions",
            method="POST",
            headers=dict(
                **self.auth_header,
                **{"X-Admin-Key": f"{admin_id}:{settings.APP_API_TOKEN}"}
            ),
            json=data.model_dump()
        )

        if response.status_code == 201:
            subscription = SubscriptionRead(**response.data)
            return subscription
        
        return None

    # ------------ payment links ------------

    async def generate_link(self, telegram_id: int, subscription_id: int) -> PaymentSchema:
        response = await web_client.fetch(
            url=f"api/v1/payments/create-link/{subscription_id}?telegram_id={telegram_id}",
            method="POST",
            headers=self.auth_header
        )
        if response.status_code == 200:
            return PaymentSchema(**response.data)

        return None

seafi_api = SeafiAPI()
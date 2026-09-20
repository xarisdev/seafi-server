from fastcrud import FastCRUD

from ..models.subscription import Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionRead

CRUDSubscription = FastCRUD[Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionRead, dict, SubscriptionUpdate]
crud_subscriptions = CRUDSubscription()
from fastcrud import FastCRUD

from ..models.subscription import Subscription, SubscriptionCreate, SubscriptionRead, SubscriptionUpdate

CRUDSubscriptions = FastCRUD[Subscription, SubscriptionCreate, SubscriptionUpdate, SubscriptionRead, dict, SubscriptionUpdate]
crud_subscriptions = CRUDSubscriptions(Subscription)
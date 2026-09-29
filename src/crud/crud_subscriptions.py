from fastcrud import FastCRUD

from ..models.user_subscriptions import UserSubscription, UserSubscriptionCreate, UserSubscriptionRead, UserSubscriptionUpdate

CRUDSubscriptions = FastCRUD[UserSubscription, UserSubscriptionCreate, UserSubscriptionUpdate, UserSubscriptionRead, dict, UserSubscriptionUpdate]
crud_subscriptions = CRUDSubscriptions(UserSubscription)
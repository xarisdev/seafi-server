from fastcrud import FastCRUD

from ..models.subscription_plans import SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanRead

CRUDSubscriptionPlan = FastCRUD[SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanRead, dict, SubscriptionPlanUpdate]
crud_plans = CRUDSubscriptionPlan(SubscriptionPlan)
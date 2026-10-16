from fastcrud import FastCRUD

from ..models.plan import Plan, PlanCreate, PlanRead, PlanUpdate

CRUDSubscriptionPlan = FastCRUD[Plan, PlanCreate, PlanUpdate, PlanRead, dict, PlanUpdate]
crud_plans = CRUDSubscriptionPlan(Plan)
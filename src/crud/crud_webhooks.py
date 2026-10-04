from fastcrud import FastCRUD

from ..models.webhook import Webhook, WebhookCreate, WebhookRead

CRUDWebhook = FastCRUD[Webhook, WebhookCreate, dict, WebhookRead, dict, dict]
crud_webhooks = CRUDWebhook(Webhook)
#import asyncio
#from .websocket import websocket_manager

#depricated
"""class NotificationQueue:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def put_notification(self, telegram_id: int, data: dict):
        if not data:
            return

        notification = Notification(telegram_id=telegram_id, data=data)
        await self.queue.put(notification)

    async def start_worker(self):
        while True:
            notification: Notification = await self.queue.get()
            try:
                await websocket_manager.send_json(**notification.model_dump())
            except Exception as exc:
                pass
            finally:
                self.queue.task_done()
"""
notification_queue = None
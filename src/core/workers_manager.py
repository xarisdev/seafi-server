import asyncio
import logging

import httpx

from .config import settings
from ..services.filters_queue import filters_queue

class WorkersManager:
    def __init__(self, num_workers = 3):
        self.num_workers = num_workers
        self.workers_tasks: list[asyncio.Task] = []
        self._is_running = False

    async def start(self):
        if self._is_running:
            return

        self._is_running = True

        for worker_id in range(1, self.num_workers + 1):
            task = asyncio.create_task(self._worker_loop(worker_id))
            self.workers_tasks.append(task)

    async def stop(self):
        if not self._is_running:
            return

        self._is_running = False

        for task in self.workers_tasks:
            task.cancel()

        await asyncio.gather(*self.workers_tasks, return_exceptions=True)
        self.workers_tasks.clear()

    async def _worker_loop(self, worker_id: int):
        headers = {"X-Api-Key": settings.APP_TOKEN}

        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            while self._is_running:
                try:
                    filter_id = await filters_queue.rotate()
                    if not filter_id:
                        await asyncio.sleep(5.0)
                        continue

                    url = settings.LOCALHOST+f"/{filter_id}"
                    response = await client.get(url)

                    if response.status_code == 200:
                        filter_data = response.json()
                        # parsing
                    
                    elif response.status_code == 402:
                        await filters_queue.remove_filter(filter_id)

                    elif response.status_code == 204:
                        pass

                except asyncio.CancelledError:
                    break

                except Exception as exc:
                    await asyncio.sleep(2.0)

                await asyncio.sleep(settings.WORKER_DELAY)

workers_manager = WorkersManager()
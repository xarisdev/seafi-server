import asyncio
import logging

from collections import deque
from typing import Optional

logger = logging.getLogger("queue_pipeline")

class FilterIdRoundRobinQueue:
    def __init__(self):
        self._queue = deque()
        self._lock = asyncio.Lock()

    async def add_filter(self, filter_id: int):
        async with self._lock:
            if filter_id not in self._queue:
                self._queue.append(filter_id)
                logger.info(f"Filter [{filter_id}] added")

    async def remove_filter(self, filter_id: int):
        async with self._lock:
            if filter_id in self._queue:
                self._queue.remove(filter_id)
                logger.info(f"Filter [{filter_id}] removed")

    async def rotate(self) -> Optional[int]:
        async with self._lock:
            if not self._queue:
                return None

            filter_id = self._queue.popleft()
            self._queue.append(filter_id)

            return filter_id

    async def filters_count(self) -> int:
        async with self._lock:
            return self._queue.__len__()

filters_queue = FilterIdRoundRobinQueue()
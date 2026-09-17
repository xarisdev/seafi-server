import asyncio

from typing import Any, Dict
from ..agents.lalafo import LalafoAgent

class AgentsManager():
    def __init__(self):
        self.active_agents: Dict[int, asyncio.Task] = {}

    async def new_agent_for_sub(self, telegram_id: int, search_url: str):
        await self.stop_agent_for_sub(telegram_id)

        agent = LalafoAgent(telegram_id=telegram_id, search_url=search_url)
        task = asyncio.create_task(agent.start_polling())

        self.active_agents[telegram_id] = task
        # --log

    async def stop_agent_for_sub(self, telegram_id: int):
        task = self.active_agents.get(telegram_id)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            del self.active_agents[telegram_id]
            # --log

agents_manager = AgentsManager()
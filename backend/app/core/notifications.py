import asyncio
from typing import Dict, List
import json

class NotificationBroadcaster:
    """
    Very simple SSE broadcaster to handle real-time notifications.
    In a multi-instance production environment, this would use Redis Pub/Sub.
    For this project, local in-memory queues are sufficient for a single instance.
    """
    def __init__(self):
        # Map user_id -> List of asyncio.Queue
        self.user_queues: Dict[int, List[asyncio.Queue]] = {}

    async def subscribe(self, user_id: int):
        queue = asyncio.Queue()
        if user_id not in self.user_queues:
            self.user_queues[user_id] = []
        self.user_queues[user_id].append(queue)
        
        try:
            while True:
                data = await queue.get()
                yield data
        finally:
            self.user_queues[user_id].remove(queue)
            if not self.user_queues[user_id]:
                del self.user_queues[user_id]

    async def broadcast(self, user_id: int, data: dict):
        if user_id in self.user_queues:
            for queue in self.user_queues[user_id]:
                await queue.put(json.dumps(data, ensure_ascii=False))

# Singleton instance
broadcaster = NotificationBroadcaster()

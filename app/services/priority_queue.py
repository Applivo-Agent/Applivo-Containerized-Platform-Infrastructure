"""
app/services/priority_queue.py
───────────────────────────────
Priority queue service for tier-based task prioritization.
Premium users get highest priority, then Pro, then Starter.
Uses Redis (if available) or in-memory fallback.
"""

from __future__ import annotations

import asyncio
import heapq
import time
from dataclasses import dataclass, field
from typing import Any, Optional

import structlog

from app.models.subscription import PLAN_PRIORITY, PlanTier

logger = structlog.get_logger()


@dataclass(order=True)
class PriorityTask:
    """A task with priority for the queue."""
    priority: int  # Lower number = higher priority (negated for max-heap)
    created_at: float = field(compare=True)
    task_id: str = field(compare=False, default="")
    user_id: str = field(compare=False, default="")
    task_type: str = field(compare=False, default="")
    payload: Any = field(compare=False, default=None)


class PriorityQueueService:
    """
    Manages task prioritization based on user subscription tier.
    Premium users' tasks are processed before Pro, and Pro before Starter.
    """

    def __init__(self):
        self._queue: list[PriorityTask] = []
        self._lock = asyncio.Lock()
        self._task_counter = 0

    def _get_priority(self, plan: Optional[str]) -> int:
        """
        Convert plan tier to priority value.
        Lower number = higher priority.
        Negated for heap: Premium=-3, Pro=-2, Starter=-1
        """
        if not plan:
            return 0
        try:
            tier = PlanTier(plan)
            return -PLAN_PRIORITY.get(tier, 0)
        except ValueError:
            return 0

    async def enqueue(
        self,
        user_id: str,
        task_type: str,
        plan: Optional[str] = None,
        payload: Any = None,
    ) -> str:
        """
        Add a task to the priority queue.
        Returns a task ID for tracking.
        """
        async with self._lock:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}_{int(time.time())}"
            priority = self._get_priority(plan)

            task = PriorityTask(
                priority=priority,
                created_at=time.time(),
                task_id=task_id,
                user_id=user_id,
                task_type=task_type,
                payload=payload,
            )

            heapq.heappush(self._queue, task)
            logger.info(
                "Task enqueued",
                task_id=task_id,
                user_id=user_id,
                task_type=task_type,
                priority=priority,
                plan=plan,
                queue_size=len(self._queue),
            )
            return task_id

    async def dequeue(self) -> Optional[PriorityTask]:
        """Get the highest priority task from the queue."""
        async with self._lock:
            if not self._queue:
                return None
            task = heapq.heappop(self._queue)
            logger.info(
                "Task dequeued",
                task_id=task.task_id,
                user_id=task.user_id,
                task_type=task.task_type,
                remaining=len(self._queue),
            )
            return task

    async def peek(self) -> Optional[PriorityTask]:
        """Peek at the next task without removing it."""
        async with self._lock:
            if not self._queue:
                return None
            return self._queue[0]

    async def size(self) -> int:
        """Get the current queue size."""
        async with self._lock:
            return len(self._queue)

    async def remove_user_tasks(self, user_id: str) -> int:
        """Remove all tasks for a specific user. Returns count removed."""
        async with self._lock:
            before = len(self._queue)
            self._queue = [t for t in self._queue if t.user_id != user_id]
            heapq.heapify(self._queue)
            removed = before - len(self._queue)
            if removed > 0:
                logger.info("Removed user tasks", user_id=user_id, removed=removed)
            return removed

    async def get_stats(self) -> dict:
        """Get queue statistics."""
        async with self._lock:
            plan_counts: dict[str, int] = {}
            task_type_counts: dict[str, int] = {}
            for task in self._queue:
                plan_counts[task.user_id] = plan_counts.get(task.user_id, 0) + 1
                task_type_counts[task.task_type] = task_type_counts.get(task.task_type, 0) + 1

            return {
                "total_tasks": len(self._queue),
                "task_types": task_type_counts,
                "next_task": {
                    "task_id": self._queue[0].task_id,
                    "task_type": self._queue[0].task_type,
                    "priority": self._queue[0].priority,
                } if self._queue else None,
            }


priority_queue = PriorityQueueService()

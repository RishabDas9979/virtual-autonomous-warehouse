"""Order queue with priorities, deadlines and aging."""
import itertools
import math
from dataclasses import dataclass

PENDING, ACTIVE, DONE = 'PENDING', 'ACTIVE', 'DONE'


@dataclass
class OrderRecord:
    id: int
    pickup: str
    dropoff: str
    priority: int            # 1 urgent, 2 normal, 3 low
    submitted: float
    deadline: float = math.inf   # absolute time
    status: str = PENDING
    robot: str = ''
    assigned: float = -1.0
    completed: float = -1.0


class OrderQueue:
    def __init__(self, aging_sec=60.0):
        self.aging_sec = aging_sec   # a waiting order gains one priority level per period
        self.orders = {}
        self._ids = itertools.count(1)

    def submit(self, pickup, dropoff, priority, now, deadline_sec=0.0):
        priority = min(3, max(1, int(priority)))
        deadline = now + deadline_sec if deadline_sec > 0 else math.inf
        rec = OrderRecord(next(self._ids), pickup, dropoff, priority, now, deadline)
        self.orders[rec.id] = rec
        return rec

    def effective_priority(self, o, now):
        return max(1, o.priority - int((now - o.submitted) // self.aging_sec))

    def _key(self, o, now):
        return (self.effective_priority(o, now), o.deadline, o.submitted, o.id)

    def pending(self, now):
        items = [o for o in self.orders.values() if o.status == PENDING]
        return sorted(items, key=lambda o: self._key(o, now))

    def set_priority(self, order_id, priority):
        o = self.orders.get(order_id)
        if o is None or o.status != PENDING or priority not in (1, 2, 3):
            return False
        o.priority = priority
        return True

    def assign(self, order_id, robot, now):
        o = self.orders[order_id]
        o.status, o.robot, o.assigned = ACTIVE, robot, now

    def complete(self, order_id, now):
        o = self.orders[order_id]
        o.status, o.completed = DONE, now

    def requeue(self, order_id):
        """Put an active order back in the queue (robot failed or ran flat)."""
        o = self.orders[order_id]
        o.status, o.robot, o.assigned = PENDING, '', -1.0

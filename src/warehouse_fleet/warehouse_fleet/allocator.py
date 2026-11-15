"""Pick the best robot for an order: nearest idle robot with enough battery."""
from dataclasses import dataclass


@dataclass
class RobotInfo:
    name: str
    x: float
    y: float
    battery: float   # 0.0 to 1.0
    state: str       # IDLE, TO_PICKUP, TO_DROPOFF, TO_CHARGER, CHARGING, FAILED


def trip_cost(graph, params, node, order):
    """Battery fraction needed: to pickup, deliver, then reach a charger."""
    d1 = graph.length(node, order.pickup)
    d2 = graph.length(order.pickup, order.dropoff)
    d3 = graph.length(order.dropoff, graph.nearest_charger(order.dropoff))
    return params.drive_rate * (d1 + d2 * params.carry_factor + d3) * params.speedup


def choose_robot(order, robots, graph, params):
    """Return the name of the chosen robot, or None if nobody qualifies."""
    best, best_score = None, float('inf')
    for r in robots:
        if r.state != 'IDLE' or r.battery < params.low:
            continue
        node = graph.nearest(r.x, r.y)
        if r.battery - trip_cost(graph, params, node, order) < params.reserve:
            continue
        score = graph.length(node, order.pickup)
        if (score, r.name) < (best_score, best or ''):
            best, best_score = r.name, score
    return best

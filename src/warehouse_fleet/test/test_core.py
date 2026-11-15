import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG))
LOC = PKG.parent / 'warehouse_navigation' / 'config' / 'locations.yaml'

from warehouse_fleet.allocator import RobotInfo, choose_robot  # noqa: E402
from warehouse_fleet.battery import Battery, BatteryParams  # noqa: E402
from warehouse_fleet.graph import Graph  # noqa: E402
from warehouse_fleet.orders import OrderQueue  # noqa: E402


def close(a, b, tol=1e-9):
    return abs(a - b) < tol


def load():
    return Graph.from_yaml(str(LOC))


def test_graph_connected():
    g = load()
    for k in g.nodes:
        assert g.path('parking_1', k)[0] is not None, k


def test_graph_symmetric_and_routed():
    g = load()
    assert close(g.length('parking_1', 'shipping_dock'), g.length('shipping_dock', 'parking_1'))
    assert 'lane_east' in g.path('parking_1', 'loading_dock')[0]
    assert g.nearest(-3.1, -7.1) == 'parking_1'


def test_battery_idle_drive_carry():
    b = Battery()
    b.step(100)
    assert close(b.level, 0.98)
    d, c = Battery(), Battery()
    d.step(0, metres=10)
    c.step(0, metres=10, carrying=True)
    assert close(d.level, 0.975) and c.level < d.level


def test_battery_charge_clamp_speedup():
    b = Battery(level=0.2)
    b.step(10, charging=True)
    assert close(b.level, 0.25)
    z = Battery(level=0.01)
    z.step(1000)
    assert z.level == 0.0 and z.is_dead
    f = Battery(BatteryParams(speedup=10.0))
    f.step(100)
    assert close(f.level, 0.8)


def test_queue_priority_and_deadline():
    q = OrderQueue()
    n = q.submit('loading_dock', 'shipping_dock', 2, 0)
    u = q.submit('loading_dock', 'shipping_dock', 1, 1)
    lo = q.submit('loading_dock', 'shipping_dock', 3, 2)
    assert [o.id for o in q.pending(3)] == [u.id, n.id, lo.id]
    q2 = OrderQueue()
    a = q2.submit('loading_dock', 'shipping_dock', 2, 0, deadline_sec=100)
    b = q2.submit('loading_dock', 'shipping_dock', 2, 0, deadline_sec=50)
    assert [o.id for o in q2.pending(1)] == [b.id, a.id]


def test_queue_aging_and_set_priority():
    q = OrderQueue(aging_sec=60)
    lo = q.submit('loading_dock', 'shipping_dock', 3, 0)
    n = q.submit('loading_dock', 'shipping_dock', 2, 100)
    assert q.pending(130)[0].id == lo.id
    assert q.set_priority(n.id, 1) and not q.set_priority(n.id, 5)
    q.assign(n.id, 'robot1', 131)
    assert not q.set_priority(n.id, 2)
    q.requeue(n.id)
    assert q.set_priority(n.id, 2)


def test_allocator():
    g, p = load(), BatteryParams()
    q = OrderQueue()
    o = q.submit('loading_dock', 'shipping_dock', 2, 0)
    r1 = RobotInfo('robot1', -3.0, -7.0, 1.0, 'IDLE')
    r2 = RobotInfo('robot2', 3.0, -7.0, 1.0, 'IDLE')
    assert choose_robot(o, [r1, r2], g, p) == 'robot2'
    r2.battery = 0.2
    assert choose_robot(o, [r1, r2], g, p) == 'robot1'
    r1.state = 'TO_PICKUP'
    assert choose_robot(o, [r1, r2], g, p) is None


if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn()
            print('ok', name)

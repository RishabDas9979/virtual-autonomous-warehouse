"""Simulated battery. Levels are fractions: 0.0 empty, 1.0 full."""
from dataclasses import dataclass


@dataclass
class BatteryParams:
    idle_rate: float = 0.0002    # per second (0.02 %/s)
    drive_rate: float = 0.0025   # per metre travelled (0.25 %/m)
    carry_factor: float = 1.3    # drive drain multiplier while carrying
    charge_rate: float = 0.005   # per second (0.5 %/s)
    low: float = 0.30            # below this: no new orders, go charge when idle
    critical: float = 0.10       # below this: abandon order, go charge now
    resume: float = 0.90         # charged enough to work again
    reserve: float = 0.15        # must still have this left after a trip
    speedup: float = 1.0         # scales drain and charge for faster demos


class Battery:
    def __init__(self, params=None, level=1.0):
        self.p = params or BatteryParams()
        self.level = level

    def step(self, dt, metres=0.0, carrying=False, charging=False):
        p = self.p
        if charging:
            self.level += p.charge_rate * dt * p.speedup
        else:
            factor = p.carry_factor if carrying else 1.0
            self.level -= (p.idle_rate * dt + p.drive_rate * metres * factor) * p.speedup
        self.level = min(1.0, max(0.0, self.level))
        return self.level

    @property
    def is_low(self):
        return self.level < self.p.low

    @property
    def is_critical(self):
        return self.level < self.p.critical

    @property
    def is_dead(self):
        return self.level <= 0.0

    @property
    def is_charged(self):
        return self.level >= self.p.resume

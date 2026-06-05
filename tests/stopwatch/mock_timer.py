from dataclasses import dataclass


@dataclass
class MockTimer:
    def __post_init__(self):
        self.time: float = 0

    def get_time(self):
        return self.time

    def tick(self, amount: float):
        self.time = self.time + amount

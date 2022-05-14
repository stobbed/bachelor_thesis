from dataclasses import dataclass
@dataclass
class Trip:
    link: str
    event_id: int
    time: int

@dataclass
class Vehicle:
    id: str
    trips: list[Trip]
    
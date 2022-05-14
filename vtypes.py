from dataclasses import dataclass
@dataclass
class Trip:
    street: str
    event_id: int

@dataclass
class Vehicle:
    id: str
    trips: list[Trip]
    
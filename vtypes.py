from dataclasses import dataclass
@dataclass
class Trip:
    link: str
    event_id: int
    time: int
    link_length: float
    link_freesped: float

@dataclass
class Vehicle:
    id: str
    trips: list[Trip]

# atm unnecessary
@dataclass
class Links:
    link: str
    length: float
    freespeed: float
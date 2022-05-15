from dataclasses import dataclass
@dataclass
class Trip:
    link: str
    event_id: int
    entered_time: int
    link_length: float
    link_freespeed: float
    left_time: int = -1

@dataclass
class Vehicle:
    id: str
    traveleddistance: float
    intown_pct: float
    countryroad_pct: float
    highway_pct: float
    avgpassenger_amount: float = -1
    # trips: list[Trip]

# atm unnecessary
@dataclass
class Links:
    link: str
    length: float
    freespeed: float
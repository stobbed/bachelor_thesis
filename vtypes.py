from dataclasses import dataclass
from xmlrpc.client import Boolean, boolean
@dataclass
class Trip:
    link: str
    event_id: int
    entered_time: int
    link_length: float
    link_freespeed: float
    left_time: int = -1
    actual_speed: float = -1
    speed_pct: float = -1
    corrected: bool = False
    passengers: int = 0

@dataclass
class Fleet:
    vehicles: dict
    totaldistance: float
    avg_distance_per_vehicle: float
    distance_intown: float
    pkm_intown: float
    distance_countryroad: float
    pkm_countryroad: float
    distance_highway: float
    pkm_highway: float
    maximumdistance: float
    maximumdistance_roadpct: list = -1
    # distance

@dataclass
class Vehicle:
    id: str
    traveleddistance: float
    intown_pct: float
    countryroad_pct: float
    highway_pct: float
    pkm_intown: float
    pkm_countryroad: float
    pkm_highway: float
    avgpassenger_amount: float
    capacity: int = -1
    # trips: list[Trip]

# atm unnecessary
@dataclass
class Links:
    link: str
    length: float
    freespeed: float
    entered_left : str = None
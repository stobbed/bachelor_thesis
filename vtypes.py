# (CC) Dustin Stobbe, 2022

from dataclasses import dataclass
from xmlrpc.client import Boolean, boolean
@dataclass
class Trip:
    link: str
    event_id: int
    entered_time: int
    link_length: float
    link_freespeed: float
    passengerfromregion: int
    passengernotfromregion: int
    passengers: int = 0
    left_time: int = -1
    actual_speed: float = -1
    speed_pct: float = -1
    corrected: bool = False

@dataclass
class Fleet:
    vehicles: dict
    totaldistance: float
    tota_lpkm: float
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
    total_pkm: float
    avgpassenger_amount: float
    avgpassenger_without_empty: float
    pkm_without_empty: float
    avg_speed: float
    speed_pct: float
    speed_length: float
    speed_above_90: float
    speed_below_70: float
    speed_below_50: float
    speed_below_30: float
    speed_below_10: float
    distance_not_from_region: float = 0
    distance_from_region: float = 0
    capacity: int = -1
    # trips: list[Trip]

# atm unnecessary
@dataclass
class Links:
    link: str
    length: float
    freespeed: float
    entered_left : str = None

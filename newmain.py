from config import dbpath
from db import *

db = Db(dbpath)
vehicles = db.get_vehicles()
getlinks = db.get_vehicle_links(vehicles)
res = getlinks.get("drt406")
print(get_link_from_id(res,"1"))


def get_link_from_id(trips,id):
    for trip in trips:
        if trip.event_id == id:
            print(trip)


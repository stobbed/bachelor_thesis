from processing import *
import sqlite3
from config import *
import os.path
from vtypes import *


class GetLinksForEvent:
    def __init__(self):
        self.d = {}

    def add(self,vehicle_id,link):

        self.d[vehicle_id] = link

    def get(self,vehicle_id):
        return self.d[vehicle_id]


class Db:
    def __init__(self,dbpath):
        self._sqliteConnection = sqlite3.connect(dbpath)
        self._cursor = self._sqliteConnection.cursor()
        self.dict = GetLinksForEvent()

    def disconnect(self):
        self._cursor.close()
    

    def get_vehicles(self) -> "list[str]":
        return create_drtvehicleids_list(self._cursor)


    def get_vehicle_links(self,ids) -> "GetLinksForEvent":
        create_dict_vid_and_links(ids, self._cursor,self.dict)

        return self.dict


class MockDb:  
    def get_vehicles(self):
        return ["bmw","vw"]

    def get_vehicle_links(self,ids):
        d = GetLinksForEvent()
        d.add("bmw",[Trip("zittauer","1"),Trip("berliner","2")])
        # d.add("vw","456")
        return d



# def test_get_occ():
#     db = MockDb()
#     events = db.get_traffic_events()
#     asssert 
# def test_get_road_perc():
#     trips = [Trip('baker street',0),Trip('berliner allee',50)]
#     velocities = {"baker street": 50.}
#     city,land,autobahn  = get_road_perc(trips,velocities)
#     assert city == .5
#     assert land == .5
#     assert autobahn == 0.



# db = Db(dbpath)
# ids = db.get_traffic_events()
# links = db.get_vehicle_links(ids)


# vehicle = data[d1]
# for trip in vehicle.trips:
#     trip.street
#     trip.time
#     # db.

#
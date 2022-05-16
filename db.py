from processing import *
import sqlite3
from config import *
import os.path
from vtypes import *
from XML2DB import *


class LinksForEvent:
    def __init__(self):
        self.d = {}

    def add(self,vehicle_id,link):
        self.d[vehicle_id] = link

    def gettrips(self,vehicle_id):
        return self.d[vehicle_id]


class Db:
    def __init__(self,dbpath):
        if os.path.exists(dbpath):
            try:
                # connects to sqlite database file - if path is faulty, creates a new and empty database
                self._sqliteConnection = sqlite3.connect(dbpath)
                self._cursor = self._sqliteConnection.cursor()
                print('Connection to SQLite-File',dbpath,'>> SUCCESS!')
            except sqlite3.Error as error:
                print('SQLite error: ', error)
            finally:
                pass
        else:
            create_database()
            self._sqliteConnection = sqlite3.connect(dbpath)
            self._cursor = self._sqliteConnection.cursor()
            print('Connection to SQLite-File',dbpath,'>> SUCCESS!')
            # raise FileNotFoundError('Invalid path (dbfile): '+dbpath+' - *.db file doesn\'t exist.')
        self.entered_dict = LinksForEvent()
        self.left_dict = LinksForEvent()

    def disconnect(self):
        self._cursor.close()
        self._sqliteConnection.close()
        print('The SQLite connection is closed')
    

    def get_vehicles(self) -> "list[str]":
        return create_drtvehicleids_list(self._cursor)


    def get_vehicle_entered_links(self,ids) -> "LinksForEvent":
        create_dict_entered_links(ids, self._cursor,self.entered_dict)
        return self.entered_dict

    def get_vehicle_left_links(self,ids) -> "LinksForEvent":
        create_dict_left_links(ids, self._cursor,self.left_dict)
        return self.left_dict


class MockDb:  
    def get_vehicles(self):
        return ["bmw","vw"]

    def get_vehicle_links(self,ids):
        d = LinksForEvent()
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
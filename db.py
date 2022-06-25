import sqlite3
import os.path
from collections import defaultdict

from configuration import *
from vtypes import *
from XML2DB import *
from processing import *


class LinksForEvent:
    def __init__(self):
        self.d = {}

    def add(self,event_id,trip):
        self.d[event_id] = trip

    def gettrips(self,vehicle_id):
        return self.d[vehicle_id]


class Db:
    def __init__(self) -> sqlite3.Connection:
        try:
            # connects to sqlite database file - if path is faulty, creates a new and empty database
            self._sqliteConnection = sqlite3.connect("file:memdb1?mode=memory", isolation_level=None)
            self._sqliteConnection.execute('PRAGMA synchronous = OFF')
            self._sqliteConnection.execute('PRAGMA CACHE_SIZE = 250000')
            self._cursor = self._sqliteConnection.cursor()
            # print('Connection to SQLite-File',dbpath,'>> SUCCESS!')
        except sqlite3.Error as error:
            print('SQLite error: ', error)
        finally:
            pass
        # self._sqliteConnection = sqlite3.connect(dbpath)
        # print('Connection to SQLite-DB >> SUCCESS!')

        # self.event_id_link_dict = {}
        # self.driven_links_dict = LinksForEvent()
        self.link_information_dict = {}

    def setup(path):
        """ clones the database from file into memory, for rocket speeds 
            input: path from simulation outputs """
        xmlpath_nw, xmlpath_evts, xmlpath_vehicles, dbpath = setpaths(path)
        if not os.path.exists(dbpath):
            create_database(dbpath, xmlpath_nw, xmlpath_evts, xmlpath_vehicles)
        conn_file = sqlite3.connect(dbpath)
        sqliteConnection = sqlite3.connect("file:memdb1?mode=memory", isolation_level=None)
        conn_file.backup(sqliteConnection)
        sqliteConnection.close()

    def localcursor(self, path) -> sqlite3.Cursor:
        """ returns the sqlite cursor to execute queries on for the local file database, for small queries """
        xmlpath_nw, xmlpath_evts, xmlpath_vehicles, dbpath = setpaths(path)
        try:
            self.local_conn = sqlite3.connect(dbpath)
            self.local_cursor = self.local_conn.cursor()
        except sqlite3.Error as error:
            print('SQLite error: ', error)
        return self.local_cursor

    def localdisconnect(self):
        """ disconnects and closes the local database """
        self.local_cursor.close()
        self.local_conn.close()

    def disconnect(self):
        """ disconnects and closes the memory database """
        self._cursor.close()
        self._sqliteConnection.close()
        # print('The SQLite connection is closed')
    
    def create_vehicle_list(self) -> list:
        """ creates a list of vehicle ids from the database"""
        return create_vehicleids_list(self._cursor)

    def fetchcursor(self) -> sqlite3.Cursor:
        """ fetches cursor for memory database"""
        return self._cursor

    def get_drtvehicles(self) -> "list[str]":
        """ creates a list containing the drtvehicleids that entered traffic """
        return create_drtvehicleids_list(self._cursor)

    def create_dict_link_info(self) -> "dict":
        """ creates a dictionary with every link id, length and freespeed """
        return create_link_information_dict(self._cursor, self.link_information_dict)
        # return self.link_information_dict

    def calculate_vehicle_information(self, vehicle, link_information_dict, path, listofagents, drt):
        """ function add cursor and opens get vehicle information to calculate all information for vehicle and stores it in the .csv file """
        return get_vehicle_information(self._cursor, vehicle, link_information_dict, path, listofagents, drt)

    # def create_dict_event_id_links(self) -> "dict":
    #     """ reads all vehicle_link_events from DB and stores this information with the event_id as key in a dictionary """
    #     return get_links_for_event_id(self._cursor, self.event_id_link_dict, self.link_information_dict)

    # def create_driven_links_dict(self, vehicleslist: list) -> "dict":
    #     """ creates a dictionary with vehicle id as key for a list of trips as content. each trip contains the necessary informtion, when the vehicle entered and left the link, the length and freespeed """
    #     create_entered_link_dict(vehicleslist, self.event_id_link_dict, self.driven_links_dict, self._cursor)
    #     return self.driven_links_dict

    # def calculate_passenger_occupancy(self, drtvehicleids: list) -> "dict":
    #     """ retrieves information about pickup_dropoff events from DB and stores the passenger amount for each event_id where such an event happened in a dictionary """
    #     return get_passenger_occupancy(drtvehicleids, self._cursor)

    # def calculate_passengers_for_link(self, drtvehicleids: list, dictofPassengerOccupancy: dict, driven_links_dict: dict) -> "dict":
    #     """ uses the previously created dictionary dictofPassengerOccupancy to retrieve how many passengers where in the car and stores that information based on the links (connected by the event_id) in a dictionary """
    #     return get_passengers_for_link(drtvehicleids, dictofPassengerOccupancy, driven_links_dict, self._cursor)

    # def assign_capacity(self, drtvehicleids: list, vehicledict: dict):
    #     """ looks up capacity for each vehicle id in vehicleids in DB and returns capacity and adds it in the vehicledict """
    #     return get_capacity(drtvehicleids, vehicledict, self._cursor)


    # unneccesary atm

    # def get_vehicle_entered_links(self,ids) -> "LinksForEvent":
    #     create_dict_entered_links(ids, self._cursor,self.entered_dict)
    #     return self.entered_dict

    # def get_vehicle_left_links(self,ids) -> "LinksForEvent":
    #     create_dict_left_links(ids, self._cursor,self.left_dict)
    #     return self.left_dict

    # def get_link(self, event_id):
    #     return self.event_id_link_dict[event_id]

    # def get_time(self, event_id):
    #     return get_time_for_event_id(event_id, self._cursor)


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
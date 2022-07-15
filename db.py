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
            # if the computer crashes for some reason, try changing the parameter PRAGMA CACHE_SIZE to a lower amount
            ramsize = getfromconfig('settings','ram')
            if ramsize == '32':
                self._sqliteConnection.execute('PRAGMA CACHE_SIZE = 140000')
            elif ramsize == '64':
                self._sqliteConnection.execute('PRAGMA CACHE_SIZE = 250000')
            else:
                self._sqliteConnection.execute('PRAGMA CACHE_SIZE = 75000')
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
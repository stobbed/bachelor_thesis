import gzip
import xml.etree.cElementTree as ET
import sqlite3
import sys
from config import *
from timeit import default_timer as timer
import os.path

def create_database():

    # set timer to get elapsed time in seconds
    start = timer()

    # set up paths first, then start script in python console
    # !!!make sure the database file doesnt exist already!!!

    # xmlpath_nw = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.output_network.xml.gz'
    # xmlpath_evts = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.output_events.xml.gz'

    # create database
    print('connecting to database...')
    try:
        sqliteConnection = sqlite3.connect(dbpath)
    except sqlite3.error as error:
        sys.exit('Failed to connect to database: ', error, '...Quitting.')
    print('connection established!')

    # open network xml
    xmlpath = xmlpath_nw
    if os.path.exists(xmlpath):
        print('opening xml.gz file...')
        file = gzip.open(xmlpath, mode='rt', encoding='UTF-8')
        print('file opened!')
    else:
        raise FileNotFoundError('Invalid path (xmlpath): '+xmlpath+' - *.xml.gz file doesn\'t exist.')
        
    

    # single nodes can be deleted from RAM after parsing using iterparse() function and an iterator
    # set up iterator for network xml
    print('setting up parser...')
    parser = ET.iterparse(file, events=('start', 'end'), parser=ET.XMLParser(encoding='UTF-8'))
    parser = iter(parser)
    event, root = parser.__next__()
    print('parser set!')

    # create nodes and links table
    print('creating database cursor...')
    cursor = sqliteConnection.cursor()
    print('cursor created!')

    print('\ncreating network node and link tables...\n')
    query = '''CREATE TABLE network_nodes (
                node_id TEXT NOT NULL PRIMARY KEY,
                x REAL,
                y REAL);'''
    try:
        cursor.execute(query)
        print('created network_nodes table')
    except sqlite3.Error as error:
        print('Error when creating network_nodes table: ', error)

    query = '''CREATE TABLE network_links (
                link_id TEXT NOT NULL PRIMARY KEY,
                from_node TEXT,
                to_node TEXT,
                length REAL,
                capacity REAL,
                freespeed REAL,
                permlanes INTEGER,
                oneway INTEGER, 
                modes TEXT);'''
    try:
        cursor.execute(query)
        print('created network_links table')
    except sqlite3.Error as error:
        print('Error when creating network_links table: ', error)

    # parse through all events of file and clear each node after parsing
    # get data rows to add into sqlite table
    print('\nfetching network node and link data from xml...\n')
    node_record = []
    link_record = []
    i = 1;
    for event, elem in parser:
        if (event == 'end' and elem.tag == 'node'):
            if str(elem.attrib['id']).startswith("pt") and publictransport_ignore == True:
                pass
            else:
                node_record.append(elem.attrib['id'])
                node_record.append(elem.attrib['x'])
                node_record.append(elem.attrib['y'])
                query = '''INSERT INTO network_nodes
                            VALUES (?, ?, ?)'''
                try:
                    cursor.execute(query, node_record)
                except sqlite3.Error as error:
                    print('Error when inserting node record into network_nodes table: ', error)

                finally:
                    node_record = []
            elem.clear()
            root.clear()
        elif (event == 'end' and elem.tag == 'link'):
            if str(elem.attrib['id']).startswith("pt") and publictransport_ignore == True:
                pass
            else:
                link_record.append(elem.attrib['id'])
                link_record.append(elem.attrib['from'])
                link_record.append(elem.attrib['to'])
                link_record.append(elem.attrib['length'])
                link_record.append(elem.attrib['capacity'])
                link_record.append(elem.attrib['freespeed'])
                link_record.append(elem.attrib['permlanes'])
                link_record.append(elem.attrib['oneway'])
                link_record.append(elem.attrib['modes'])
                query = '''INSERT INTO network_links
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
                try:
                    cursor.execute(query, link_record)
                except sqlite3.Error as error:
                    print('Error when inserting link record into network_links table: ', error)
                finally:
                    link_record = []
            elem.clear()
            root.clear()
    print('network data fetched and in database!')

    # open event xml
    xmlpath = xmlpath_evts
    if os.path.exists(xmlpath):
        print('opening xml.gz file...')
        file = gzip.open(xmlpath, mode='rt', encoding='UTF-8')
        print('file opened!')
    else:
        raise FileNotFoundError('Invalid path (xmlpath): '+xmlpath+' - *.xml.gz file doesn\'t exist.')

    # single nodes can be deleted from RAM after parsing using iterparse() function and an iterator
    # set up iterator for event xml
    print('setting up parser...')
    parser = ET.iterparse(file, events=('start', 'end'), parser=ET.XMLParser(encoding='UTF-8'))
    parser = iter(parser)
    event, root = parser.__next__()
    print('parser set!')

    print('\ncreating tables for events and event types...\n')
    # create events table
    print('creating events table...')
    query = '''CREATE TABLE events (
                event_id INTEGER NOT NULL PRIMARY KEY,
                time REAL NOT NULL,
                type_id INTEGER NOT NULL,
                vehicle TEXT);'''
    try:
        cursor.execute(query)
        print('created event table')
    except sqlite3.Error as error:
        print('Error when creating event table: ', error)

    # create enum table for types (hard coded!)
    print('creating type table...')
    query = '''CREATE TABLE types (
                type_id INTEGER NOT NULL PRIMARY KEY,
                type TEXT NOT NULL);'''
    try:
        cursor.execute(query)
        print('created event types table (enum replacement for structure keeping through databases)')
    except sqlite3.Error as error:
        print('Error when creating event types table: ', error)

    query = '''INSERT INTO types
                VALUES  (1, 'actend'),
                        (2, 'departure'),
                        (3, 'PersonEntersVehicle'),
                        (4, 'vehicle enters traffic'),
                        (5, 'coldEmissionevent'),
                        (6, 'warmEmissionevent'),
                        (7, 'left link'),
                        (8, 'entered link'),
                        (9, 'vehicle leaves traffic'),
                        (10, 'PersonLeavesVehicle'),
                        (11, 'arrival'),
                        (12, 'actstart'),
                        (13, 'travelled'),
                        (14, 'VehicleArrivesAtFacility'),
                        (15, 'VehicleDepartsAtFacility'),
                        (16, 'TransitDriverStarts'),
                        (17, 'waitingForPt'),
                        (18, 'stuckAndAbort'),
                        (19, 'vehicle aborts'),
                        (20, 'dvrpTaskStarted'),
                        (21, 'dvrpTaskEnded'),
                        (22, 'DrtRequest submitted'),
                        (23, 'PassengerRequest scheduled'),
                        (24, 'passenger picked up'),
                        (25, 'passenger dropped off'),
                        (26, 'personMoney'),
                        (-1, '!unknown type!');'''
    try:
        cursor.execute(query)
        print('inserted types table data (hard coded!)')
    except sqlite3.Error as error:
        print('Error when inserting types table: ', error)

    if publictransport_ignore == False:
        print('creating transitdriverstarts_events table...')
        query = '''CREATE TABLE transitdriverstarts_events (
                    transitdriverstarts_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    driverId TEXT,
                    vehicleId TEXT,
                    transitLineId TEXT,
                    transitRouteId TEXT,
                    departureId INTEGER);'''
        try:
            cursor.execute(query)
            print('created transitdriverstarts_event table')
        except sqlite3.Error as error:
            print('Error when creating transitdriverstarts_event table: ', error)

        print('creating waitingforpt_events table...')
        query = '''CREATE TABLE waitingforpt_events (
                    waitingforpt_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    agent INTEGER,
                    atStop TEXT,
                    destinationStop TEXT);'''
        try:
            cursor.execute(query)
            print('created waitingforpt_events table')
        except sqlite3.Error as error:
            print('Error when creating waitingforpt_events table: ', error)

        print('creating vehicle_facility_events table...')
        query = '''CREATE TABLE vehicle_facility_events (
                    vehicle_facility_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    vehicle INTEGER,
                    facility INTEGER,
                    delay REAL);'''
        try:
            cursor.execute(query)
            print('created vehicle_facility_events table')
        except sqlite3.Error as error:
            print('Error when creating vehicle_facility_events table: ', error)

    print('creating stuckandabort_events table...')
    query = '''CREATE TABLE stuckandabort_events (
                stuckandabort_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                link INTEGER,
                legMode TEXT);'''
    try:
        cursor.execute(query)
        print('created stuckandabort_events table')
    except sqlite3.Error as error:
        print('Error when creating stuckandabort_events table: ', error)

    print('creating vehicleaborts_events table...')
    query = '''CREATE TABLE vehicleaborts_events (
                vehicleaborts_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                link INTEGER,
                vehicle INTEGER);'''
    try:
        cursor.execute(query)
        print('created vehicleaborts_events table')
    except sqlite3.Error as error:
        print('Error when creating vehicleaborts_events table: ', error)

    # create actStart and actEnd type events table
    print('creating act_events table...')
    query = '''CREATE TABLE act_events (
                act_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                link INTEGER,
                actType TEXT);'''
    try:
        cursor.execute(query)
        print('created act_events table')
    except sqlite3.Error as error:
        print('Error when creating act_events table: ', error)

    # create departure and arrival events type table
    print('creating dep_arr_events table...')
    query = '''CREATE TABLE dep_arr_events (
                dep_arr_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                link INTEGER,
                legMode TEXT);'''
    try:
        cursor.execute(query)
        print('created departure and arrival events table as dep_arr_events')
    except sqlite3.Error as error:
        print('Error when creating dep_arr_events table: ', error)

    print('creating travelled_events type table...')
    query = '''CREATE TABLE travelled_events (
                travelled_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                distance REAL);'''
    try:
        cursor.execute(query)
        print('created travelled_events table')
    except sqlite3.Error as error:
        print('Error when creating travelled_events table: ', error)

    print('creating vehicle_link_events table...')
    query = '''CREATE TABLE vehicle_link_events (
                vehicle_link_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                link INTEGER,
                vehicle INTEGER,
                left_entered TEXT);'''
    try:
        cursor.execute(query)
        print('created vehicle_link_events table')
    except sqlite3.Error as error:
        print('Error when creating vehicle_link_events table: ', error)

    print('creating person_vehicle_events table...')
    query = '''CREATE TABLE person_vehicle_events (
                person_vehicle_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                vehicle INTEGER);'''
    try:
        cursor.execute(query)
        print('created person_vehicle_events table')
    except sqlite3.Error as error:
        print('Error when creating person_vehicle_events table: ', error)

    print('creating vehicle_traffic_events table...')
    query = '''CREATE TABLE vehicle_traffic_events (
                vehicle_traffic_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                link INTEGER,
                vehicle INTEGER,
                networkMode TEXT,
                relativePosition REAL);'''
    try:
        cursor.execute(query)
        print('created vehicle_traffic_events table')
    except sqlite3.Error as error:
        print('Error when creating vehicle_traffic_events table: ', error)

    print('creating dvrpTask_events table...')
    query = '''CREATE TABLE dvrpTask_events (
                dvrpTask_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                link INTEGER,
                dvrpVehicle TEXT,
                taskType TEXT,
                taskIndex INTEGER,
                dvrpMode TEXT);'''
    try:
        cursor.execute(query)
        print('created dvrpTask_events table')
    except sqlite3.Error as error:
        print('Error when creating dvrpTask_events table: ', error)

    print('creating DrtRequest_events table...')
    query = '''CREATE TABLE DrtRequest_events (
                DrtRequest_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                mode TEXT,
                request TEXT,
                fromLink INTEGER,
                toLink INTEGER,
                unsharedRideTime REAL,
                unsharedRideDistance REAL);'''
    try:
        cursor.execute(query)
        print('created DrtRequest_events table')
    except sqlite3.Error as error:
        print('Error when creating DrtRequest_events table: ', error)

    print('creating PassengerRequest_events table...')
    query = '''CREATE TABLE PassengerRequest_events (
                PassengerRequest_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                mode TEXT,
                request TEXT,
                vehicle TEXT,
                pickupTime REAL,
                dropoffTime REAL);'''
    try:
        cursor.execute(query)
        print('created PassengerRequest_events table')
    except sqlite3.Error as error:
        print('Error when creating PassengerRequest_events table: ', error)

    print('creating PassengerPickedUpDropOff_events table...')
    query = '''CREATE TABLE PassengerPickedUpDropOff_events (
                PassengerPickUp_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                mode TEXT,
                request TEXT,
                vehicle TEXT,
                pickup_dropoff INTEGER);'''
    try:
        cursor.execute(query)
        print('created PassengerPickedUpDropOff_events table')
    except sqlite3.Error as error:
        print('Error when creating PassengerPickedUpDropOff_events table: ', error)

    print('creating enteredlink_events table...')
    query = '''CREATE TABLE enteredlink_events (
                event_id INTEGER NOT NULL,
                link INTEGER,
                vehicle INTEGER);'''
    try:
        cursor.execute(query)
        print('created enteredlink_events table')
    except sqlite3.Error as error:
        print('Error when creating enteredlink_events table: ', error)

    print('creating leftlink_events table...')
    query = '''CREATE TABLE leftlink_events (
                event_id INTEGER NOT NULL,
                link INTEGER,
                vehicle INTEGER);'''
    try:
        cursor.execute(query)
        print('created leftlink_events table')
    except sqlite3.Error as error:
        print('Error when creating leftlink_events table: ', error)

    print('creating personMoney_events table...')
    query = '''CREATE TABLE personMoney_events (
                personMoney_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                person INTEGER,
                amount REAL,
                purpose TEXT,
                transactionPartner TEXT);'''
    try:
        cursor.execute(query)
        print('created personMoney_events table')
    except sqlite3.Error as error:
        print('Error when creating personMoney_events table: ', error)

    # parse through all events of file and clear each node after parsing
    # get data rows to add into sqlite table
    print('\nfetching event data from xml...\n')
    single_row = []
    i = 1
    for event, elem in parser:
        if (event == 'end' and elem.tag == 'event'):
            if i % 5000000 == 0:
                print('parsed through', i, 'events')
            # events table with time and type
            single_row.append(i)
            single_row.append(elem.attrib['time'])
            if elem.attrib['type'] == 'actend':
                single_row.append(1)
            elif elem.attrib['type'] == 'departure':
                single_row.append(2)
            elif elem.attrib['type'] == 'PersonEntersVehicle':
                single_row.append(3)
            elif elem.attrib['type'] == 'vehicle enters traffic':
                single_row.append(4)
            elif elem.attrib['type'] == 'coldEmissionevent':
                single_row.append(5)
            elif elem.attrib['type'] == 'warmEmissionevent':
                single_row.append(6)
            elif elem.attrib['type'] == 'left link':
                single_row.append(7)
            elif elem.attrib['type'] == 'entered link':
                single_row.append(8)
            elif elem.attrib['type'] == 'vehicle leaves traffic':
                single_row.append(9)
            elif elem.attrib['type'] == 'PersonLeavesVehicle':
                single_row.append(10)
            elif elem.attrib['type'] == 'arrival':
                single_row.append(11)
            elif elem.attrib['type'] == 'actstart':
                single_row.append(12)
            elif elem.attrib['type'] == 'travelled':
                single_row.append(13)
            elif elem.attrib['type'] == 'VehicleArrivesAtFacility':
                single_row.append(14)
            elif elem.attrib['type'] == 'VehicleDepartsAtFacility':
                single_row.append(15)
            elif elem.attrib['type'] == 'TransitDriverStarts':
                single_row.append(16)
            elif elem.attrib['type'] == 'waitingForPt':
                single_row.append(17)
            elif elem.attrib['type'] == 'stuckAndAbort':
                single_row.append(18)
            elif elem.attrib['type'] == 'vehicle aborts':
                single_row.append(19)
            elif elem.attrib['type'] == 'dvrpTaskStarted':
                single_row.append(20)
            elif elem.attrib['type'] == 'dvrpTaskEnded':
                single_row.append(21)
            elif elem.attrib['type'] == 'DrtRequest submitted':
                single_row.append(22)
            elif elem.attrib['type'] == 'PassengerRequest scheduled':
                single_row.append(23)
            elif elem.attrib['type'] == 'passenger picked up':
                single_row.append(24)
            elif elem.attrib['type'] == 'passenger dropped off':
                single_row.append(25)
            elif elem.attrib['type'] == 'personMoney':
                single_row.append(26)
            else:
                single_row.append(-1)
                print('could not insert due to unknown type:',elem.attrib)
            if elem.attrib['type'] == 'left link' or elem.attrib['type'] == 'entered link':
                single_row.append(elem.attrib['vehicle'])
            elif elem.attrib['type'] == 'dvrpTaskStarted' or elem.attrib['type'] == 'dvrpTaskEnded':
                single_row.append(elem.attrib['dvrpVehicle'])
            elif elem.attrib['type'] == 'actstart' or elem.attrib['type'] == 'actend':
                if elem.attrib['actType'] == 'DrtStay' or elem.attrib['actType'] == 'DrtBusStop':
                    single_row.append(elem.attrib['person'])
                else:
                    single_row.append('None')
            elif elem.attrib['type'] == 'vehicle enters traffic' or elem.attrib['type'] == 'vehicle leaves traffic':
                single_row.append(elem.attrib['vehicle'])
            else:
                single_row.append('None')
            query = '''INSERT INTO events(event_id, time, type_id, vehicle)
                        VALUES (?, ?, ?, ?);'''
            try:
                if publictransport_ignore == True and str(single_row[3]).startswith('pt') or str(single_row[3]).startswith('freigth') or single_row[2] == 14 or single_row[2] == 15 or single_row[2] == 16 or single_row[2] == 17:
                    pass
                else:
                    cursor.execute(query, single_row)
            except sqlite3.Error as error:
                print('Error when inserting row into events table: ', error)
            finally:
                single_row = []


            # actstart and actend type table
            publictransport_event = False
            if elem.attrib['type'] == 'actstart' or elem.attrib['type'] == 'actend':
                if elem.attrib['actType'] == 'pt interaction' and publictransport_ignore == True:
                    publictransport_event = True
                else:
                    single_row.append(i)
                    single_row.append(elem.attrib['person'])
                    single_row.append(elem.attrib['link'])
                    single_row.append(elem.attrib['actType'])
                    query = '''INSERT INTO act_events(event_id, person, link, actType)
                                VALUES (?, ?, ?, ?);'''
                    try:
                        cursor.execute(query, single_row)
                    except sqlite3.Error as error:
                        print('Error when inserting row into act_events table: ', error)
                    finally:
                        single_row = []
            elif elem.attrib['type'] == 'departure' or elem.attrib['type'] == 'arrival':
                if str(elem.attrib['link']).startswith("pt") and publictransport_ignore == True:
                    publictransport_event = True
                else:
                    single_row.append(i)
                    single_row.append(elem.attrib['person'])
                    single_row.append(elem.attrib['link'])
                    single_row.append(elem.attrib['legMode'])
                    query = '''INSERT INTO dep_arr_events(event_id, person, link, legMode)
                                VALUES (?, ?, ?, ?);'''
                    try:
                        cursor.execute(query, single_row)
                    except sqlite3.Error as error:
                        print('Error when inserting row into dep_arr_events table: ', error)
                    finally:
                        single_row = []
            elif elem.attrib['type'] == 'travelled':
                single_row.append(i)
                single_row.append(elem.attrib['person'])
                single_row.append(elem.attrib['distance'])
                query = '''INSERT INTO travelled_events(event_id, person, distance)
                            VALUES (?, ?, ?);'''
                try:
                    cursor.execute(query, single_row)
                except sqlite3.Error as error:
                    print('Error when inserting row into travelled_events table: ', error)
                finally:
                    single_row = []
            elif elem.attrib['type'] == 'PersonEntersVehicle' or elem.attrib['type'] == 'PersonLeavesVehicle':
                if str(elem.attrib['vehicle']).startswith("pt") and publictransport_ignore == True:
                    publictransport_event = True
                else:
                    single_row.append(i)
                    single_row.append(elem.attrib['person'])
                    single_row.append(elem.attrib['vehicle'])
                    query = '''INSERT INTO person_vehicle_events(event_id, person, vehicle)
                                VALUES (?, ?, ?);'''
                    try:
                        cursor.execute(query, single_row)
                    except sqlite3.Error as error:
                        print('Error when inserting row into person_vehicle_events table: ', error)
                    finally:
                        single_row = []
            elif elem.attrib['type'] == 'vehicle enters traffic' or elem.attrib['type'] == 'vehicle leaves traffic':
                if str(elem.attrib['link']).startswith("pt") and publictransport_ignore == True:
                    publictransport_event = True
                else:
                    single_row.append(i)
                    single_row.append(elem.attrib['person'])
                    single_row.append(elem.attrib['link'])
                    single_row.append(elem.attrib['vehicle'])
                    single_row.append(elem.attrib['networkMode'])
                    single_row.append(elem.attrib['relativePosition'])
                    query = '''INSERT INTO vehicle_traffic_events(event_id, person, link, vehicle, networkMode, relativePosition)
                                VALUES (?, ?, ?, ?, ?, ?);'''
                    try:
                        cursor.execute(query, single_row)
                    except sqlite3.Error as error:
                        print('Error when inserting row into vehicle_traffic_events table: ', error)
                    finally:
                        single_row = []
            elif elem.attrib['type'] == 'left link' or elem.attrib['type'] == 'entered link':
                if str(elem.attrib['link']).startswith("pt") and publictransport_ignore == True:
                    publictransport_event = True
                else:
                    single_row.append(i)
                    single_row.append(elem.attrib['link'])
                    single_row.append(elem.attrib['vehicle'])
                    if elem.attrib['type'] == 'left link':
                        single_row.append('left')
                    elif elem.attrib['type'] == 'entered link':
                        single_row.append('entered')
                    query = '''INSERT INTO vehicle_link_events(event_id, link, vehicle, left_entered)
                                VALUES (?, ?, ?, ?);'''
                    try:
                        cursor.execute(query, single_row)
                    except sqlite3.Error as error:
                        print('Error when inserting row into vehicle_link_events table: ', error)
                    finally:
                        single_row.pop()
                        if elem.attrib['type'] == 'entered link':
                            query = '''INSERT INTO enteredlink_events(event_id, link, vehicle)
                                VALUES (?, ?, ?);'''
                            try:
                                cursor.execute(query, single_row)
                            except sqlite3.Error as error:
                                print('Error when inserting row into enteredlink_events table: ', error)
                        if elem.attrib['type'] == 'left link':
                            query = '''INSERT INTO leftlink_events(event_id, link, vehicle)
                                VALUES (?, ?, ?);'''
                            try:
                                cursor.execute(query, single_row)
                            except sqlite3.Error as error:
                                print('Error when inserting row into leftlink_events table: ', error)
                        single_row = []
            elif elem.attrib['type'] == 'VehicleArrivesAtFacility' or elem.attrib['type'] == 'VehicleDepartsAtFacility':
                if str(elem.attrib['vehicle']).startswith("pt") and publictransport_ignore == True:
                    publictransport_event = True
                else:
                    single_row.append(i)
                    single_row.append(elem.attrib['vehicle'])
                    single_row.append(elem.attrib['facility'])
                    single_row.append(elem.attrib['delay'])
                    query = '''INSERT INTO vehicle_facility_events(event_id, vehicle, facility, delay)
                                VALUES (?, ?, ?, ?);'''
                    try:
                        cursor.execute(query, single_row)
                    except sqlite3.Error as error:
                        print('Error when inserting row into vehicle_facility_events table: ', error)
                    finally:
                        single_row = []
            elif elem.attrib['type'] == 'TransitDriverStarts':
                if str(elem.attrib['driverId']).startswith("pt") and publictransport_ignore == True:
                    publictransport_event = True
                else:
                    single_row.append(i)
                    single_row.append(elem.attrib['driverId'])
                    single_row.append(elem.attrib['vehicleId'])
                    single_row.append(elem.attrib['transitLineId'])
                    single_row.append(elem.attrib['transitRouteId'])
                    single_row.append(elem.attrib['departureId'])
                    query = '''INSERT INTO transitdriverstarts_events(event_id, driverId, vehicleId, transitLineId, transitRouteId, departureId)
                                VALUES (?, ?, ?, ?, ?, ?);'''
                    try:
                        cursor.execute(query, single_row)
                    except sqlite3.Error as error:
                        print('Error when inserting row into transitdriverstarts_events table: ', error)
                    finally:
                        single_row = []
            elif elem.attrib['type'] == 'waitingForPt':
                if publictransport_ignore == True:
                    publictransport_event = True
                else:
                    single_row.append(i)
                    # could also implement writing down the person here
                    single_row.append(elem.attrib['agent'])
                    single_row.append(elem.attrib['atStop'])
                    single_row.append(elem.attrib['destinationStop'])
                    query = '''INSERT INTO waitingforpt_events(event_id, agent, atStop, destinationStop)
                                VALUES (?, ?, ?, ?);'''
                    try:
                        cursor.execute(query, single_row)
                    except sqlite3.Error as error:
                        print('Error when inserting row into waitingforpt_events table: ', error)
                    finally:
                        single_row = []
            elif elem.attrib['type'] == 'vehicle aborts':
                single_row.append(i)
                single_row.append(elem.attrib['link'])
                single_row.append(elem.attrib['vehicle'])
                query = '''INSERT INTO vehicleaborts_events(event_id, link, vehicle)
                            VALUES (?, ?, ?);'''
                try:
                    cursor.execute(query, single_row)
                except sqlite3.Error as error:
                    print('Error when inserting row into vehicleaborts_events table: ', error)
                finally:
                    single_row = []
            elif elem.attrib['type'] == 'stuckAndAbort' and 'link' in elem.attrib:
                single_row.append(i)
                single_row.append(elem.attrib['link'])
                single_row.append(elem.attrib['legMode'])
                single_row.append(elem.attrib['person'])
                query = '''INSERT INTO stuckandabort_events(event_id, link, legMode, person)
                            VALUES (?, ?, ?, ?);'''
                try:
                    cursor.execute(query, single_row)
                except sqlite3.Error as error:
                    print('Error when inserting row into stuckandabort_events table: ', error)
                finally:
                    single_row = []
            elif elem.attrib['type'] == 'dvrpTaskStarted' or elem.attrib['type'] == 'dvrpTaskEnded':
                single_row.append(i)
                single_row.append(elem.attrib['person'])
                single_row.append(elem.attrib['link'])
                single_row.append(elem.attrib['dvrpVehicle'])
                single_row.append(elem.attrib['taskType'])
                single_row.append(elem.attrib['taskIndex'])
                single_row.append(elem.attrib['dvrpMode'])
                query = '''INSERT INTO dvrpTask_events(event_id, person, link, dvrpVehicle, taskType, taskIndex, dvrpMode)
                            VALUES (?, ?, ?, ?, ?, ?, ?);'''
                try:
                    cursor.execute(query, single_row)
                except sqlite3.Error as error:
                    print('Error when inserting row into dvrpTask_events table: ', error)
                finally:
                    single_row = []
            elif elem.attrib['type'] == 'DrtRequest submitted':
                single_row.append(i)
                single_row.append(elem.attrib['person'])
                single_row.append(elem.attrib['mode'])
                single_row.append(elem.attrib['request'])
                single_row.append(elem.attrib['fromLink'])
                single_row.append(elem.attrib['toLink'])
                single_row.append(elem.attrib['unsharedRideTime'])
                single_row.append(elem.attrib['unsharedRideDistance'])
                query = '''INSERT INTO DrtRequest_events(event_id, person, mode, request, fromLink, toLink, unsharedRideTime, unsharedRideDistance)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?);'''
                try:
                    cursor.execute(query, single_row)
                except sqlite3.Error as error:
                    print('Error when inserting row into DrtRequest_events table: ', error)
                finally:
                    single_row = []
            elif elem.attrib['type'] == 'PassengerRequest scheduled':
                single_row.append(i)
                single_row.append(elem.attrib['person'])
                single_row.append(elem.attrib['mode'])
                single_row.append(elem.attrib['request'])
                single_row.append(elem.attrib['vehicle'])
                single_row.append(elem.attrib['pickupTime'])
                single_row.append(elem.attrib['dropoffTime'])
                query = '''INSERT INTO PassengerRequest_events(event_id, person, mode, request, vehicle, pickupTime, dropoffTime)
                            VALUES (?, ?, ?, ?, ?, ?, ?);'''
                try:
                    cursor.execute(query, single_row)
                except sqlite3.Error as error:
                    print('Error when inserting row into PassengerRequest_events table: ', error)
                finally:
                    single_row = []
            elif elem.attrib['type'] == 'passenger picked up' or elem.attrib['type'] == 'passenger dropped off':
                single_row.append(i)
                single_row.append(elem.attrib['person'])
                single_row.append(elem.attrib['mode'])
                single_row.append(elem.attrib['request'])
                single_row.append(elem.attrib['vehicle'])
                if elem.attrib['type'] == 'passenger picked up':
                    single_row.append(0)
                elif elem.attrib['type'] == 'passenger dropped off':
                    single_row.append(1)
                query = '''INSERT INTO PassengerPickedUpDropOff_events(event_id, person, mode, request, vehicle, pickup_dropoff)
                            VALUES (?, ?, ?, ?, ?, ?);'''
                try:
                    cursor.execute(query, single_row)
                except sqlite3.Error as error:
                    print('Error when inserting row into PassengerPickedUpDropOff_events table: ', error)
                finally:
                    single_row = []
            elif elem.attrib['type'] == 'personMoney':
                single_row.append(i)
                single_row.append(elem.attrib['person'])
                single_row.append(elem.attrib['amount'])
                single_row.append(elem.attrib['purpose'])
                single_row.append(elem.attrib['transactionPartner'])
                query = '''INSERT INTO personMoney_events(event_id, person, amount, purpose, transactionPartner)
                            VALUES (?, ?, ?, ?, ?);'''
                try:
                    cursor.execute(query, single_row)
                except sqlite3.Error as error:
                    print('Error when inserting row into personMoney_events table: ', error)
                finally:
                    single_row = []
            else:
                print('Found unknown type: ', elem.attrib)
            elem.clear()
            root.clear()
            #i+=1
        i = i + 1

    print('\nxml to db conversion finished!\n')

    print('improving query performance through index creation')
    query = '''CREATE INDEX idx_events_time
            ON events(time);'''
    try:
        cursor.execute(query)
    except sqlite3.Error as error:
        print('Error: ', error)

    query = '''CREATE INDEX idx_events_type
            ON events(type_id);'''
    try:
        cursor.execute(query)
    except sqlite3.Error as error:
        print('Error: ', error)
    print('...index creation completed!\n')
    sqliteConnection.commit()
    print('committed changes in tables to database file')
    cursor.close()
    print('cursor closed.')
    sqliteConnection.close()
    print('connection to database closed.')

    end = timer()
    duration = end-start
    print('\n Elapsed time: ', duration)
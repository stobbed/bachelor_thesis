from collections import defaultdict
import pickle

# from regex import D
from database_operations import query_db
from vtypes import *

# testtrip = Trip('Münzstraße', '123')
# testtrip2 = Trip('Berliner Straße', '234')
# print(testtrip.street)
# event_id = '123'
# globals()[f"evt_{event_id}"] = Trip('Münzstraße', '123')
# print(evt_123)


def create_drtvehicleids_list(cursor):
    """ creates a list containing the drtvehicleids that entered traffic
        input: cursor
        output: drtvehicleids (list of ids) """
    # extracting the vehicle ids that executed traffic events from the DB
    print("Retrieving Vehicle IDS from database file")
    query = '''  SELECT vehicle FROM vehicle_traffic_events'''
    vehicleiddata = query_db(query, cursor)

    # creating empty lists
    var = []
    drtvehicleids = []

    # creating a list from the list with tuples inside that come from SQLITE
    for item in vehicleiddata:
        for x in item:
            var.append(x)

    # writing the used drt vehicles into the variable drtvehicles
    for aussortieren in var:
        if str(aussortieren).startswith("drt") == True:
            drtvehicleids.append(aussortieren)

    # deleting duplicates
    drtvehicleids = list(dict.fromkeys(drtvehicleids))

    print("Vehicle IDS sucessfully stored")
    return drtvehicleids


def create_dict_entered_links(drtvehicleids, cursor, linkdict):
    print("creating dictionary with driven links for each VID")
    query = '''     SELECT l.link, l.event_id, e.time, n.length, n.freespeed
                    FROM (enteredlink_events l INNER JOIN events e ON e.event_id == l.event_id)
                    INNER JOIN network_links n ON l.link == n.link_id
                    WHERE vehicle = ?'''
    for id in drtvehicleids:
        linkdict.add(id, get_links_for_VID(id, query, cursor))
    print("successfully created dictionary with VID and links")


def create_dict_left_links(drtvehicleids, cursor, linkdict):
    print("creating dictionary with driven links for each VID")
    query = '''     SELECT l.link, l.event_id, e.time, n.length, n.freespeed
                    FROM (leftlink_events l INNER JOIN events e ON e.event_id == l.event_id)
                    INNER JOIN network_links n ON l.link == n.link_id
                    WHERE vehicle = ?'''
    for id in drtvehicleids:
        linkdict.add(id, get_links_for_VID(id, query, cursor))
    print("successfully created dictionary with VID and links")
    

def get_links_for_VID(id, query, cursor) -> "list[Trip]":
    db_output = query_db(query, cursor, id)
    res = []
    for tuple in db_output:
        link = tuple[0]
        event_id = tuple[1]
        entered_time = tuple[2]
        link_length = tuple[3]
        link_freespeed = tuple[4]
        res.append(Trip(link, event_id, entered_time,
                   link_length, link_freespeed))
    return res

def create_vehicle_dict(vehicleids, enteredlinks):
    vehicledict = {}
    for id in vehicleids:
        vehicledict[id] = calculate_distance_roadpct(id, enteredlinks.gettrips(id))
    return vehicledict

def calculate_distance_roadpct(id, enteredlinks_for_id):
    print("calculating distance and roadpct...")

    # evtl. speeds anpassen
    in_town_max = 51 / 3.6
    out_town_max = 101 / 3.6

    totaldistance = 0
    intown = 0
    countryroad = 0
    highway = 0
    for trips in enteredlinks_for_id:
        totaldistance += trips.link_length
        if trips.link_freespeed <= in_town_max:
            intown += trips.link_length
        if trips.link_freespeed < out_town_max and trips.link_freespeed > in_town_max:
            countryroad += trips.link_length
        if trips.link_freespeed >= out_town_max:
            highway += trips.link_length
        trips.link
        intownpct = intown/totaldistance
        countryroadpct = countryroad/totaldistance
        highwaypct = highway/totaldistance
    vehicleinfo = Vehicle(id, totaldistance, intownpct, countryroadpct, highwaypct)
    return vehicleinfo

def create_fleet_information(vehicledict, vehicles):
    fleetdistance = 0
    maximum_distance = 0
    for id in vehicles:
        fleetdistance += vehicledict[id].traveleddistance
        if vehicledict[id].traveleddistance > maximum_distance:
            maximum_distance = vehicledict[id].traveleddistance
            roadpct = []
            roadpct.append(vehicledict[id].intown_pct)
            roadpct.append(vehicledict[id].countryroad_pct)
            roadpct.append(vehicledict[id].highway_pct)
    return Fleet(vehicledict, fleetdistance, maximum_distance, roadpct)

def get_passenger_occupancy(drtvehicleids, dictofVIDandLinks, cursor):
    occupancy_query = '''SELECT event_id, person, request, pickup_dropoff FROM PassengerPickedUpDropOff_events WHERE vehicle = ?'''
    # drivenlinks_query = '''SELECT event_id FROM enteredlink_events WHERE vehicle = ? AND link = ?'''
    drivenlinks_query = '''SELECT event_id, link, vehicle FROM enteredlink_events'''
    db_output_links = query_db(drivenlinks_query, cursor)
    dictofPassengerOccupancy = defaultdict(list)
    for id in drtvehicleids:
        db_output_occupancy = query_db(occupancy_query, cursor, id)
        passengers = 0
        for tuple in db_output_occupancy:
            if tuple[3] == 0:
                passengers += 1
            elif tuple[3] == 1:
                passengers -= 1
            occupancytuple = (tuple[0], passengers, tuple[2])
            dictofPassengerOccupancy[id].append(occupancytuple)

        # for link in dictofVIDandLinks[id]:
        #     db_output_links = query_db(drivenlinks_query, cursor, id, link)
        #     print(id, link)
        #     print(db_output_links)


def picklefile_write(filename, content):
    with open(filename, 'wb') as fp:
        pickle.dump(content, fp)

def picklefile_read(filename):
    with open(filename, 'rb') as fp:
        content = pickle.load(fp)
    return content


# ------------------------------ not needed atm --------------------------------------------------

def create_dict_vid_distance_roadpct(dictofVIDandLinks, dictofLinks_Length, dictofLinks_Freespeed, drtvehicleids):
    print("creating dictionaries with VID and distance, as well as roadpct...")
    dictofVIDandDistance = {}
    dictofVIDandRoadPct = defaultdict(list)

    in_town_max = 51 / 3.6
    out_town_max = 101 / 3.6

    for id in drtvehicleids:
        dictofVIDandDistance[id] = 0
        roadpctlist = []
        roadpctlist.append(0)
        roadpctlist.append(0)
        roadpctlist.append(0)
        for links in dictofVIDandLinks[id]:
            dictofVIDandDistance[id] += dictofLinks_Length[str(links)]
            if dictofLinks_Freespeed[str(links)] <= in_town_max:
                roadpctlist[0] += dictofLinks_Length[str(links)]
            if dictofLinks_Freespeed[str(links)] <= out_town_max and dictofLinks_Freespeed[str(links)] > in_town_max:
                roadpctlist[1] += dictofLinks_Length[str(links)]
            if dictofLinks_Freespeed[str(links)] > out_town_max:
                roadpctlist[2] += dictofLinks_Length[str(links)]
        roadpctlist[0] = roadpctlist[0]/dictofVIDandDistance[id]
        roadpctlist[1] = roadpctlist[1]/dictofVIDandDistance[id]
        roadpctlist[2] = roadpctlist[2]/dictofVIDandDistance[id]
        dictofVIDandRoadPct[id] = roadpctlist
    return dictofVIDandRoadPct, dictofVIDandDistance

# aktuell unnecessary
def create_dict_linkinformation(cursor):
    print("creating dictionaries with link ids, length and freespeed...")
    query = ''' SELECT link_id, length, freespeed FROM network_links '''
    linkslist_fromdb = query_db(query, cursor)

    dictofLinks_Length = {}
    dictofLinks_Freespeed = {}
    for tuple in linkslist_fromdb:
        key = tuple[0]
        dictofLinks_Length[key] = tuple[1]
        dictofLinks_Freespeed[key] = tuple[2]
    print("successfully created dictionaries with link ids, length and freespeed")
    return dictofLinks_Length, dictofLinks_Freespeed
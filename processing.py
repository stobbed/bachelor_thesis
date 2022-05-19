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

# def get_speeds_for_link_and_id(enteredlinks, leftlinks, vehicleslist, cursor):
#     for id in vehicleslist:
#         i = 0
#         triplist = enteredlinks.d[id]
#         for trip in triplist:
#             link = trip.link
#             lefttripslist = leftlinks.d[id]
#             z = 0
#             for lefttrip in lefttripslist:
#                 if lefttrip.link == link and z >= i-5 and z <= i+5:
#                     enteredlinks.d[id][i].left_time = lefttrip.entered_time
#                     print(enteredlinks.d[id][i].entered_time)
#                     print(enteredlinks.d[id][i].left_time)
#                     print(link)
#                     print(lefttrip.link)
#                 z += 1
#             if enteredlinks.d[id][i].left_time > enteredlinks.d[id][i].entered_time:
#                 enteredlinks.d[id][i].actual_speed = enteredlinks.d[id][i].link_length / (enteredlinks.d[id][i].left_time - enteredlinks.d[id][i].entered_time)
#                 enteredlinks.d[id][i].speed_pct = enteredlinks.d[id][i].actual_speed / enteredlinks.d[id][i].link_freespeed
#                 if enteredlinks.d[id][i].speed_pct < .2:
#                     times = get_time_for_dvrpTask(id, link, cursor)
#                     if times != None:
#                         for time in times:
#                             if time >= enteredlinks.d[id][i].entered_time and time <= enteredlinks.d[id][i].left_time:
#                                 print('vehicle: ' + str(id) + ' time match entered: ' + str(enteredlinks.d[id][i].entered_time) + ' left: ' + str(enteredlinks.d[id][i].left_time) + ' and stopped at: ' + str(time) + ' on link: ' + str(link))
#                                 print(i)
#                                 print(z)
#                     # print('speed pct: ' + str(enteredlinks.d[id][i].speed_pct) + ' on link: ' + str(enteredlinks.d[id][i].link) + ' for vehicle: ' + str(id))
#                     # print('actual speed: ' + str(enteredlinks.d[id][i].actual_speed))
#                     # print('link speed: ' + str(enteredlinks.d[id][i].link_freespeed))
#             else:
#                 pass
#                 # print('no left time, or does not make sense on: ' + str(enteredlinks.d[id][i].link))
#             i += 1

def get_speeds_for_link_and_id(enteredlinks, leftlinks, vehicleslist, cursor):
    for id in vehicleslist:
        i = 0
        triplist = enteredlinks.d[id]
        for trip in triplist:
            link = trip.link
            lefttripslist = leftlinks.d[id]
            z = 0
            for index in range(i, len(lefttripslist)):
                if index >= i:
                    lefttrip = lefttripslist[index]
                    if lefttrip.link == link and enteredlinks.d[id][i].left_time == -1:
                        enteredlinks.d[id][i].left_time = lefttrip.entered_time
                        # print(index)
                        # print(i)
                        # print(enteredlinks.d[id][i].entered_time)
                        # print(enteredlinks.d[id][i].left_time)
                        # print(link)
                        # print(lefttrip.link)
            if enteredlinks.d[id][i].left_time > enteredlinks.d[id][i].entered_time:
                enteredlinks.d[id][i].actual_speed = enteredlinks.d[id][i].link_length / (enteredlinks.d[id][i].left_time - enteredlinks.d[id][i].entered_time)
                enteredlinks.d[id][i].speed_pct = enteredlinks.d[id][i].actual_speed / enteredlinks.d[id][i].link_freespeed
                if enteredlinks.d[id][i].speed_pct < .2:
                    times = get_time_for_dvrpTask(id, link, cursor)
                    if times != None:
                        for time in times:
                            if time >= enteredlinks.d[id][i].entered_time and time <= enteredlinks.d[id][i].left_time:
                                print('vehicle: ' + str(id) + ' time match entered: ' + str(enteredlinks.d[id][i].entered_time) + ' left: ' + str(enteredlinks.d[id][i].left_time) + ' and stopped at: ' + str(time) + ' on link: ' + str(link))
                                print(i)
                    # print('speed pct: ' + str(enteredlinks.d[id][i].speed_pct) + ' on link: ' + str(enteredlinks.d[id][i].link) + ' for vehicle: ' + str(id))
                    # print('actual speed: ' + str(enteredlinks.d[id][i].actual_speed))
                    # print('link speed: ' + str(enteredlinks.d[id][i].link_freespeed))
            else:
                pass
                # print('no left time, or does not make sense on: ' + str(enteredlinks.d[id][i].link))
            i += 1

def get_speed(vehicleslist, cursor):
    for id in vehicleslist:
        get_links_entered_and_left_for_VID(id, cursor)

def get_links_entered_and_left_for_VID(id, cursor):
    # query = ''' SELECT e.event_id, e.time, type_id, v.link
    #             FROM events e INNER JOIN vehicle_link_events v on v.event_id == e.event_id
    #             WHERE e.vehicle = ? '''
    query = ''' SELECT event_id, time, type_id
                FROM events
                WHERE vehicle = ? '''
    db_output = query_db(query, cursor, id)
    print(id)
    for index in range(0, len(db_output)):
        event_id = db_output[index][0]
        time = db_output[index][1]
        type_id = db_output[index][2]
        # link = db_output[index][3]
        if type_id == 7 or type_id == 8:
            pass
        else:
            print(event_id, time, type_id)

def get_links_for_event_id(cursor, event_id_link_dict):
    query = ''' SELECT v.event_id, v.link, v.left_entered, n.length, n.freespeed
                FROM vehicle_link_events v INNER JOIN network_links n ON v.link == n.link_id'''
    db_output = query_db(query, cursor)
    for tuple in db_output:
        event_id = tuple [0]
        link = tuple [1]
        left_entered = tuple [2]
        length = tuple [3]
        freespeed = tuple [4]
        event_id_link_dict[event_id] = Links(link, length, freespeed)
    return event_id_link_dict

def get_time_for_event_id (event_id, cursor):
    query = ''' SELECT time FROM events WHERE event_id = ?'''
    return query_db(query, cursor, event_id)

# def get_speed2(vehicleslist, cursor):
#     for id in vehicleslist:
#         i = 0
#         query = ''' SELECT e.time, v.link
#                     FROM vehiclelink_events v INNER JOIN events e on e.event_id == v.event_id
#                     WHERE v.vehicle = ? '''

def get_time_for_dvrpTask(vehicleid, link, cursor):
    query = '''     SELECT e.time
                    FROM dvrpTask_events d INNER JOIN events e ON e.event_id == d.event_id
                    WHERE d.dvrpVehicle = ? AND d.link = ? AND d.taskType = ?'''
    taskType = 'STAY'
    db_output = query_db(query, cursor, vehicleid, link, taskType)
    time = []
    for tuple in db_output:
        for entry in tuple:
            time.append(entry)
    if time != []:
        return time

def create_vehicle_dict(vehicleids, enteredlinks):
    vehicledict = {}
    for id in vehicleids:
        vehicledict[id] = calculate_distance_roadpct(id, enteredlinks.gettrips(id))
    return vehicledict

def calculate_distance_roadpct(id, enteredlinks_for_id):
    # print("calculating distance and roadpct...")

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
    distance_intown = 0
    distance_countryroad = 0
    distance_highway = 0
    maximum_distance = 0
    for id in vehicles:
        fleetdistance += vehicledict[id].traveleddistance
        distance_intown += vehicledict[id].traveleddistance * vehicledict[id].intown_pct
        distance_countryroad += vehicledict[id].traveleddistance * vehicledict[id].countryroad_pct
        distance_highway += vehicledict[id].traveleddistance * vehicledict[id].highway_pct
        if vehicledict[id].traveleddistance > maximum_distance:
            maximum_distance = vehicledict[id].traveleddistance
            roadpct = []
            roadpct.append(vehicledict[id].intown_pct)
            roadpct.append(vehicledict[id].countryroad_pct)
            roadpct.append(vehicledict[id].highway_pct)
    return Fleet(vehicledict, fleetdistance, distance_intown, distance_countryroad, distance_highway, maximum_distance, roadpct)

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
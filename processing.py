from audioop import add
from collections import defaultdict
import pickle
from re import I

# from regex import D
from database_operations import query_db
from vtypes import *


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

def create_link_information_dict(cursor, link_information_dict):
    query = ''' SELECT link_id, length, freespeed
                FROM network_links'''
    db_output = query_db(query, cursor)
    for tuple in db_output:
        link_information_dict[tuple[0]] = Links(tuple[0], tuple[1], tuple[2])

def get_links_for_event_id(cursor, event_id_link_dict, link_information_dict):
    # query = ''' SELECT v.event_id, v.link, v.left_entered, n.length, n.freespeed
    #             FROM vehicle_link_events v INNER JOIN network_links n ON v.link == n.link_id'''
    query = ''' SELECT event_id, link, left_entered
                FROM vehicle_link_events '''
    db_output = query_db(query, cursor)
    for tuple in db_output:
        event_id = tuple [0]
        link = tuple [1]
        left_entered = tuple [2]
        length = link_information_dict[str(link)].length
        freespeed = link_information_dict[str(link)].freespeed
        event_id_link_dict[event_id] = Links(link, length, freespeed, left_entered)
    return event_id_link_dict

def create_entered_link_dict(vehicleslist, event_id_link_dict, driven_links_dict, cursor):
    for id in vehicleslist:
        query = ''' SELECT event_id, time, type_id, vehicle
                FROM events 
                WHERE vehicle = ?'''
        db_output = query_db(query, cursor, id)
        driven_links_dict.d[id] = []
        tripindex = 0
        for index in range(0, len(db_output)):
            event_id = db_output[index][0]
            time = db_output[index][1]
            type_id = db_output[index][2]
            vehicle = db_output[index][3]
            if type_id == 8:
                trip = event_id_link_dict[event_id]
                link = trip.link
                length = trip.length
                freespeed = trip.freespeed
                driven_links_dict.d[vehicle].append(Trip(link, event_id, time, length, freespeed))
                tripindex += 1
            elif type_id == 7:
                if tripindex != 0:
                    if db_output[index-1][2] == 8 and driven_links_dict.d[vehicle][tripindex-1].link == event_id_link_dict[event_id].link:
                        # print(vehicledict.d[vehicle][tripindex-1].time, time)
                        entered_index = tripindex -1
                        driven_links_dict.d[vehicle][entered_index].actual_speed = driven_links_dict.d[vehicle][entered_index].link_length/(time - driven_links_dict.d[vehicle][entered_index].entered_time)
                        driven_links_dict.d[vehicle][entered_index].speed_pct = driven_links_dict.d[vehicle][entered_index].actual_speed/driven_links_dict.d[vehicle][entered_index].link_freespeed
                        # add_left_time_to_link(vehicle, entered_index, time, driven_links_dict)
            elif type_id == 4 and db_output[index+1][2] == 7:
                stop1 = False
                stop2 = False
                index_entered_link = index
                index_left_link = index + 1
                index_entered_traffic = index
                index_left_traffic = index
                while db_output[index_entered_link][2] != 8 and stop1 == False:
                    if index_entered_link == 1:
                        stop1 = True
                    index_entered_link -= 1
                while db_output[index_left_traffic][2] != 9 and stop2 == False:
                    if index_left_traffic== 1:
                        stop2 = True
                    index_left_traffic -= 1
                query = ''' SELECT link FROM vehicle_traffic_events WHERE event_id = ?'''
                if index_left_traffic != 0:
                    link_entered_traffic = query_db(query, cursor, db_output[index_entered_traffic][0])[0]
                    link_left_traffic = query_db(query, cursor, db_output[index_left_traffic][0])[0]
                    if event_id_link_dict[db_output[index_entered_link][0]].link == link_entered_traffic[0] and link_left_traffic[0] == link_entered_traffic[0] and event_id_link_dict[db_output[index_entered_link][0]].link == event_id_link_dict[db_output[index_left_link][0]].link:
                        time_spent_outside_traffic = db_output[index_entered_traffic][1] - db_output[index_left_traffic][1]
                        time_difference = db_output[index_left_traffic][1] - db_output[index_entered_link][1] + db_output[index_left_link][1] - db_output[index_entered_traffic][1]
                        left_time_corrected = db_output[index_left_link][1] - time_spent_outside_traffic
                        i = 0
                        for trip in driven_links_dict.d[id]:
                            if trip.event_id == db_output[index_entered_link][0]:
                                index_entered_link_corrected = i
                            i += 1
                        driven_links_dict.d[vehicle][index_entered_link_corrected].actual_speed = driven_links_dict.d[vehicle][index_entered_link_corrected].link_length/(left_time_corrected - driven_links_dict.d[vehicle][index_entered_link_corrected].entered_time)
                        driven_links_dict.d[vehicle][index_entered_link_corrected].speed_pct = driven_links_dict.d[vehicle][index_entered_link_corrected].actual_speed/driven_links_dict.d[vehicle][index_entered_link_corrected].link_freespeed
                        driven_links_dict.d[vehicle][index_entered_link_corrected].corrected = True
                        # add_left_time_to_link(vehicle, index_entered_link_corrected, left_time_corrected, driven_links_dict, corrected)

            # wenn Fahrzeug Traffic leaved, trz volle Link Länge mit einrechnen und Freespeed annehmen
            # für Passenger Pickup Events, Zeit des Pickups rausrechnen
            # Idee: Zeit bei Vehicle Leaves Traffic stoppen (left trafffic time - entered link time + left link time - entered traffic time)                     

def vehicle_enters_traffic_event(event_id_link_dict, driven_links_dict, db_output, vehicle, index, cursor):
    stop1 = False
    stop2 = False
    index_entered_link = index
    index_left_link = index + 1
    index_entered_traffic = index
    index_left_traffic = index
    while db_output[index_entered_link][2] != 8 and stop1 == False:
        if index_entered_link == 1:
            stop1 = True
        index_entered_link -= 1
    while db_output[index_left_traffic][2] != 9 and stop2 == False:
        if index_left_traffic== 1:
            stop2 = True
        index_left_traffic -= 1
        query = ''' SELECT link FROM vehicle_traffic_events WHERE event_id = ?'''
        if index_left_traffic != 0:
            link_entered_traffic = query_db(query, cursor, db_output[index_entered_traffic][0])[0]
            link_left_traffic = query_db(query, cursor, db_output[index_left_traffic][0])[0]
            if event_id_link_dict[db_output[index_entered_link][0]].link == link_entered_traffic[0] and link_left_traffic[0] == link_entered_traffic[0] and event_id_link_dict[db_output[index_entered_link][0]].link == event_id_link_dict[db_output[index_left_link][0]].link:
                time_spent_outside_traffic = db_output[index_entered_traffic][1] - db_output[index_left_traffic][1]
                time_difference = db_output[index_left_traffic][1] - db_output[index_entered_link][1] + db_output[index_left_link][1] - db_output[index_entered_traffic][1]
                left_time_corrected = db_output[index_left_link][1] - time_spent_outside_traffic
                i = 0
                for trip in driven_links_dict.d[id]:
                    if trip.event_id == db_output[index_entered_link][0]:
                        index_entered_link_corrected = i
                    i += 1
                driven_links_dict.d[vehicle][index_entered_link_corrected].actual_speed = driven_links_dict.d[vehicle][index_entered_link_corrected].link_length/(left_time_corrected - driven_links_dict.d[vehicle][index_entered_link_corrected].entered_time)
                driven_links_dict.d[vehicle][index_entered_link_corrected].speed_pct = driven_links_dict.d[vehicle][index_entered_link_corrected].actual_speed/driven_links_dict.d[vehicle][index_entered_link_corrected].link_freespeed
                driven_links_dict.d[vehicle][index_entered_link_corrected].corrected = True
                # add_left_time_to_link(vehicle, index_entered_link_corrected, left_time_corrected, driven_links_dict, corrected)

def calculate_potential_error_rate(vehicleslist, driven_links_dict):
    error = {}
    sumtrips = 0
    sumerror = 0
    for id in vehicleslist:
        counter = 0
        for trip in driven_links_dict.d[id]:
            if trip.corrected == False and trip.actual_speed == -1 or trip.speed_pct < .2:
                counter += 1
        error[id] = [len(driven_links_dict.d[id]), counter]
        sumtrips += len(driven_links_dict.d[id])
        sumerror += counter

    print('total of: ' + str(sumtrips) + ' trips, with ' + str(sumerror) + ' potential errors"')


def create_vehicle_dict(vehicleids, driven_links_dict):
    print("Creating vehicle dictionary...")
    vehicledict = {}
    for id in vehicleids:
        vehicledict[id] = calculate_distance_roadpct(id, driven_links_dict.gettrips(id))
    print("Succesfully created vehicle dictionary")
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

def get_passenger_occupancy(drtvehicleids, cursor):
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
        print(' ')
        print(id)
        print(dictofPassengerOccupancy[id])
    return dictofPassengerOccupancy

        # for link in dictofVIDandLinks[id]:
        #     db_output_links = query_db(drivenlinks_query, cursor, id, link)
        #     print(id, link)
        #     print(db_output_links)

def get_passengers_for_link(drtvehicleids, dictofPassengerOccupancy, driven_links_dict, cursor):
    for id in drtvehicleids:
        print('writing passengers into trip information for ' + str(id))
        for index in range(0, len(dictofPassengerOccupancy[id])):
            link_for_task = get_link_for_dvrpTask_event(dictofPassengerOccupancy[id][index], id, cursor)
            if index != len(dictofPassengerOccupancy[id])-1:
                link_for_next_task = get_link_for_dvrpTask_event(dictofPassengerOccupancy[id][index+1], id, cursor)
            else:
                link_for_next_task = None
            # if db_output == []:
            #     db_output = query_db(query, cursor, id, time[0][0]+1)
            start = False
            stop = False
            for tripindex in range(0, len(driven_links_dict.d[id])):
                trip = driven_links_dict.d[id][tripindex]
                if trip.link == link_for_task and start == False and stop == False:
                    # print(id, db_output[0][0])
                    start = True
                if link_for_next_task != None:
                    if trip.link == link_for_next_task and stop == False:
                        stop = True
                if start == True and stop == False:
                    driven_links_dict.d[id][tripindex].passengers = dictofPassengerOccupancy[id][index][1]

def get_link_for_dvrpTask_event(passenger_event, id, cursor):
    query = ''' SELECT d.link FROM dvrpTask_events d INNER JOIN events e ON e.event_id == d.event_id WHERE d.dvrpVehicle = ? AND e.time = ?'''
    time = get_time_for_event_id(passenger_event[0], cursor)
    passengers = passenger_event[1]
    drt_request = passenger_event[2]
    db_output = query_db(query, cursor, id, time[0][0])
    return db_output[0][0]


def picklefile_write(filename, content):
    with open(filename, 'wb') as fp:
        pickle.dump(content, fp)

def picklefile_read(filename):
    with open(filename, 'rb') as fp:
        content = pickle.load(fp)
    return content

def get_time_for_event_id (event_id, cursor):
    query = ''' SELECT time FROM events WHERE event_id = ?'''
    return query_db(query, cursor, event_id)

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

# def create_dict_entered_links(drtvehicleids, cursor, linkdict):
#     print("creating dictionary with driven links for each VID")
#     query = '''     SELECT l.link, l.event_id, e.time, n.length, n.freespeed
#                     FROM (enteredlink_events l INNER JOIN events e ON e.event_id == l.event_id)
#                     INNER JOIN network_links n ON l.link == n.link_id
#                     WHERE vehicle = ?'''
#     for id in drtvehicleids:
#         linkdict.add(id, get_links_for_VID(id, query, cursor))
#     print("successfully created dictionary with VID and links")


# def create_dict_left_links(drtvehicleids, cursor, linkdict):
#     print("creating dictionary with driven links for each VID")
#     query = '''     SELECT l.link, l.event_id, e.time, n.length, n.freespeed
#                     FROM (leftlink_events l INNER JOIN events e ON e.event_id == l.event_id)
#                     INNER JOIN network_links n ON l.link == n.link_id
#                     WHERE vehicle = ?'''
#     for id in drtvehicleids:
#         linkdict.add(id, get_links_for_VID(id, query, cursor))
#     print("successfully created dictionary with VID and links")

# def get_links_for_VID(id, query, cursor) -> "list[Trip]":
#     db_output = query_db(query, cursor, id)
#     res = []
#     for tuple in db_output:
#         link = tuple[0]
#         event_id = tuple[1]
#         entered_time = tuple[2]
#         link_length = tuple[3]
#         link_freespeed = tuple[4]
#         res.append(Trip(link, event_id, entered_time,
#                    link_length, link_freespeed))
#     return res

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

# def get_links_entered_and_left_for_VID(id, cursor):
#     # query = ''' SELECT e.event_id, e.time, type_id, v.link
#     #             FROM events e INNER JOIN vehicle_link_events v on v.event_id == e.event_id
#     #             WHERE e.vehicle = ? '''
#     query = ''' SELECT event_id, time, type_id
#                 FROM events
#                 WHERE vehicle = ? '''
#     db_output = query_db(query, cursor, id)
#     print(id)
#     for index in range(0, len(db_output)):
#         event_id = db_output[index][0]
#         time = db_output[index][1]
#         type_id = db_output[index][2]
#         # link = db_output[index][3]
#         if type_id == 7 or type_id == 8:
#             pass
#         else:
#             print(event_id, time, type_id)
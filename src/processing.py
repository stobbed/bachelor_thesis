# (CC) Dustin Stobbe, 2022

# this python file contains all sort of functions needed to analyze the MATSIM outputs
# in order to return the vehicleinfo.csv

from collections import defaultdict
import pickle
import os.path
import os
from datetime import datetime
import csv
import pandas as pd
import xml.etree.cElementTree as ET
import sqlite3
import numpy

from configuration import *
from database_operations import query_db
from vtypes import *

def create_drtvehicleids_list(cursor: sqlite3.Cursor) -> list:
    """ creates a list containing the drtvehicleids that entered traffic
        input: cursor
        output: drtvehicleids (list of ids) """
    # extracting the vehicle ids that executed traffic events from the DB
    # print("Retrieving Vehicle IDS from database file...")
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
        if str(aussortieren).startswith("drt") or str(aussortieren).startswith("taxi"):
            drtvehicleids.append(aussortieren)

    # deleting duplicates
    drtvehicleids = list(dict.fromkeys(drtvehicleids))

    # print("...Vehicle IDS sucessfully stored")
    return drtvehicleids

def create_vehicleids_list(cursor: sqlite3.Cursor) -> list:
    """ creates a list containing the vehicleids that entered traffic
        input: cursor
        output: vehicleids (list of ids) """
    # extracting the vehicle ids that executed traffic events from the DB
    # print("Retrieving Vehicle IDS from database file...")
    query = '''  SELECT vehicle FROM vehicle_traffic_events'''
    vehicleiddata = query_db(query, cursor)

    # creating empty lists
    var = []
    vehicleids = []

    # creating a list from the list with tuples inside that come from SQLITE
    for item in vehicleiddata:
        for x in item:
            var.append(x)

    # writing the used drt vehicles into the variable drtvehicles
    for aussortieren in var:
        if not (str(aussortieren).startswith("freight") or str(aussortieren).startswith("drt") or str(aussortieren).startswith("taxi")):
            vehicleids.append(aussortieren)

    # deleting duplicates
    vehicleids = list(dict.fromkeys(vehicleids))

    # print("...Vehicle IDS sucessfully stored")
    return vehicleids

def create_personlist(path: str, simulationname: str) -> list:
    """ creates a list with passengers from the in the config specified region by reading and filtering from the output_persons.csv.gz in the MATSIM output folder"""
    # read in compressed csv file
    data = pd.read_csv(os.path.join(path, simulationname + '.output_persons.csv.gz'), compression='gzip')
    # retrieve region to filte for from config.ini
    region = getfromconfig('settings', 'region')
    listofagents = []
    # parse through contents of read in csv
    for line in data._values:
        # extracting the home regioon information from csv row
        text = str(line).split(";")
        agent = text[0].replace("['","")
        homeregion = text[-1].replace("']","")
        if homeregion == region:
            listofagents.append(int(agent))
    return listofagents

def match_passengers_and_cars(listofagents: list, vehiclesllist: list) -> list:
    """ compares the two lists, containg the list of agents and the vehicleslist.. since currently each vehicle for a passenger is named exactly the same
        if this however changes this part should be adapted accordingly """
    
    agents = set(listofagents)
    vehicles = set(vehiclesllist)

    # calculate the intersection of the two sets thereby reducing the number of vehicles to parse through drastically
    usedvehicles = agents & vehicles
    return usedvehicles

def create_link_information_dict(cursor: sqlite3.Cursor, link_information_dict: dict) -> "dict":
    """ creates a dictionary with every link id, length and freespeed """
    # print("creating link_information_dict..." + str(gettime()))
    query = ''' SELECT link_id, length, freespeed
                FROM network_links'''
    db_output = query_db(query, cursor)
    # iterate through db_output list of tuples and store information contained in tuple in dictionary in a Class called Links
    for tuple in db_output:
        link_information_dict[tuple[0]] = Links(tuple[0], tuple[1], tuple[2])
    # print("...succesfully created link_information_dict!" + str(gettime()))
    return link_information_dict

def create_results_dir(path: str):
    ''' creates a direcotry called results in the MATSIM outputs folder for each scenario '''
    if not os.path.exists(os.path.join(path,'results')):
        os.mkdir(os.path.join(path,'results'))
    # if os.path.exists(os.path.join(path, 'results', getsimulationname(path) + '_vehicleinfo.csv')):
    #     os.remove(os.path.join(path, 'results', getsimulationname(path) + '_vehicleinfo.csv'))

def get_vehicle_information(cursor: sqlite3.Cursor, vehicle: str, link_information_dict: dict, path: str, listofagents: list, drt_status = True):
    ''' primary function that gets called for every vehicle inside the multiprocessing 
        first gets the driven links and if drt_status = True goes through all events
        and adds the information how many passengers where present in the car on which link'''
    event_id_link_dict = get_links_for_vehicleid(cursor, vehicle, link_information_dict)
    driven_links = create_entered_link_list(vehicle, event_id_link_dict, cursor, listofagents)
    del event_id_link_dict
    # if drt_status == True:
    #     passengeroccupancy = get_passenger_occupancy(vehicle, cursor)
    #     driven_links = get_passengers_for_link(vehicle, passengeroccupancy, driven_links, cursor)
    #     del passengeroccupancy
    if len(driven_links) > 0:
        vehicleinfo = create_vehicle_info(vehicle, driven_links)
        if drt_status == True:
            vehicleinfo.capacity = get_capacity(vehicle, cursor)
        del driven_links
        vinfo = []
        keys = []
        for nis in vehicleinfo.__dict__:
            vinfo.append(vehicleinfo.__dict__[nis])
        filename = os.path.join(path, 'results', getsimulationname(path) + '_vehicleinfo.csv')
        with open(filename,'a') as file:
            writer_object = csv.writer(file)
            writer_object.writerow(vinfo)
            file.close()   


def get_links_for_vehicleid(cursor: sqlite3.Cursor, vehicle: str, link_information_dict: dict) -> "dict":
    """ reads all vehicle_link_events from DB and stores this information with the event_id as key in a dictionary"""
    # print("creating event_id_link_dict... ", str(gettime()))
    query = ''' SELECT event_id, link, left_entered
                FROM vehicle_link_events WHERE vehicle = ?'''
    db_output = query_db(query, cursor, vehicle)
    event_id_link_dict = {}
    # iterate through db_output list of tuples and store information contained in tuple in dictionary with event_id as key
    # and store the information contained in the link_information_dict for this link as well
    for tuple in db_output:
        event_id = tuple [0]
        link = tuple [1]
        left_entered = tuple [2]
        # retrieve information for link from link_information_dict
        length = link_information_dict[str(link)].length
        freespeed = link_information_dict[str(link)].freespeed
        event_id_link_dict[event_id] = Links(link, length, freespeed, left_entered)
    # print("...succesfully created event_id_link_dict! ", str(gettime()))
    return event_id_link_dict

def create_entered_link_list(vehicle: str, event_id_link_dict: dict, cursor: sqlite3.Cursor, listofagents: list) -> list:
    """ creates a list of trips as content. 
        each trip contains the necessary informtion, when the vehicle entered and left the link, the length and freespeed
        this script als calculates the actual speeed, as well as the percentual speed it therefore reached"""
    # print("creating entered_link_dict... ", str(gettime()))
    query = ''' SELECT event_id, time, type_id, vehicle
            FROM events 
            WHERE vehicle = ?'''
    query_passengerequest = ''' SELECT person
                                FROM PassengerRequest_events
                                WHERE event_id = ? '''
    query_passengervehicle = ''' SELECT person
                                 FROM person_vehicle_events
                                 WHERE event_id = ?'''
    # retrieve all events for given vehicle from DB
    db_output = query_db(query, cursor, vehicle)
    driven_links = []
    tripindex = 0
    passengerfromregion = 0
    passengernotfromregion = 0
    passengers = 0
    # iterate through db_output with an index
    for index in range(0, len(db_output)):
        if not (str(vehicle).startswith("drt") or str(vehicle).startswith("taxi")):
            passengerfromregion = 1
            passengers = 1
        event_id = db_output[index][0]
        time = db_output[index][1]
        type_id = db_output[index][2]
        vehicle = db_output[index][3]
        # type_id = 23, PassengerRequest scheduled event, by counting upp passengerfromregion/ notregion allocates distance driven empty to passenger to passenger
        if type_id == 23:
            db_output_request = query_db(query_passengerequest, cursor, event_id)
            if (str(vehicle).startswith("drt") or str(vehicle).startswith("taxi")):
                if int(db_output_request[0][0]) in listofagents:
                    passengerfromregion += 1
                else:
                    passengernotfromregion += 1
        # type_id = 8 means entered link and therefore appends the dictionary with the Class trip and its information
        if type_id == 8:
            trip = event_id_link_dict[event_id]
            link = trip.link
            length = trip.length
            freespeed = trip.freespeed
            driven_links.append(Trip(link, event_id, time, length, freespeed, passengerfromregion, passengernotfromregion, passengers))
            tripindex += 1
        # type_id = 7 means left link
        elif type_id == 7:
            # checks if its the first interaction of the car, since then there could be no entered link before that
            if tripindex != 0:
                # if the previous event of the car was entering this particular link, stores 
                if db_output[index-1][2] == 8 and driven_links[tripindex-1].link == event_id_link_dict[event_id].link:
                    entered_index = tripindex -1
                    driven_links[entered_index].left_time = time
                    driven_links[entered_index].actual_speed = driven_links[entered_index].link_length/(time - driven_links[entered_index].entered_time)
                    driven_links[entered_index].speed_pct = driven_links[entered_index].actual_speed/driven_links[entered_index].link_freespeed
        # type_id = 24 means passenger picked up, and therefore counts up the passenger count
        elif type_id == 24:
            passengers += 1
        # type_id == 4 means vehicle enters traffic, therefore further calculation is required
        elif type_id == 4 and db_output[index+1][2] == 7 and index > 0:
            stop1 = False
            stop2 = False
            index_entered_link = index
            index_left_link = index + 1
            index_entered_traffic = index
            index_left_traffic = index
            # search for an event prior to entering traffic where the vehicle entered the link and storing its index
            while db_output[index_entered_link][2] != 8 and stop1 == False:
                # stop condition, so index always stays above 0
                if index_entered_link == 1:
                    stop1 = True
                index_entered_link -= 1
            # search for an event prior to entering traffic, where the vehicle left traffic and store its index
            while db_output[index_left_traffic][2] != 9 and stop2 == False:
                # stop condition, so index always stays above 0
                if index_left_traffic== 1:
                    stop2 = True
                index_left_traffic -= 1
            query = ''' SELECT link FROM vehicle_traffic_events WHERE event_id = ?'''
            # if index for left_traffic was found and is not 0...
            if index_left_traffic > 0 and index_entered_link > 0:
                # looks up the link for the event_id corresponding to the entered and left traffic events
                link_entered_traffic = query_db(query, cursor, db_output[index_entered_traffic][0])[0]
                link_left_traffic = query_db(query, cursor, db_output[index_left_traffic][0])[0]
                # checks if links are a match and then calculates the time spent outside of traffic and only uses time on link for speed calculation
                if event_id_link_dict[db_output[index_entered_link][0]].link == link_entered_traffic[0] and link_left_traffic[0] == link_entered_traffic[0] and event_id_link_dict[db_output[index_entered_link][0]].link == event_id_link_dict[db_output[index_left_link][0]].link:
                    time_spent_outside_traffic = db_output[index_entered_traffic][1] - db_output[index_left_traffic][1]
                    time_difference = db_output[index_left_traffic][1] - db_output[index_entered_link][1] + db_output[index_left_link][1] - db_output[index_entered_traffic][1]
                    left_time_corrected = db_output[index_left_link][1] - time_spent_outside_traffic
                    i = 0
                    # due to setting the driven_links_dict up as a list, a search for the index matching the event_id where the link was entered is necessary
                    for trip in driven_links:
                        if trip.event_id == db_output[index_entered_link][0]:
                            index_entered_link_corrected = i
                        i += 1
                    driven_links[index_entered_link_corrected].left_time = left_time_corrected
                    driven_links[index_entered_link_corrected].actual_speed = driven_links[index_entered_link_corrected].link_length/(left_time_corrected - driven_links[index_entered_link_corrected].entered_time)
                    driven_links[index_entered_link_corrected].speed_pct = driven_links[index_entered_link_corrected].actual_speed/driven_links[index_entered_link_corrected].link_freespeed
                    driven_links[index_entered_link_corrected].corrected = True
        # type_id = 10 means persons leaves vehicle and therefore removes the allocation of driven distance for passengerfromregion / notregion except the vehicle is not empty
        elif type_id == 10:
            if (str(vehicle).startswith("drt") or str(vehicle).startswith("taxi")):
                db_output_vehicleevent = query_db(query_passengervehicle, cursor, event_id)
                if db_output_vehicleevent[0][0] in listofagents:
                    passengerfromregion -= 1
                elif not (str(db_output_vehicleevent[0][0]).startswith("drt") or str(db_output_vehicleevent[0][0]).startswith("taxi")):
                    passengernotfromregion -=1
        # type_id = 25 means passenger dropped off and therefore subtracts 1 passenger from the passenger amount
        elif type_id == 25:
            passengers -= 1
    # print("...succesfully created entered_link_dict!", str(gettime()))
    return driven_links


def create_vehicle_info(vehicle: str, driven_links: list) -> Vehicle:
    """ calls another function that calculates travelleddistance, road percentages as well as pkm and avgpassenger amounts and much more"""
    vehicleinfo = calculate_distance_roadpct(vehicle, driven_links)
    return vehicleinfo

def calculate_distance_roadpct(vehicle: str, enteredlinks_for_vehicle: list) -> Vehicle:
    """ calculates total driven distance, checks road type and stores road percentages as well as person kilometers (and much more) and returns Vehicle Class with information for vehicle id"""
    # evtl. speeds anpassen
    in_town_max = 51 / 3.6
    out_town_max = 101 / 3.6

    # assigning of variables to add up
    totaldistance = 0
    intown = 0
    pkm_intown = 0
    countryroad = 0
    pkm_countryroad = 0
    highway = 0
    pkm_highway = 0
    totalpassengers = 0
    speed_above_90 = 0; speed_below_70 = 0; speed_below_50 = 0; speed_below_30 = 0; speed_below_10 = 0
    speed_length_sum = 0
    distance_not_from_region = 0
    distance_from_region = 0
    intownpct = 0
    countryroadpct = 0
    highwaypct = 0
    avg_speed = 0
    speed_pct_sum = 0
    avgpassenger_amount = 0
    avgpassenger_without_empty = 0
    trips_without_empty = 0
    pkm_without_empty = 0
    km_without_empty = 0
    # iterate through entered links
    for trips in enteredlinks_for_vehicle:
        if trips.passengerfromregion > 0:
            totaldistance += trips.link_length
            distance_from_region += trips.link_length
            if trips.link_freespeed <= in_town_max:
                intown += trips.link_length
                pkm_intown += trips.link_length * trips.passengers
            if trips.link_freespeed < out_town_max and trips.link_freespeed > in_town_max:
                countryroad += trips.link_length
                pkm_countryroad += trips.link_length * trips.passengers
            if trips.link_freespeed >= out_town_max:
                highway += trips.link_length
                pkm_highway += trips.link_length * trips.passengers
            totalpassengers += trips.passengers
            if trips.passengers > 0:
                avgpassenger_without_empty += trips.passengers
                pkm_without_empty += trips.passengers * trips.link_length
                km_without_empty += trips.link_length
                trips_without_empty += 1
            if trips.actual_speed != -1:
                speed_length_sum += trips.actual_speed * trips.link_length
                speed_pct_sum += trips.speed_pct * trips.link_length
            intownpct = intown/totaldistance
            countryroadpct = countryroad/totaldistance
            highwaypct = highway/totaldistance
            if trips.speed_pct >= .9:
                speed_above_90 += trips.link_length
            if trips.speed_pct <= .7:
                speed_below_70 += trips.link_length
            elif trips.speed_pct <= .5:
                speed_below_50 += trips.link_length
            elif trips.speed_pct <= .3:
                speed_below_30 += trips.link_length
            elif trips.speed_pct <= .1:
                speed_below_10 += trips.link_length
        elif trips.passengernotfromregion > 0:
            # if passenger is not from region
            totaldistance += trips.link_length
            distance_not_from_region += trips.link_length
        else:
            #empty_travel
            totaldistance += trips.link_length
            pass
    totalpkm = pkm_intown + pkm_countryroad + pkm_highway
    if trips_without_empty > 0:
        avgpassenger_without_empty = avgpassenger_without_empty / trips_without_empty
        pkm_without_empty = pkm_without_empty / km_without_empty
    if totaldistance > 0:
        avg_speed = (speed_length_sum * 3.6) / totaldistance
        avgpassenger_amount = totalpassengers/len(enteredlinks_for_vehicle)
        speed_pct = speed_pct_sum / totaldistance
    speed_length_sum = speed_length_sum * 3.6
    vehicleinfo = Vehicle(vehicle, totaldistance, intownpct, countryroadpct, highwaypct, pkm_intown, pkm_countryroad, pkm_highway, totalpkm, avgpassenger_amount, avgpassenger_without_empty, pkm_without_empty, avg_speed, speed_pct, speed_length_sum, speed_above_90, speed_below_70, speed_below_50, speed_below_30, speed_below_10, distance_not_from_region, distance_from_region)
    return vehicleinfo


def get_passenger_occupancy(vehicle: str, cursor: sqlite3.Cursor) -> "list":
    """ retrieves information about pickup_dropoff events from DB and stores the passenger amount for each event_id where such an event happened in a list"""
    # print("creating dictionary with occupancy for event_ids... ", str(gettime()))
    occupancy_query = '''SELECT event_id, person, request, pickup_dropoff FROM PassengerPickedUpDropOff_events WHERE vehicle = ?'''
    # drivenlinks_query = '''SELECT event_id, link, vehicle FROM enteredlink_events'''
    # db_output_links = query_db(drivenlinks_query, cursor)
    passengeroccupancy = []
    db_output_occupancy = query_db(occupancy_query, cursor, vehicle)
    passengers = 0
    for tuple in db_output_occupancy:
        if tuple[3] == 0:
            # if tuple[3] == 0 means that a passenger was picked up and therfore increases the passenger amount by 1
            passengers += 1
        elif tuple[3] == 1:
            # if tuple[3] == 1 means that a passenger was dropped off and therfore decreases the passenger amount by 1
            passengers -= 1
        # creates a tuple containg the event_id where the pickup_dropff event occured, passengers at that time, as well as the drt request
        occupancytuple = (tuple[0], passengers, tuple[2])
        passengeroccupancy.append(occupancytuple)
    # print("...created occupancy dictionary! ", str(gettime()))
    return passengeroccupancy

def get_capacity(vehicle: str, cursor: sqlite3.Cursor):
    """ looks up capacity for each vehicle id in vehicleids in DB and returns capacity """
    # print("adding capacity to each vehicle in vehicledict...")
    query = ''' SELECT capacity FROM vehicles WHERE vehicle_id = ?'''
    db_output = query_db(query, cursor, vehicle)
    capacity = db_output[0][0]
    return capacity

def get_link_for_dvrpTask_event(passenger_event: tuple, vehicle: str, cursor: sqlite3.Cursor) -> "int":
    """ requires a passenger_pickup_dropffoff_event as input and a vehicle id and returns the link where this event happened"""
    query = ''' SELECT d.link FROM dvrpTask_events d INNER JOIN events e ON e.event_id == d.event_id WHERE d.dvrpVehicle = ? AND e.time = ?'''
    time = get_time_for_event_id(passenger_event[0], cursor)
    passengers = passenger_event[1]
    drt_request = passenger_event[2]
    db_output = query_db(query, cursor, vehicle, time)
    return db_output[0][0]

def get_time_for_event_id (event_id: int, cursor: sqlite3.Cursor) -> "float":
    """ issues a DB query and returns the matching time to event_id that was entered """
    query = ''' SELECT time FROM events WHERE event_id = ?'''
    time = query_db(query, cursor, event_id)
    return time[0][0]

def calculate_avg_vehicle(path: str) -> dict:
    """ reads the vehicleinfo_finished_csv from the given path (only to the MATSIM output folder in general), calculates averages and returns that information in a dictionary"""
    
    # assin empty variables to count up
    drt_vehicleamount = 0
    drt_totalkm = 0; drt_totalkm_region = 0; drt_totalkm_notregion = 0; drt_totalpkm = 0
    drt_intown_pct = 0; drt_countryroad_pct = 0; drt_highway_pct = 0
    drt_pkm_intown = 0; drt_pkm_countryroad = 0; drt_pkm_highway = 0
    drt_avg_speed = 0; drt_speed_pct = 0; drt_speed_length = 0; drt_speed_above_90 = 0; drt_speed_below_70 = 0; drt_speed_below_50 = 0; drt_speed_below_30 = 0; drt_speed_below_10 = 0
    drt_avgpassenger_amount = 0; drt_avgpassenger_without_empty = 0; drt_pkm_without_empty = 0

    vehicleamount = 0
    totalkm = 0
    intown_pct = 0; countryroad_pct = 0; highway_pct = 0
    avg_speed = 0; speed_pct = 0; speed_length = 0; speed_above_90 = 0; speed_below_70 = 0; speed_below_50 = 0; speed_below_30 = 0; speed_below_10 = 0
    
    small_vehicles = 0; medium_vehicles = 0; large_vehicles = 0
    
    data = pd.read_csv(os.path.join(path, 'results', getsimulationname(path) + '_vehicleinfo_finished.csv'), low_memory=False, header=0, skip_blank_lines=True)
    vehicles = []
    # parsind through read in excel file and reading lines
    for line in data._values:
        # additionally checks for duplicates in the vehicleinfo csv
        checknew = []
        checknew.append(line[0])
        check = set(vehicles) & set(checknew)
        # if check == set() and str(line[0]) != str(-1.0) and str(line[0]) != str(0.0):
        if check == set() and len(str(line[0]))>4:
            vehicles.append(line[0])
            # passenger capacity 2 -> small vehicles
            if line[22] == 2:
                small_vehicles += 1
            # passenger capacity 4 -> medium vehicles
            elif line[22] == 4:
                medium_vehicles += 1
            # passenger capacity 7 -> large vehicles
            elif line[22] == 7:
                large_vehicles += 1
            if str(line[0]).startswith("drt") or str(line[0]).startswith("taxi"):
                drt_vehicleamount += 1
                drt_totalkm += line[1]; drt_totalkm_region += line[21]; drt_totalkm_notregion += line[20]; drt_totalpkm += line[8]
                drt_intown_pct += line[2]; drt_countryroad_pct += line[3]; drt_highway_pct += line[4]
                drt_pkm_intown += line[5]; drt_pkm_countryroad += line[6]; drt_pkm_highway += line[7]
                drt_avg_speed += line[12]; drt_speed_pct += line[13]; drt_speed_length += line[14]; drt_speed_above_90 += line[15]; drt_speed_below_70 += line[16]; drt_speed_below_50 += line[17]; drt_speed_below_30 += line[18]; drt_speed_below_10 += line[19]
                drt_avgpassenger_amount += line[9]; drt_avgpassenger_without_empty += line[10]; drt_pkm_without_empty += line[11]
            else:
                if line[1] > 0:
                    vehicleamount += 1
                    totalkm += line[1]
                    intown_pct += line[2]; countryroad_pct += line[3]; highway_pct += line[4]
                    avg_speed += line[12]; speed_pct += line[13]; speed_length += line[14]; speed_above_90 += line[15]; speed_below_70 += line[16]; speed_below_50 += line[17]; speed_below_30 += line[18]; speed_below_10 += line[19]
        else:
            # print("found duplicate vehicle in csv", line[0])
            pass
    
    # stores all retrieved information the dictionary
    info = {}
    info['drt_vehicleamount'] = drt_vehicleamount
    if drt_vehicleamount > 0:
        info['drt_avg_totalkm_region'] = drt_totalkm_region / drt_vehicleamount
        info['drt_avg_totalkm_notregion'] = drt_totalkm_notregion / drt_vehicleamount
        info['drt_totalkm'] = drt_totalkm
        info['drt_avg_totalkm'] = (drt_totalkm_region + drt_totalkm_notregion) / drt_vehicleamount
        info['drt_avg_totalpkm'] = drt_totalpkm / drt_vehicleamount
        info['drt_avg_intown_pct'] = drt_intown_pct / drt_vehicleamount
        info['drt_avg_countryroad_pct'] = drt_countryroad_pct / drt_vehicleamount
        info['drt_avg_highway_pct'] = drt_highway_pct / drt_vehicleamount
        info['drt_avg_pkm_intown'] = drt_pkm_intown / drt_vehicleamount
        info['drt_avg_pkm_countryroad'] = drt_pkm_countryroad / drt_vehicleamount
        info['drt_avg_pkm_highway'] = drt_pkm_highway / drt_vehicleamount
        info['drt_avg_speed_pervehicle'] = drt_avg_speed / drt_vehicleamount
        info['drt_avg_speed_overlength'] = drt_speed_length / drt_totalkm_region
        info['drt_avg_speed_pct'] = drt_speed_pct / drt_vehicleamount
        info['drt_avg_speed_above_90'] = drt_speed_above_90 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_speed_below_70'] = drt_speed_below_70 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_speed_below_50'] = drt_speed_below_50 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_speed_below_30'] = drt_speed_below_30 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_speed_below_10'] = drt_speed_below_10 / (drt_totalkm_region + drt_totalkm_notregion)
        info['drt_avg_passenger_amount'] = drt_avgpassenger_amount / drt_vehicleamount
        info['drt_avgpassenger_without_empty'] = drt_avgpassenger_without_empty / drt_vehicleamount
        info['drt_pkm_without_empty'] = drt_pkm_without_empty / drt_vehicleamount

        info['small_vehicles'] = small_vehicles
        info['medium_vehicles'] = medium_vehicles
        info['large_vehicles'] = large_vehicles

    info['vehicleamount'] = vehicleamount
    info['totalkm'] = totalkm
    info['avg_totalkm'] = totalkm / vehicleamount
    info['avg_intown_pct'] = intown_pct / vehicleamount
    info['avg_countryroad_pct'] = countryroad_pct / vehicleamount
    info['avg_highway_pct'] = highway_pct / vehicleamount
    info['avg_speed_pervehicle'] = avg_speed / vehicleamount
    info['avg_speed_overlength'] = speed_length / totalkm
    info['avg_speed_pct'] = speed_pct / vehicleamount
    info['avg_speed_above_90'] = speed_above_90 / totalkm
    info['avg_speed_below_70'] = speed_below_70 / totalkm
    info['avg_speed_below_50'] = speed_below_50 / totalkm
    info['avg_speed_below_30'] = speed_below_30 / totalkm
    info['avg_speed_below_10'] = speed_below_10 / totalkm
    return info

def gettime() -> datetime.datetime:
    """ pretty self explanatory, gets the current time and fomats it into HH/MM/SS format """
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time

# ------------------------------ not needed atm --------------------------------------------------

# mainly for debug purposes creation of pickle files and reading them
def picklefile_write(filename: str, content) -> "None":
    """ creates a pickle file with filename (complete path if not in the same directory as the script) and the contents, especially useful for debugging"""
    #file = os.path.join(path_drt, 'pickle', filename)
    file = os.path.join(filename)
    with open(file, 'wb') as fp:
        pickle.dump(content, fp)
   
def picklefile_read(filename: str):
    """ reads the pickle file under filename (complete path if not in the same directory as the script) and returns it contents"""
    # file = os.path.join(path_drt, 'pickle', filename)
    file = os.path.join(filename)
    if os.path.exists(file):
        with open(file, 'rb') as fp:
            content = pickle.load(fp)
    else:
        print(str(filename) + ' does not exist, if the file is not in the same folder as the script make sure to enter the complete directory')
    return content

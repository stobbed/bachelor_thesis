from collections import defaultdict
import os.path
import pickle
from config import simulationdate
from database_operations import query_db

def create_drtvehicleids_list(cursor):
    """ creates a list containing the drtvehicleids that entered traffic 
        input: cursor
        output: drtvehicleids (list of ids) """
    # extracting the vehicle ids that executed traffic events from the DB 
    print("Retrieving Vehicle IDS from database file")
    vehicleid_query= '''  SELECT vehicle FROM vehicle_traffic_events'''
    vehicleiddata = query_db(vehicleid_query, cursor)

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
    drtvehicleids=list(dict.fromkeys(drtvehicleids))

    print("Vehicle IDS sucessfully stored")
    return drtvehicleids

def create_dict_vid_and_links(drtvehicleids, cursor):
    print("creating dictionary with driven links for each VID")
    dictofVIDandLinks = defaultdict(list)
    vehicledrivenlinks_query = '''SELECT link FROM vehicle_link_events WHERE vehicle = ?'''
    for id in drtvehicleids:
        linksforvehicleIDS = query_db(vehicledrivenlinks_query, cursor, id)
        for tuple in linksforvehicleIDS:
            x = tuple[0]
            dictofVIDandLinks[id].append(x)
    print("successfully created dictionary with VID and links")
    return dictofVIDandLinks

def create_dict_links_length_freespeed(cursor):
    print("creating dictionaries with link ids, length and freespeed...")
    getlinksandlength_query = ''' SELECT link_id, length, freespeed FROM network_links '''
    linkslist_fromdb = query_db(getlinksandlength_query, cursor)

    dictofLinks_Length = {}
    dictofLinks_Freespeed = {}
    for tuple in linkslist_fromdb:
        key=tuple[0]
        dictofLinks_Length[key] = tuple[1]
        dictofLinks_Freespeed[key] = tuple[2]
    print("successfully created dictionaries with link ids, length and freespeed")
    return dictofLinks_Length, dictofLinks_Freespeed

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
            if dictofLinks_Freespeed[str(links)] <= out_town_max and dictofLinks_Freespeed[str(links)] >in_town_max:
                roadpctlist[1] += dictofLinks_Length[str(links)]
            if dictofLinks_Freespeed[str(links)] > out_town_max:
                roadpctlist[2] += dictofLinks_Length[str(links)]
        roadpctlist[0] = roadpctlist[0]/dictofVIDandDistance[id]
        roadpctlist[1] = roadpctlist[1]/dictofVIDandDistance[id]
        roadpctlist[2] = roadpctlist[2]/dictofVIDandDistance[id]
        dictofVIDandRoadPct[id] = roadpctlist
    return dictofVIDandRoadPct, dictofVIDandDistance
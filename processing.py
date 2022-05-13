from database_operations import query_db
from collections import defaultdict

def getDictWithLinksFromIds(drtvehicleids, cursor):
    dictofVIDandLinks = defaultdict(list)
    vehicledrivenlinks_query = '''SELECT link FROM vehicle_link_events WHERE vehicle = ?'''
    for id in drtvehicleids:
        linksforvehicleIDS = query_db(vehicledrivenlinks_query, cursor, id)
        for tuple in linksforvehicleIDS:
            x = tuple[0]
            dictofVIDandLinks[id].append(x)
    return dictofVIDandLinks

def create_drtvehicleids_list(cursor):
    """ creates a list containing the drtvehicleids that entered traffic 
        input: cursor
        output: drtvehicleids (list of ids) """
    # extracting the vehicle ids that executed traffic events from the DB 
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
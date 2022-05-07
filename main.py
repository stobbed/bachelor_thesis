from timeit import default_timer as timer
# from get_data_from_db import query_db, query_db_var
from collections import defaultdict
import sqlite3
import os.path
import pickle

# second chance

q_start=timer()

#this is a comment
hallo=timer()

# currently path needs to be adjusted here
dbfile_path = "/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/DBFiles/b-drt-mpm-1pct.db"

# establish database connection
# check if dbfile actually already exists, avoiding empty database creation
if os.path.exists(dbfile_path):
    try:
        # connects to sqlite database file - if path is faulty, creates a new and empty database
        sqliteConnection = sqlite3.connect(dbfile_path)
        cursor = sqliteConnection.cursor()
        print('Connection to SQLite-File',dbfile_path,'>> SUCCESS!')
    except sqlite3.Error as error:
        print('SQLite error: ', error)
    finally:
        pass
else:
    raise FileNotFoundError('Invalid path (dbfile): '+dbfile_path+' - *.db file doesn\'t exist.')

def query_db(sql_query, var = None):
    record = None
    if var == None:
        cursor.execute(sql_query)
    else:
        cursor.execute(sql_query, (var,))
    # save queried table locally in record
    record = cursor.fetchall()
    return record


# extracting the vehicle ids that executed traffic events from the DB 
vehicleid_query= '''  SELECT vehicle FROM vehicle_traffic_events'''
vehicleiddata = query_db(vehicleid_query)

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

# ---------------------------------------------------------

# retrieve driven kilometers per vehicle

# Variante 1
# vehiclelinks_query = ''' SELECT vehicle, link FROM vehicle_link_events '''
# vehiclelinksdb = query_db(vehiclelinks_query)
# dictofVIDandLinks = defaultdict(list)

# for tuple in vehiclelinksdb:
#     # print(tuple)
#     for id in drtvehicleids:
#         if tuple[0] == id:
#             pass
#             x = tuple[1]
#             dictofVIDandLinks[id].append(x)

#comment
#Variante 2
def getDictWithLinksFromIds(drtvehicleids):
    dictofVIDandLinks = defaultdict(list)
    vehicledrivenlinks_query = '''SELECT link FROM vehicle_link_events WHERE vehicle = ?'''
    for id in drtvehicleids:
        linksforvehicleIDS = query_db(vehicledrivenlinks_query, id)
        for tuple in linksforvehicleIDS:
            x = tuple[0]
            dictofVIDandLinks[id].append(x)
    return dictofVIDandLinks


if os.path.exists('dictofVIDandLinks.pickle'):
    with open('dictofVIDandLinks.pickle', 'rb') as fp:
        dictofVIDandLinks = pickle.load(fp)
    print("List of vehicle IDS from .pickle file restored")
else:
    dictofVIDandLinks = getDictWithLinksFromIds(drtvehicleids)
    with open('dictofVIDandLinks.pickle', 'wb') as fp:
        pickle.dump(dictofVIDandLinks, fp)
    print("List of links for each VID created and stored into .pickle file")

# print("List of links for each VID sucessfully stored")

# Variante 3
# dictofVIDandLinks = {}
# for id in drtvehicleids:
#     dictofVIDandLinks[id] = []
#     # list=[]
#     vehicledrivenlinks_query = '''SELECT link FROM vehicle_link_events WHERE vehicle = ?'''
#     linksforvehicleIDS = query_db(vehicledrivenlinks_query, id)
#     #print(query_db_var(vehicledrivenlinks_query, ID))
#     # print(linksforvehicleIDS)
#     for tuple in linksforvehicleIDS:
#         x = tuple[0]
#         dictofVIDandLinks[id].append(x)
#     # dictofVIDandLinks[ID]=list

# extract a dictionary
getlinksandlength_query = ''' SELECT link_id, length, freespeed FROM network_links '''
linkslist_fromdb = query_db(getlinksandlength_query)

dictofLinks_Length = {}
dictofLinks_Freespeed = {}
for tuple in linkslist_fromdb:
    key=tuple[0]
    dictofLinks_Length[key] = tuple[1]
    dictofLinks_Freespeed[key] = tuple[2]

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
    print(dictofVIDandRoadPct[id])

# with open('dictofVIDandLength.csv', 'w') as f:
#     for key in dictofVIDandLength.keys():
#         f.write("%s, %s\n"% (key, dictofVIDandLength[key]))

if (sqliteConnection):
            cursor.close()
            sqliteConnection.close()
            print('The SQLite connection is closed')

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')

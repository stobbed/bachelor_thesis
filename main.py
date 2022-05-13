from timeit import default_timer as timer
# from get_data_from_db import query_db, query_db_var
from collections import defaultdict
import os.path
import pickle
from config import dbpath as dbfile_path

from XML2DB_1pct import create_database
from database_operations import establish_db_connection, query_db, close_db_connection
from processing import create_drtvehicleids_list, getDictWithLinksFromIds

# track time
q_start=timer()
if os.path.exists(dbfile_path):
    print("Up to Date Database already exists, establishing connection to existing database...")
else:
    print('Database does not exist yet, creating database file now...')
    create_database()
    

# # establish database connection
sqliteConnection, cursor = establish_db_connection(dbfile_path)

drtvehicleids = create_drtvehicleids_list(cursor)

# ---------------------------------------------------------

# retrieve driven kilometers per vehicle

if os.path.exists('dictofVIDandLinks.pickle'):
    with open('dictofVIDandLinks.pickle', 'rb') as fp:
        dictofVIDandLinks = pickle.load(fp)
    print("List of vehicle IDS from .pickle file restored")
else:
    dictofVIDandLinks = getDictWithLinksFromIds(drtvehicleids, cursor)
    with open('dictofVIDandLinks.pickle', 'wb') as fp:
        pickle.dump(dictofVIDandLinks, fp)
    print("List of links for each VID created and stored into .pickle file")
    

# extract a dictionary
getlinksandlength_query = ''' SELECT link_id, length, freespeed FROM network_links '''
linkslist_fromdb = query_db(getlinksandlength_query, cursor)

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
    # print(dictofVIDandRoadPct[id])

# with open('dictofVIDandLength.csv', 'w') as f:
#     for key in dictofVIDandLength.keys():
#         f.write("%s, %s\n"% (key, dictofVIDandLength[key]))

close_db_connection(sqliteConnection, cursor)

# time tracking stuff
q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')
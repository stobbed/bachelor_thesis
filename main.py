from timeit import default_timer as timer
# from get_data_from_db import query_db, query_db_var
from collections import defaultdict
import os.path
import pickle

from config import dbpath as dbfile_path
from config import simulationdate

from XML2DB import create_database
from database_operations import establish_db_connection, close_db_connection
from processing import GetLinksForEvent, create_drtvehicleids_list, create_dict_entered_links, create_dict_vid_distance_roadpct, create_dict_linkinformation, get_passenger_occupancy

from types import Db



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

# retrieve driven links for each VID

picklefilename = 'dictofVIDandLinks-' + simulationdate + '.pickle'
if os.path.exists(picklefilename):
    with open(picklefilename, 'rb') as fp:
        dictofVIDandLinks = pickle.load(fp)
    for id in drtvehicleids:
        print(len(dictofVIDandLinks[id]))
        dictofVIDandLinks[id] = list(dict.fromkeys(dictofVIDandLinks[id]))
        print(len(dictofVIDandLinks[id]))
    print("List of vehicle IDS from .pickle file restored")
else:
    print(".pickle file does not exist yet or is not up do date, creating list now and saving as .pickle")
    dictLinks = GetLinksForEvent()
    dictofVIDandLinks = create_dict_entered_links(drtvehicleids, cursor)
    with open(picklefilename, 'wb') as fp:
        pickle.dump(dictofVIDandLinks, fp)
    print("List of links for each VID created and stored into .pickle file")

# create a dictionary with link ids, their length and freespeed
dictofLinks_Length, dictofLinks_Freespeed = create_dict_linkinformation(cursor)

# retrieve Distance and road pct for each VID
dictofVIDandRoadPct, dictofVIDandDistance = create_dict_vid_distance_roadpct(dictofVIDandLinks, dictofLinks_Length, dictofLinks_Freespeed, drtvehicleids)

# with open('dictofVIDandLength.csv', 'w') as f:
#     for key in dictofVIDandLength.keys():
#         f.write("%s, %s\n"% (key, dictofVIDandLength[key]))

get_passenger_occupancy(drtvehicleids, dictofVIDandLinks, cursor)

close_db_connection(sqliteConnection, cursor)

# time tracking stuff
q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')
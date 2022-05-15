from timeit import default_timer as timer
import pickle

from config import dbpath
from db import *

q_start=timer()

db = Db(dbpath)
vehicleslist = db.get_vehicles()
# enteredlinks = db.get_vehicle_entered_links(vehicles)
# leftlinks = db.get_vehicle_left_links(vehicles)

# with open('enteredlinks.pickle', 'wb') as fp:
#     pickle.dump(enteredlinks, fp)
# with open('leftlinks.pickle', 'wb') as fp:
#     pickle.dump(leftlinks, fp)

if os.path.exists('enteredlinks.pickle'):
    with open('enteredlinks.pickle', 'rb') as fp:
        enteredlinks = pickle.load(fp)
else:
    enteredlinks = db.get_vehicle_entered_links(vehicleslist)
    with open('enteredlinks.pickle', 'wb') as fp:
        pickle.dump(enteredlinks, fp)

if os.path.exists('leftlinks.pickle'):
    with open('leftlinks.pickle', 'rb') as fp:
        leftlinks = pickle.load(fp)
else:
    leftlinks = db.get_vehicle_left_links(vehicleslist)
    with open('leftlinks.pickle', 'wb') as fp:
        pickle.dump(leftlinks, fp)

vehicledict = create_vehicle_dict(vehicleslist, enteredlinks)

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')

# def get_link_from_id(trips,id):
#     for trip in trips:
#         if trip.event_id == id:
#             print(trip)


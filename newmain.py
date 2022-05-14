from timeit import default_timer as timer
import pickle

from config import dbpath
from db import *

q_start=timer()

db = Db(dbpath)
vehicles = db.get_vehicles()
enteredlinks = db.get_vehicle_entered_links(vehicles)
leftlinks = db.get_vehicle_left_links(vehicles)

with open('enteredlinks.pickle', 'wb') as fp:
    pickle.dump(enteredlinks, fp)

with open('leftlinks.pickle', 'wb') as fp:
    pickle.dump(leftlinks, fp)

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')

def get_link_from_id(trips,id):
    for trip in trips:
        if trip.event_id == id:
            print(trip)


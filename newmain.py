from timeit import default_timer as timer
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

enteredlinks_pickle = 'enteredlinks.pickle'
if os.path.exists('enteredlinks.pickle'):
    enteredlinks= picklefile_read(enteredlinks_pickle)
else:
    enteredlinks = db.get_vehicle_entered_links(vehicleslist)
    picklefile_write(enteredlinks_pickle, enteredlinks)

leftlinks_pickle = 'leftlinks.pickle'
if os.path.exists(leftlinks_pickle):
    leftlinks = picklefile_read(leftlinks_pickle)
else:
    leftlinks = db.get_vehicle_left_links(vehicleslist)
    picklefile_write(leftlinks_pickle, leftlinks)

vehicledict = create_vehicle_dict(vehicleslist, enteredlinks)
drt = create_fleet_information(vehicledict, vehicleslist)

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')

# def get_link_from_id(trips,id):
#     for trip in trips:
#         if trip.event_id == id:
#             print(trip)


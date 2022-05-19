from timeit import default_timer as timer
from config import dbpath
from db import *

q_start=timer()

db = Db(dbpath)
# print(db.get_time(12354))
vehicleslist = db.get_vehicles()
link_event_id_dict = db.create_dict_event_id_links()

# enteredlinks = db.get_vehicle_entered_links(vehicles)
# leftlinks = db.get_vehicle_left_links(vehicles)

# with open('enteredlinks.pickle', 'wb') as fp:
#     pickle.dump(enteredlinks, fp)
# with open('leftlinks.pickle', 'wb') as fp:
#     pickle.dump(leftlinks, fp)

enteredlinks_pickle = 'enteredlinks.pickle'
if os.path.exists(enteredlinks_pickle):
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

linkdict_pickle = 'linkdict.pickle'
if os.path.exists(linkdict_pickle):
    enteredlinks= picklefile_read(enteredlinks_pickle)
else:
    enteredlinks = db.get_vehicle_entered_links(vehicleslist)
    picklefile_write(enteredlinks_pickle, enteredlinks)

vehicledict = create_vehicle_dict(vehicleslist, enteredlinks)
drt = create_fleet_information(vehicledict, vehicleslist)

# db.get_links_with_id()
# db.get_speed_for_link(vehicleslist)

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')

# def get_link_from_id(trips,id):
#     for trip in trips:
#         if trip.event_id == id:
#             print(trip)


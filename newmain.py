from timeit import default_timer as timer
from config import dbpath
from db import *

q_start=timer()

db = Db(dbpath)
# print(db.get_time(12354))
vehicleslist = db.get_vehicles()
link_information_dict = db.create_dict_link_info()
link_event_id_dict = db.create_dict_event_id_links()

# driven_links_dict = db.create_driven_links_dict(vehicleslist)
# picklefile_write('driven_links_dict.pickle', driven_links_dict)
driven_links_dict = picklefile_read('driven_links_dict.pickle')

error = {}
sumtrips = 0
sumerror = 0
for id in vehicleslist:
    counter = 0
    for trip in driven_links_dict.d[id]:
        if trip.corrected == False and trip.actual_speed == -1:
            counter += 1
            # print(id, trip)
    error[id] = [len(driven_links_dict.d[id]), counter]
    sumtrips += len(driven_links_dict.d[id])
    sumerror += counter

print(sumtrips, sumerror)

# enteredlinks = db.get_vehicle_entered_links(vehicles)
# leftlinks = db.get_vehicle_left_links(vehicles)

# with open('enteredlinks.pickle', 'wb') as fp:
#     pickle.dump(enteredlinks, fp)
# with open('leftlinks.pickle', 'wb') as fp:
#     pickle.dump(leftlinks, fp)

# enteredlinks_pickle = 'enteredlinks.pickle'
# if os.path.exists(enteredlinks_pickle):
#     enteredlinks= picklefile_read(enteredlinks_pickle)
# else:
#     enteredlinks = db.get_vehicle_entered_links(vehicleslist)
#     picklefile_write(enteredlinks_pickle, enteredlinks)

# leftlinks_pickle = 'leftlinks.pickle'
# if os.path.exists(leftlinks_pickle):
#     leftlinks = picklefile_read(leftlinks_pickle)
# else:
#     leftlinks = db.get_vehicle_left_links(vehicleslist)
#     picklefile_write(leftlinks_pickle, leftlinks)

# vehicledict = create_vehicle_dict(vehicleslist, enteredlinks)
# drt = create_fleet_information(vehicledict, vehicleslist)

# db.get_links_with_id()
# db.get_speed_for_link(vehicleslist)

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')

# def get_link_from_id(trips,id):
#     for trip in trips:
#         if trip.event_id == id:
#             print(trip)


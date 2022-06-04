from timeit import default_timer as timer
from config import dbpath
from db import *

debugging = False

q_start=timer()

db = Db(dbpath)

vehicleslist = db.get_drtvehicles()

link_information_dict = db.create_dict_link_info()

# link_event_id_dict = db.create_dict_event_id_links()
# picklefile_write('link_event_id_dict.pickle', link_event_id_dict)

# driven_links_dict = db.create_driven_links_dict(vehicleslist)
# picklefile_write('driven_links_dict.pickle', driven_links_dict)

if debugging == True:
    link_event_id_dict = picklefile_read('link_event_id_dict.pickle')
    driven_links_dict = picklefile_read('driven_links_dict.pickle')
    links_dict = picklefile_read('links_dict.pickle')
    vehicledict = picklefile_read('vehicledict.pickle')
else:
    link_event_id_dict = db.create_dict_event_id_links()
    picklefile_write('link_event_id_dict.pickle', link_event_id_dict)
    driven_links_dict = db.create_driven_links_dict(vehicleslist)
    picklefile_write('driven_links_dict.pickle', driven_links_dict)
    dictofPassengerOccupancy = db.calculate_passenger_occupancy(vehicleslist)
    links_dict = db.calculate_passengers_for_link(vehicleslist, dictofPassengerOccupancy, driven_links_dict)
    picklefile_write('links_dict.pickle', links_dict)
    vehicledict = create_vehicle_dict(vehicleslist, driven_links_dict)
    vehicledict = db.assign_capacity(vehicleslist, vehicledict)
    picklefile_write('vehicledict.pickle', vehicledict)


analyse_speed_pct_threshold(vehicleslist, driven_links_dict)

# dictofPassengerOccupancy = db.calculate_passenger_occupancy(vehicleslist)
# links_dict = db.calculate_passengers_for_link(vehicleslist, dictofPassengerOccupancy, driven_links_dict)
# picklefile_write('links_dict.pickle', links_dict)
# vehicledict = create_vehicle_dict(vehicleslist, driven_links_dict)
# vehicledict = db.assign_capacity(vehicleslist, vehicledict)
# picklefile_write('vehicledict.pickle', vehicledict)
drt = create_fleet_information(vehicledict, vehicleslist)

print(len(drt.vehicles))
print(drt.avg_distance_per_vehicle)
print(drt.maximumdistance)

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')


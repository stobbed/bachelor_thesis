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
calculate_potential_error_rate(vehicleslist, driven_links_dict)

vehicledict = create_vehicle_dict(vehicleslist, driven_links_dict)
drt = create_fleet_information(vehicledict, vehicleslist)
dictofPassengerOccupancy = db.calculate_passenger_occupancy(vehicleslist)
db.calculate_passengers_for_link(vehicleslist, dictofPassengerOccupancy, driven_links_dict)

# db.get_links_with_id()
# db.get_speed_for_link(vehicleslist)

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')

# def get_link_from_id(trips,id):
#     for trip in trips:
#         if trip.event_id == id:
#             print(trip)


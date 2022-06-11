from timeit import default_timer as timer

from py import process
from configuration import *
from db import *
import multiprocessing

q_start=timer()

def xmltofleetinformation(path):
    db = Db(path)

    vehicleslist = db.get_drtvehicles()
    db.create_dict_link_info()

    # for i in range(1,1000,100):
    #     data = query_db(i,100)
    #     d = db.create_driven_links_dict(data)

    # multiprocessing
    pool = multiprocessing.Pool()
    processes = [pool.apply_async(db.calculate_vehicle_information, args = (vehicle,)) for vehicle in vehicleslist]
    result = [p.get() for p in processes]

    # for vehicle in vehicleslist:
    #     db.calculate_vehicle_information(vehicle)

    # link_event_id_dict = db.create_dict_event_id_links()
    # driven_links_dict = db.create_driven_links_dict(vehicleslist)
    # dictofPassengerOccupancy = db.calculate_passenger_occupancy(vehicleslist)
    # links_dict = db.calculate_passengers_for_link(vehicleslist, dictofPassengerOccupancy, driven_links_dict)
    # vehicledict = create_vehicle_dict(vehicleslist, driven_links_dict)
    # vehicledict = db.assign_capacity(vehicleslist, vehicledict)
    
    # print('creating vehicledict.pickle...')
    # picklefile_write('vehicledict.pickle', vehicledict)
    # print('...created vehicledict.pickle')


    # analyse_speed_pct_threshold(vehicleslist, driven_links_dict)
    # fleet = create_fleet_information(vehicledict, vehicleslist)
    # print('creating fleet.pickle...')
    # picklefile_write('fleet.pickle', fleet)
    # print('...created fleet.pickle')
    # return fleet

drt = xmltofleetinformation(path_drt)

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')


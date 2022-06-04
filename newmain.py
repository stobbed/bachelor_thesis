from timeit import default_timer as timer
from config import *
from db import *


q_start=timer()

def xmltofleetinformation(path):
    db = Db(path)

    vehicleslist = db.get_drtvehicles()
    link_information_dict = db.create_dict_link_info()

    if debugging == True:
        link_event_id_dict = picklefile_read('link_event_id_dict.pickle')
        driven_links_dict = picklefile_read('driven_links_dict.pickle')
        links_dict = picklefile_read('links_dict.pickle')
        vehicledict = picklefile_read('vehicledict.pickle')
    else:
        link_event_id_dict = db.create_dict_event_id_links()
        driven_links_dict = db.create_driven_links_dict(vehicleslist)
        dictofPassengerOccupancy = db.calculate_passenger_occupancy(vehicleslist)
        links_dict = db.calculate_passengers_for_link(vehicleslist, dictofPassengerOccupancy, driven_links_dict)
        vehicledict = create_vehicle_dict(vehicleslist, driven_links_dict)
        vehicledict = db.assign_capacity(vehicleslist, vehicledict)
        print('creating vehicledict.pickle...')
        picklefile_write('vehicledict.pickle', vehicledict)
        print('...created vehicledict.pickle')

        if picklecreation == True:
            print('creating link_event_id_dict.pickle...')
            picklefile_write('link_event_id_dict.pickle', link_event_id_dict)
            print('...created link_event_id_dict.pickle')
            print('creating driven_links_dict.pickle...')
            picklefile_write('driven_links_dict.pickle', driven_links_dict)
            print('...created driven_links_dict.pickle')
            print('creating links_dict.pickle...')
            picklefile_write('links_dict.pickle', links_dict)
            print('...created links_dict.pickle')
            print('creating vehicledict.pickle...')
            picklefile_write('vehicledict.pickle', vehicledict)
            print('...created vehicledict.pickle')


    analyse_speed_pct_threshold(vehicleslist, driven_links_dict)
    fleet = create_fleet_information(vehicledict, vehicleslist)
    print('creating fleet.pickle...')
    picklefile_write('fleet.pickle', fleet)
    print('...created fleet.pickle')
    return fleet

drt = xmltofleetinformation(path_drt)

q_end=timer()
q_duration=q_end-q_start
print('\n Total elapsed time: ', q_duration,'\n')


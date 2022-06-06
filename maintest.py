from py import process
from config import *
from db import *
import multiprocessing
import time

def vehicleinfo_batch(vehicle, link_information_dict, simulationname):
    db = Db(path_drt)
    db.calculate_vehicle_information(vehicle, link_information_dict, simulationname)
    print('finished with vehicle: ', str(vehicle))

if __name__ == "__main__":
    tic = time.perf_counter()
    db = Db(path_drt)
    simulationname = getsimulationname(path_drt)

    vehicleslist = db.get_drtvehicles()
    link_information_dict = db.create_dict_link_info()

    # for i in range(1,1000,100):
    #     data = query_db(i,100)
    #     d = db.create_driven_links_dict(data)

    # multiprocessing
    pool = multiprocessing.Pool()
    processes = [pool.apply_async(vehicleinfo_batch, args = (vehicle, link_information_dict, simulationname)) for vehicle in vehicleslist]
    result = [p.get() for p in processes]

    toc = time.perf_counter()
    print(f'took you: {toc-tic:0.2f} seconds')


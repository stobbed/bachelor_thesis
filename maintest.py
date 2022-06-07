from config import *
from db import *
import multiprocessing
import time

def vehicleinfo_batch(vehicle, link_information_dict, simulationname, path, listofagents):
    db = Db(path)
    db.calculate_vehicle_information(vehicle, link_information_dict, simulationname, path, listofagents)
    print('finished with vehicle: ', str(vehicle))

def batching(path):
    db = Db(path)
    link_information_dict = db.create_dict_link_info()
    simulationname = getsimulationname(path)
    vehicleslist = db.get_drtvehicles()
    listofagents = create_personlist(path, simulationname)
    # multiprocessing
    pool = multiprocessing.Pool()
    processes = [pool.apply_async(vehicleinfo_batch, args = (vehicle, link_information_dict, simulationname, path, listofagents)) for vehicle in vehicleslist]
    result = [p.get() for p in processes]

if __name__ == "__main__":
    tic = time.perf_counter()

    path = path_drt
    batching(path)
    # multiprocessing
    # pool = multiprocessing.Pool()
    # processes = [pool.apply_async(vehicleinfo_batch, args = (vehicle, link_information_dict, simulationname)) for vehicle in vehicleslist]
    # result = [p.get() for p in processes]

    toc = time.perf_counter()
    print(f'took you: {toc-tic:0.2f} seconds')
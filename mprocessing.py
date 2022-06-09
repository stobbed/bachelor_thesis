import multiprocessing
from tqdm import tqdm

from processing import *
from db import *

def vehicleinfo_batch(vehicle, link_information_dict, path, listofagents):
    db = Db(path)
    db.calculate_vehicle_information(vehicle, link_information_dict, path, listofagents)

# pbar = tqdm(total=len(vehicleslist))
def update(*a):
    pbar.update()

def batching(path):
    db = Db(path)
    link_information_dict = db.create_dict_link_info()
    simulationname = getsimulationname(path)
    vehicleslist = db.get_drtvehicles()
    db.disconnect()
    listofagents = create_personlist(path, simulationname)
    
    #progress bar
    global pbar 
    pbar = tqdm(total=len(vehicleslist))

    # multiprocessing
    pool = multiprocessing.Pool()
    processes = [pool.apply_async(vehicleinfo_batch, args = (vehicle, link_information_dict, path, listofagents), callback = update) for vehicle in vehicleslist]
    result = [p.get() for p in processes]
    pool.close()
    pool.join()
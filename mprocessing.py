import multiprocessing
from tqdm import tqdm

from processing import *
from db import *

def vehicleinfo_batch(vehicle, link_information_dict, path, listofagents, drt = True):
    db = Db(path)
    db.calculate_vehicle_information(vehicle, link_information_dict, path, listofagents, drt)

# pbar = tqdm(total=len(vehicleslist))
def update(*a):
    pbar.update()

def batching_drt(path):
    simulationname = getsimulationname(path)
    if not os.path.exists(os.path.join(path, 'results', simulationname + '_vehicleinfo_finished.csv')):
        db = Db(path)
        link_information_dict = db.create_dict_link_info()
        vehicleslist = db.get_drtvehicles()
        db.disconnect()
        listofagents = create_personlist(path, simulationname)
        create_results_dir(path)

        #progress bar
        global pbar
        # if pbar:
        #     pbar.reset()
        pbar = tqdm(total=len(vehicleslist))

        # multiprocessing
        pool = multiprocessing.Pool()
        processes = [pool.apply_async(vehicleinfo_batch, args = (vehicle, link_information_dict, path, listofagents), callback = update) for vehicle in vehicleslist]
        result = [p.get() for p in processes]
        pool.close()
        pool.join()
        pbar.update()
        os.rename(os.path.join(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv')), os.path.join(path, 'results', simulationname + '_vehicleinfo_finished.csv'))
    else:
        print("vehicle info csv already exists!")

def batching_nondrt(path):
    simulationname = getsimulationname(path)
    if os.path.exists(os.path.exists(os.path.join(path, 'results', getsimulationname(path) + '_vehicleinfo.csv'))):
        # os.remove(os.path.join(path, 'results', getsimulationname(path) + '_vehicleinfo.csv'))
        pass
    if not os.path.exists(os.path.join(path, 'results', getsimulationname(path) + '_vehicleinfo_finished.csv')):
        drt = False
        db = Db(path)
        link_information_dict = db.create_dict_link_info()
        db.disconnect()
        listofagents = create_personlist(path, simulationname)
        create_results_dir(path)

        #progress bar
        global pbar
        pbar.reset()
        pbar = tqdm(total=len(listofagents))

        # multiprocessing
        pool = multiprocessing.Pool()
        processes = [pool.apply_async(vehicleinfo_batch, args = (vehicle, link_information_dict, path, listofagents, drt), callback = update) for vehicle in listofagents]
        result = [p.get() for p in processes]
        pool.close()
        pool.join()
        pbar.update()
        os.rename(os.path.join(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv')), os.path.join(path, 'results', simulationname + '_vehicleinfo_finished.csv'))
    else:
        print("vehicle info csv already exists!")
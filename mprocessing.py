import multiprocessing
from tqdm import tqdm

from processing import *
from db import *

def vehicleinfo_batch(vehicle: str, link_information_dict: dict, path: str, listofagents: list, drt = True):
    """ establishes connection to database since a sqlite connection object can not be put into multiprocessing, and then calls up the function that calculates all necessary
        information for further calculations and stores it in the vehicleinfo.csv """
    db = Db()
    db.calculate_vehicle_information(vehicle, link_information_dict, path, listofagents, drt)

def update(*a):
    """ updates the progress from the progess bar in the terminal """
    pbar.update()

def batching_drt(path: str):
    """ function that gets called once per scenario (for any scenario containing DRT vehicles), which does all the necessary calculations and ends in file called vehicleinfo_finished.csv
        containing all the necessary information for the lifecycle assessment and comparison
        
        uses multiprocessing and lots of memory, so be careful or change the parameter in db.py in line 28 to a lower amount """
    simulationname = getsimulationname(path)

    # checks if a finished vehicleinfo file already exists
    if not os.path.exists(os.path.join(path, 'results', simulationname + '_vehicleinfo_finished.csv')):
        finished_drt = False

        # if DB file doesnt already exists creates one or clones the existing database into memory for faster processings
        Db.setup(path)
        db = Db()

        link_information_dict = db.create_dict_link_info()
        vehicleslist = db.get_drtvehicles()
        print("amount of used DRT vehicles:", len(vehicleslist))
        listofagents = create_personlist(path, simulationname)
        create_results_dir(path)

        # starts a loop that keeps restarting until the program is finished with all vehicles, since sometimes timeouts may occur
        while finished_drt == False:
            # checks if the program was previously started and reads in alread processed vehicles so no duplicates are created
            if os.path.exists(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv')):
                print("vehiceinfo already exists from previous calculation, checking for potential duplicates")
                vehiclesinlist = []
                data = pd.read_csv(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv'), low_memory=False, header=0, skip_blank_lines=True)
                for line in data._values:
                    if str(line[0]).startswith("drt") or str(line[0]).startswith("taxi"):
                        vehiclesinlist.append(line[0])

                set1 = set(vehicleslist)
                set2 = set(vehiclesinlist)

                del vehicleslist
                vehicleslist = set1.symmetric_difference(set2)

            # for DRT vehicles

            #progress bar
            global pbar
            pbar = tqdm(total=len(vehicleslist))

            # multiprocessing
            pool = multiprocessing.Pool()
            processes = [pool.apply_async(vehicleinfo_batch, args = (vehicle, link_information_dict, path, listofagents), callback = update) for vehicle in vehicleslist]
            try:
                result = [p.get(timeout=1800) for p in processes]
                pool.close()
                pool.join()
                finished_drt = True
            except multiprocessing.context.TimeoutError:
                print("timeout occured.. process took to long, aborted at", pbar.n, "from", pbar.total)
                pool.close()
                pool.terminate()

        pbar.update()
        print("created info for all drt trips!")
        del vehicleslist

        # for any other trips from Berlin people
        drt = False
        finished_reference = False
        vehicles = db.create_vehicle_list()
        db.disconnect()
        vehicleslist = match_passengers_and_cars(listofagents, vehicles)

        # starts a loop that keeps restarting until the program is finished with all vehicles, since sometimes timeouts may occur
        while finished_reference == False:
            if os.path.exists(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv')):
                print("vehiceinfo already exists from previous calculation, checking for potential duplicates")
                vehiclesinlist = []
                data = pd.read_csv(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv'), low_memory=False, header=0, skip_blank_lines=True)
                for line in data._values:
                    if not str(line[0]).startswith("drt") and not str(line[0]).startswith("taxi"):
                        vehiclesinlist.append(line[0])

                set1 = set(vehicleslist)
                set2 = set(vehiclesinlist)

                del vehicleslist
                vehicleslist = set1.symmetric_difference(set2)

            # progress bar in terminal
            try:
                pbar.reset()
            except:
                pass
            pbar = tqdm(total=len(vehicleslist))

            # multiprocessing
            pool = multiprocessing.Pool()
            processes = [pool.apply_async(vehicleinfo_batch, args = (vehicle, link_information_dict, path, listofagents, drt), callback = update) for vehicle in vehicleslist]
            try:
                result = [p.get(timeout=1200) for p in processes]
                pool.close()
                pool.join()
                finished_reference = True
            except multiprocessing.context.TimeoutError:
                print("timeout occured.. process took to long, aborted at", pbar.n, "from", pbar.total)
                pool.close()
                pool.terminate()

        pbar.update()
        print("created info for all non drt trips in drt scenario!")

        # once all calculations are done for this scneario the file gets renamed vehicleinfo_finished.csv
        os.rename(os.path.join(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv')), os.path.join(path, 'results', simulationname + '_vehicleinfo_finished.csv'))
    else:
        print("vehicle info csv already exists!")

def batching_nondrt(path: str):
    """ function that gets called once per scenario (for reference scenarios without DRT), which does all the necessary calculations and ends in file called vehicleinfo_finished.csv
        containing all the necessary information for the lifecycle assessment and comparison
        
        uses multiprocessing and lots of memory, so be careful or change the parameter in db.py in line 28 to a lower amount """
    simulationname = getsimulationname(path)

    # checks if a finished vehicleinfo file already exists
    if not os.path.exists(os.path.join(path, 'results', getsimulationname(path) + '_vehicleinfo_finished.csv')):
        drt = False
        finished_reference = False
        Db.setup(path)
        db = Db()
        link_information_dict = db.create_dict_link_info()
        listofagents = create_personlist(path, simulationname)
        vehicles = db.create_vehicle_list()
        vehicleslist = match_passengers_and_cars(listofagents, vehicles)
        db.disconnect()
        create_results_dir(path)

        #progress bar
        global pbar

        # starts a loop that keeps restarting until the program is finished with all vehicles, since sometimes timeouts may occur
        while finished_reference == False:
            if os.path.exists(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv')):
                print("vehiceinfo already exists from previous calculation, checking for potential duplicates")
                vehiclesinlist = []
                data = pd.read_csv(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv'), low_memory=False, header=0, skip_blank_lines=True)
                for line in data._values:
                    if not str(line[0]).startswith("drt") and not str(line[0]).startswith("taxi"):
                        vehiclesinlist.append(line[0])

                set1 = set(vehicleslist)
                set2 = set(vehiclesinlist)

                del vehicleslist
                vehicleslist = set1.symmetric_difference(set2)

            # progress bar in terminal
            try:
                pbar.reset()
            except:
                pass
            pbar = tqdm(total=len(vehicleslist))

            # multiprocessing
            pool = multiprocessing.Pool()
            processes = [pool.apply_async(vehicleinfo_batch, args = (vehicle, link_information_dict, path, listofagents, drt), callback = update) for vehicle in vehicleslist]
            try:
                result = [p.get(timeout=1200) for p in processes]
                pool.close()
                pool.join()
                finished_reference = True
            except multiprocessing.context.TimeoutError:
                print("timeout occured.. process took to long, aborted at", pbar.n, "from", pbar.total)
                pool.close()
                pool.terminate()

        # once all calculations are done for this scneario the file gets renamed vehicleinfo_finished.csv
        os.rename(os.path.join(os.path.join(path, 'results', simulationname + '_vehicleinfo.csv')), os.path.join(path, 'results', simulationname + '_vehicleinfo_finished.csv'))
    else:
        print("vehicle info csv already exists!")
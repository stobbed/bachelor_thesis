from configuration import *
from db import *
from configurationgui import *
from lca import *
import mprocessing
from postprocessing import *

import time

if __name__ == "__main__":
    # ppening GUI to configure paths
    gui = configgui()

    if gui.success == False:
        print("\naborted program, due to failure or closing the window, you need to press the button 'Start Script'!\n")
        quit()

    tic = time.perf_counter()

    # getting the (adjusted) paths from the config.ini
    path_drt = getfromconfig('paths','path_drt')
    path_reference = getfromconfig('paths','path_reference')

    # analyse MATSIM outputs and store results in vehicleinfo.csv
    mprocessing.batching_drt(path_drt)
    print("finished analyzing drt scenario!")
    mprocessing.batching_nondrt(path_reference)
    print("finished analyzing reference scenario!")

    drt_info = calculate_avg_vehicle(path_drt)
    reference_info = calculate_avg_vehicle(path_reference)

    # db = Db()
    # cursor = db.localcursor(path_drt)
    drt_vehicles_drt, drt_vehicles_nondrt = scale_scenario(drt_info)
    vehicles_drt, vehicles_nondrt = scale_scenario(reference_info)
    # db.disconnect()
    # db.localdisconnect()

    openlca = olcaclient()
    openlca.lifecycleassessment(drt_vehicles_drt, drt_vehicles_nondrt, getsimulationname(path_drt))
    print("lifecycleassessment for drt scenario done!")
    openlca.lifecycleassessment(vehicles_drt, vehicles_nondrt, getsimulationname(path_reference))
    print("lifecycleassessment for reference scenario done")

    compare_scnearios(path_drt, path_reference)

    # print(drt_info)
    # print(" ")
    # print(reference_info)

    toc = time.perf_counter()
    print(f'took you: {toc-tic:0.1f} seconds')
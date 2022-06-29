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

    # forceable closes the programm if the GUI windows was closed
    if gui.success == False:
        print("\naborted program, due to failure or closing the window, you need to press the button 'Start Script'!\n")
        quit()

    # starts a timer
    tic = time.perf_counter()

    # getting the (adjusted) paths from the config.ini
    path_drt = getfromconfig('paths','path_drt')
    path_reference = getfromconfig('paths','path_reference')

    # analyse MATSIM outputs and store results in vehicleinfo.csv
    mprocessing.batching_drt(path_drt)
    print("finished analyzing drt scenario!")
    mprocessing.batching_nondrt(path_reference)
    print("finished analyzing reference scenario!")

    # calculating avg vehicles from vehicleinfo.csv files
    drt_info = calculate_avg_vehicle(path_drt)
    reference_info = calculate_avg_vehicle(path_reference)

    # scaling the scenario since MATSIM only calculates a pct share of the traffic due to calculation times.. considers scaling effects for DRT
    drt_vehicles_drt, drt_vehicles_nondrt = scale_scenario(drt_info)
    vehicles_drt, vehicles_nondrt = scale_scenario(reference_info)

    # starts lifecycleassessment and in results creates one excel for each scenario containing the GHG emissions as well as the necessary vehicle and fleet information
    openlca = olcaclient()
    openlca.lifecycleassessment(drt_vehicles_drt, drt_vehicles_nondrt, getsimulationname(path_drt))
    print("lifecycleassessment for drt scenario done!")
    openlca.lifecycleassessment(vehicles_drt, vehicles_nondrt, getsimulationname(path_reference))
    print("lifecycleassessment for reference scenario done")

    # comparing both scenarios and creating graphics
    compare_scnearios(path_drt, path_reference)

    # stopping timer
    toc = time.perf_counter()
    print(f'took you: {toc-tic:0.1f} seconds')
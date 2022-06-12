from configuration import *
from db import *
from configurationgui import *
from lca import *
import mprocessing

import time


if __name__ == "__main__":
    # ppening GUI to configure paths
    gui = configgui()

    tic = time.perf_counter()

    # getting the (adjusted) paths from the config.ini
    path_drt = getfromconfig('paths','path_drt')
    path_reference = getfromconfig('paths','path_reference')

    # analyse MATSIM outputs and store results in vehicleinfo.csv
    mprocessing.batching_drt(path_drt)
    print("finished analyzing drt scenario!")
    mprocessing.batching_nondrt(path_reference)
    print("finished analyzing reference scenario!")

    # drt_info = calculate_avg_vehicle(path_drt)
    # reference_info = calculate_avg_vehicle(path_reference)

    openlca = olcaclient(path_drt)
    openlca.lifecycleassessment_electric()

    # openlca = olcaclient(path_reference)

    # print(drt_info)
    # print(" ")
    # print(reference_info)

    toc = time.perf_counter()
    print(f'took you: {toc-tic:0.1f} seconds')
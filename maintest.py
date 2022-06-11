from configuration import *
from db import *
from configurationgui import *
import mprocessing

import time


if __name__ == "__main__":
    gui = configui()

    tic = time.perf_counter()

    path_drt = getfromconfig('paths','path_drt')
    path_reference = getfromconfig('paths','path_reference')

    mprocessing.batching_drt(path_drt)
    print("finished analyzing drt scenario!")
    mprocessing.batching_nondrt(path_reference)
    print("finished analyzing reference scenario!")

    drt_info = calculate_avg_vehicle(path_drt)
    reference_info = calculate_avg_vehicle(path_reference)

    print(drt_info)
    print(" ")
    print(reference_info)

    toc = time.perf_counter()
    print(f'took you: {toc-tic:0.1f} seconds')
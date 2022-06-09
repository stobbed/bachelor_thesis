from config import *
from db import *

import mprocessing
import multiprocessing
from tqdm import tqdm
import time

if __name__ == "__main__":
    tic = time.perf_counter()

    mprocessing.batching(path_drt)
    print("finished analyzing drt scenario!")
    mprocessing.batching(path_reference)
    print("finished analyzing reference scenario!")

    toc = time.perf_counter()
    print(f'took you: {toc-tic:0.1f} seconds')
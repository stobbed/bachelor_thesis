from db import *
from postprocessing import *

drt_vehicles_drt = (picklefile_read("drt_vehicles_drt.pickle"))
drt_vehicles_nondrt = picklefile_read("drt_vehicles_nondrt.pickle")


path_drt = "/Users/dstobbe/Downloads/MATSIM Output/berlin-drt-v5.5-1pct"

db_drt = Db(path_drt)
cursor = db_drt.fetchcursor()

vehicleslist = create_vehicleids_list(cursor)
print(len(vehicleslist))

listofagents = create_personlist(path_drt, getsimulationname(path_drt))
print(len(listofagents))

usedvehicles = list(match_passengers_and_cars(listofagents, vehicleslist))

print(len(usedvehicles))

# drt_info = calculate_avg_vehicle(path_drt)
# drt_vehicles_drt, drt_vehicles_nondrt = scale_scenario(drt_info, cursor)

# print(drt_vehicles_drt, drt_vehicles_nondrt)
from db import *
from postprocessing import *
from lca import *
from configurationgui import *

path = "/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-2seats"

import mprocessing

mprocessing.batching_drt(path)

# gui = configgui()

# if gui.success == True:
#     print("run program")
# else:
#     print("aborted")
#     quit()

# xmlpath_nw, xmlpath_evts, xmlpath_vehicles, dbpath = setpaths(path)
# xmlpath = xmlpath_vehicles

# sqliteconn = sqlite3.connect(dbpath)
# cursor = sqliteconn.cursor()
# if os.path.exists(xmlpath):
#     print('opening xml.gz file...')
#     file = gzip.open(xmlpath, mode='rt', encoding='UTF-8')
#     print('file opened!')
    
#     tree = ET.parse(file)
#     root = tree.getroot()
#     vehicle_record = []
#     query = '''INSERT INTO vehicles
#                 VALUES (?, ?, ?)'''

#     for child in root:
#         vehicle_record.append(child.attrib['id'])
#         vehicle_record.append(child.attrib['start_link'])
#         vehicle_record.append(child.attrib['capacity'])
#         try:
#             cursor.execute(query, vehicle_record)
#         except sqlite3.Error as error:
#             print('Error when inserting node record into vehicles table: ', error)
#         finally:
#             vehicle_record = []
# else:
#     # raise FileNotFoundError('Invalid path (xmlpath): '+xmlpath+' - *.xml.gz file doesn\'t exist.')
#     print("no such file exists...")

# sqliteconn.commit()
# sqliteconn.close()

# drt_vehicles_drt = (picklefile_read("drt_vehicles_drt.pickle"))
# drt_vehicles_nondrt = picklefile_read("drt_vehicles_nondrt.pickle")

# print(drt_vehicles_drt)
# print(drt_vehicles_nondrt)

# openlca = olcaclient()
# openlca.lifecycleassessment(drt_vehicles_drt, drt_vehicles_nondrt, "drt_hundekopf.xlsx")

# for fuel, vehiclesizes in drt_vehicles_nondrt.items():
#     for size, vehiclesize in vehiclesizes.items():
#         print("size:",size)
#         print("vehiclesize",vehiclesize)

# path_drt = "/Users/dstobbe/Downloads/MATSIM Output/berlin-drt-v5.5-1pct"

# db_drt = Db(path_drt)
# cursor = db_drt.fetchcursor()

# vehicleslist = create_vehicleids_list(cursor)
# print(len(vehicleslist))

# listofagents = create_personlist(path_drt, getsimulationname(path_drt))
# print(len(listofagents))

# usedvehicles = list(match_passengers_and_cars(listofagents, vehicleslist))

# print(len(usedvehicles))

# # drt_info = calculate_avg_vehicle(path_drt)
# # drt_vehicles_drt, drt_vehicles_nondrt = scale_scenario(drt_info, cursor)

# # print(drt_vehicles_drt, drt_vehicles_nondrt)
import time
import multiprocessing
import random
from tqdm import tqdm

from processing import *

calculate_avg_vehicle_duplicates("/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-4seats")

def update(*a):
    pbar.update()

def function():
    number = random.randint(0,7)
    print(number)
    for _ in range(0,number):
        # print("tik")
        time.sleep(1)
    print("finished")

if __name__ == '__main__':
    vehicleslist = []
    for x in range(0,20,1):
        vehicleslist.append(x)

    global pbar
    pbar = tqdm(total=len(vehicleslist))

    pool = multiprocessing.Pool(2)
    processes = [pool.apply_async(function, callback = update) for vehicle in vehicleslist]
    try:
        result = [p.get(timeout=5) for p in processes]
        pool.close()
        pool.join()
        print("done")
    except multiprocessing.context.TimeoutError:
        print("timeout at", pbar.n, "from", pbar.total)
        pool.close()
        pool.terminate()

    print("hello")

# from db import *
# from postprocessing import *
# from lca import *
# from configurationgui import *

# vehiclesfull = picklefile_read("vehicle.pickle")

# vehiclesinlist = []
# data = pd.read_csv(os.path.join("/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-2seats/results", "berlin-rebalancing-10000vehicles-2seats_vehicleinfo.csv"), low_memory=False, header=0, skip_blank_lines=True)
# for line in data._values:
#     vehiclesinlist.append(line[0])

# set1 = set(vehiclesfull)
# set2 = set(vehiclesinlist)

# new = set1.symmetric_difference(set2)
# print(list(new))

# # with open("vehicles.csv",'a') as file:
# #     writer_object = csv.writer(file)
# #     for fahrzeug in vehicles:
# #         writer_object.writerow([fahrzeug])
# #     file.close()

# test = {}
# test['h'] = {}
# test['h']['test'] = 1

# print(test.get('h').get('test'))

# drt_excel = os.path.join("lca","drt_hundekopf.xlsx")

# excel = pd.read_excel(os.path.join(drt_excel), sheet_name="LCA_results_total")
# print(excel)
# print(excel._values[0][1])
# totalco2 = pd.read_excel(os.path.join(drt_excel), skiprows=3, nrows=4, sheet_name="LCA_results_total", usecols="B", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]


# # https://stackoverflow.com/questions/67056605/how-to-drop-all-tables-in-sqlite3-using-python

# TABLE_PARAMETER = "{TABLE_PARAMETER}"
# DROP_TABLE_SQL = f"DROP TABLE {TABLE_PARAMETER};"
# GET_TABLES_SQL = "SELECT name FROM sqlite_schema WHERE type='table';"

# def delete_all_tables(con):
#     tables = get_tables(con)
#     delete_tables(con, tables)


# def get_tables(con):
#     cur = con.cursor()
#     cur.execute(GET_TABLES_SQL)
#     tables = cur.fetchall()
#     cur.close()
#     return tables


# def delete_tables(con, tables):
#     cur = con.cursor()
#     for table, in tables:
#         sql = DROP_TABLE_SQL.replace(TABLE_PARAMETER, table)
#         cur.execute(sql)
#     cur.close()

# print('connecting to database...')
# try:
#     # sqliteConnection = sqlite3.connect("dbatabase.db")
#     # sqliteConnection = sqlite3.connect("file:memdb1?mode=memory")
#     sqliteConnection = sqlite3.connect("file:memdb1?mode=memory", isolation_level=None)
# except sqlite3.error as error:
#     sys.exit('Failed to connect to database: ', error, '...Quitting.')
# print('connection established!')

# # delete_all_tables(sqliteConnection)

# # create nodes and links table
# print('creating database cursor...')
# cursor = sqliteConnection.cursor()
# print('cursor created!')

# query2 = ''' SELECT * from network_nodes'''
# test = cursor.execute(query2)
# res = test.fetchall()
# print(res)

# cursor.close()
# sqliteConnection.close()
# path = "/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-2seats"

# import mprocessing

# mprocessing.batching_drt(path)

# # gui = configgui()

# # if gui.success == True:
# #     print("run program")
# # else:
# #     print("aborted")
# #     quit()

# # xmlpath_nw, xmlpath_evts, xmlpath_vehicles, dbpath = setpaths(path)
# # xmlpath = xmlpath_vehicles

# # sqliteconn = sqlite3.connect(dbpath)
# # cursor = sqliteconn.cursor()
# # if os.path.exists(xmlpath):
# #     print('opening xml.gz file...')
# #     file = gzip.open(xmlpath, mode='rt', encoding='UTF-8')
# #     print('file opened!')
    
# #     tree = ET.parse(file)
# #     root = tree.getroot()
# #     vehicle_record = []
# #     query = '''INSERT INTO vehicles
# #                 VALUES (?, ?, ?)'''

# #     for child in root:
# #         vehicle_record.append(child.attrib['id'])
# #         vehicle_record.append(child.attrib['start_link'])
# #         vehicle_record.append(child.attrib['capacity'])
# #         try:
# #             cursor.execute(query, vehicle_record)
# #         except sqlite3.Error as error:
# #             print('Error when inserting node record into vehicles table: ', error)
# #         finally:
# #             vehicle_record = []
# # else:
# #     # raise FileNotFoundError('Invalid path (xmlpath): '+xmlpath+' - *.xml.gz file doesn\'t exist.')
# #     print("no such file exists...")

# # sqliteconn.commit()
# # sqliteconn.close()

# # drt_vehicles_drt = (picklefile_read("drt_vehicles_drt.pickle"))
# # drt_vehicles_nondrt = picklefile_read("drt_vehicles_nondrt.pickle")

# # print(drt_vehicles_drt)
# # print(drt_vehicles_nondrt)

# # openlca = olcaclient()
# # openlca.lifecycleassessment(drt_vehicles_drt, drt_vehicles_nondrt, "drt_hundekopf.xlsx")

# # for fuel, vehiclesizes in drt_vehicles_nondrt.items():
# #     for size, vehiclesize in vehiclesizes.items():
# #         print("size:",size)
# #         print("vehiclesize",vehiclesize)

# # path_drt = "/Users/dstobbe/Downloads/MATSIM Output/berlin-drt-v5.5-1pct"

# # db_drt = Db(path_drt)
# # cursor = db_drt.fetchcursor()

# # vehicleslist = create_vehicleids_list(cursor)
# # print(len(vehicleslist))

# # listofagents = create_personlist(path_drt, getsimulationname(path_drt))
# # print(len(listofagents))

# # usedvehicles = list(match_passengers_and_cars(listofagents, vehicleslist))

# # print(len(usedvehicles))

# # # drt_info = calculate_avg_vehicle(path_drt)
# # # drt_vehicles_drt, drt_vehicles_nondrt = scale_scenario(drt_info, cursor)

# # # print(drt_vehicles_drt, drt_vehicles_nondrt)
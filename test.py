from calendar import c
import pytest
import pickle
import os.path
from configuration import *
import gzip
import xml.etree.cElementTree as ET
import csv
import pandas as pd

import configparser
from processing import *
from postprocessing import *
from db import *
# from postprocessing import *

test = {}
test['consumption'] = 6
test['small'] = {}
test['small']['km'] = 15
test['small']['amount'] = 2

for key, value in test.items():
    print("key:", key)
    print("value:",value)

path = "/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats/hundekopf-rebalancing-1000vehicles-2seats_vehicleinfo_finished.csv"

drt_info = calculate_avg_vehicle(path)
db_drt = Db(path_drt)
cursor = db_drt.fetchcursor()

drt_vehicles_drt, drt_vehicles_nondrt = scale_scenario(drt_info, cursor)


vehicle = "taxi12"

if not (str(vehicle).startswith("drt") or str(vehicle).startswith("taxi")):
    print("yes")

# vehicles = create_vehicle_list("/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats")

xmlpath = "/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats/hundekopf-rebalancing-1000vehicles-2seats.output_allVehicles.xml.gz"
if os.path.exists(xmlpath):
    print('opening xml.gz file...')
    file = gzip.open(xmlpath, mode='rt', encoding='UTF-8')
    print('file opened!')
else:
    raise FileNotFoundError('Invalid path (xmlpath): '+xmlpath+' - *.xml.gz file doesn\'t exist.')

tree = ET.parse(file)
root = tree.getroot()

vehicles = []
for child in root:
    if len(child.attrib) > 1:
        if child.attrib['type'] == "car":
            vehicles.append(child.attrib['id'])

print(len(vehicles))

# xmlpath = "/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats/hundekopf-rebalancing-1000vehicles-2seats.output_allVehicles.xml.gz"
# if os.path.exists(xmlpath):
#     print('opening xml.gz file...')
#     file = gzip.open(xmlpath, mode='rt', encoding='UTF-8')
#     print('file opened!')
# else:
#     raise FileNotFoundError('Invalid path (xmlpath): '+xmlpath+' - *.xml.gz file doesn\'t exist.')

# # single nodes can be deleted from RAM after parsing using iterparse() function and an iterator
# # set up iterator for event xml
# print('setting up parser...')
# parser = ET.iterparse(file, events=('start', 'end'), parser=ET.XMLParser(encoding='UTF-8'))
# # parser = iter(parser)
# event, root = parser.__next__()
# print('parser set!')

# vehicles = []
# for child in root:
#     if len(child.attrib) > 1:
#         if child.attrib['type'] == "car":
#             vehicles.append(child.attrib['id'])

# print(len(vehicles))


test = {}
test['small'] = 20
test['medium'] = 100

for item in test:
    print(item)

path_drt = getfromconfig('paths','path_drt')
drt_info = calculate_avg_vehicle(path_drt)
scale_scenario(drt_info, 1)

Parameter = {'electric':2, 'battery':10}
for key, value in Parameter.items():
    print(key)
    print(value)

# config = configparser.ConfigParser()
# config.add_section('paths')
# config.set('paths', 'path_drt', "r'/Users/dstobbe/Downloads/MATSIM Output/berlin-drt-v5.5-1pct'")
# config.set('paths', 'path_refrence', "r'/Users/dstobbe/Downloads/MATSIM Output/berlin-v5.5.3-1pct'")

# config.add_section('vehicle_parameters')
# config.set('vehicle_parameters', 'drt_vehiclesize', str(2))

# with open("config.ini", "w") as file:
#     config.write(file)

# from configurationgui import *
# app = App()
# app.mainloop()

# print(path_drt)

path="/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats"
data = pd.read_csv(os.path.join(path, getsimulationname(path) + '_vehicleinfo.csv'))
totalkm_region = 0 ;totalkm_notregion = 0; totalpkm = 0
intown_pct = 0; countryroad_pct = 0; highway_pct = 0
pkm_intown = 0; pkm_countryroad = 0; pkm_highway = 0
avgpassenger_amount = 0
data = pd.read_csv("/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats/hundekopf-rebalancing-1000vehicles-2seats_vehicleinfo.csv")
vehicleamount = data._values.shape[0]
for line in data._values:
    totalkm_region += line[1]; totalkm_notregion += line[10]; totalpkm += line[8]
    intown_pct += line[2]; countryroad_pct += line[3]; highway_pct += line[4]
    pkm_intown += line[5]; pkm_countryroad += line[6]; pkm_highway += line[7]
    avgpassenger_amount += line[9]
totalkm = totalkm_region + totalkm_notregion
avg_totalkm = totalkm / vehicleamount
avg_totalkm_region = totalkm_region / vehicleamount
avg_totalkm_notregion = totalkm_notregion / vehicleamount
avg_totalpkm = totalpkm / vehicleamount
avg_intown_pct = intown_pct / vehicleamount
avg_countryroad_pct = countryroad_pct / vehicleamount
avg_highway_pct = highway_pct / vehicleamount
avg_pkm_intown = pkm_intown / vehicleamount
avg_pkm_countryroad = pkm_countryroad / vehicleamount
avg_pkm_highway = pkm_highway / vehicleamount
avgpassenger_amount = avgpassenger_amount / vehicleamount

region = 'berlin'
data = pd.read_csv("/Users/dstobbe/Downloads/MATSIM Output/berlin-drt-v5.5-1pct/berlin-drt-v5.5-1pct.output_persons.csv.gz", compression='gzip')
listofagents = []
for line in data._values:
    text = str(line).split(";")
    agent = text[0].replace("['","")
    homeregion = text[-1].replace("']","")
    if homeregion == region:
        listofagents.append(agent)

with open('link_event_id_dict.pickle', 'rb') as fp:
    content = pickle.load(fp)
    print(content)

def test_trip():
    testtrip = Trip('Münzstraße', '123')
    testtrip2 = Trip('Berliner Straße', '234')
    event_id = '123'
    d = {event_id: testtrip }

xmlpath = xmlpath_vehicles
if os.path.exists(xmlpath):
    print('opening xml.gz file...')
    file = gzip.open(xmlpath, mode='rt', encoding='UTF-8')
    print('file opened!')
else:
    raise FileNotFoundError('Invalid path (xmlpath): '+xmlpath+' - *.xml.gz file doesn\'t exist.')

tree = ET.parse(file)
root = tree.getroot()
for child in root:
    # print(child.tag, child.attrib)
    print(child.attrib['id'])

# single nodes can be deleted from RAM after parsing using iterparse() function and an iterator
# set up iterator for event xml
# print('setting up parser...')
# parser = ET.iterparse(file, events=('start', 'end'), parser=ET.XMLParser(encoding='UTF-8'))
# parser = iter(parser)
# event, root = parser.__next__()
# print('parser set!')

# vehicle_record = []
# for event, elem in parser:
#     if (event == 'end' and elem.tag == 'vehicle'):
#         print(elem)
#         vehicle_record.append(elem.attrib['id'])
#         vehicle_record.append(elem.attrib['start_link'])
#         vehicle_record.append(elem.attrib['capacity'])
#         query = '''INSERT INTO vehicles
#                     VALUES (?, ?, ?)'''

#     # try:
#     #     cursor.execute(query, node_record)
#     # except sqlite3.Error as error:
#     #     print('Error when inserting node record into network_nodes table: ', error)

#     # finally:
#     vehicle_record = []
#     elem.clear()
#     root.clear()

with open('leftlinks.pickle', 'rb') as fp:
    test = pickle.load(fp)

print("hello")
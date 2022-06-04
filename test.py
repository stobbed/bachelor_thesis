import pytest
import os.path
from config import *
import gzip
import xml.etree.cElementTree as ET

from db import DataDb

datadb = DataDb('/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats')
columns = ['link', 'enter_time', 'left_time']
datadb.createtable('drt1',columns)
content = [('berliner','12','13'),('frankfurter','10','11'),('münchener','0','4')]
datadb.writemultiplerows('drt1',content)
datadb.commit()

tablename = 'drt2'
column = ['enter_time','left_time']
newvalue = ['0','100']
condition_column = 'link'
condition_value = '012345'
query = '''UPDATE ''' + str(tablename) + ''' SET '''
for index in range(0,len(newvalue)):
    if index == 0:
        query += str(column[index]) + ''' = ''' + str(newvalue[index])
    elif index > 0:
        query += ''', ''' + str(column[index]) + ''' = ''' + str(newvalue[index])
query += ''' WHERE ''' + str(condition_column) + ''' = ''' + str(condition_value)

print(query)

tablename = '''test'''
content = ['bmw', '4', '200km']
query = '''INSERT INTO ''' + str(tablename) + '\n' + '''VALUES ('''
for index in range(0,len(content)):
    if index<len(content)-1:
        query += '''?,'''
    else:
        query += '''?)'''
print(query)

query2 = '''CREATE TABLE network_links (
                link_id TEXT NOT NULL PRIMARY KEY,
                from_node TEXT,
                to_node TEXT,
                length REAL,
                capacity REAL,
                freespeed REAL,
                permlanes INTEGER,
                oneway INTEGER, 
                modes TEXT);'''

tablename = '''network_links'''
query = '''CREATE TABLE ''' + tablename + ''' (\n'''
columns = ['''link_id TEXT NOT NULL PRIMARY KEY''', '''from_node TEXT''', '''to_node TEXT''']

index=0
for item in columns:
    if index<len(columns)-1:
        query += item + ''',\n'''
    elif index==len(columns)-1:
        query += item + ''');'''
    index+=1


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

# tree = ET.parse(file)
# root = tree.getroot()
# for child in root:
#     # print(child.tag, child.attrib)
#     print(child.attrib['id'])

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
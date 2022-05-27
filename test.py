import pytest
import pickle
import os.path
from config import *
import gzip
import xml.etree.cElementTree as ET

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
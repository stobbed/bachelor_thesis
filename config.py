# This is a config file, adjust pathes in the marked area
import os.path
import datetime
import platform
import sys

import tkinter as tk
from tkinter import filedialog

your_os = platform.system()

# -------------------------------------------------------------------------------- #
# adjust path to simulation data and paramters in here

# path_drt = r'/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats'
manualdirectory = False

region = 'berlin'
path_drt = r'/Users/dstobbe/Downloads/MATSIM Output/berlin-drt-v5.5-1pct'
# path_drt = r'G:\MATSIM Output\berlin-drt-v5.5-1pct'
# path_drt = r'G:\MATSIM Output\hundekopf-rebalancing-1000vehicles-2seats'

# xmlpath_nw = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.output_network.xml.gz'
# xmlpath_evts = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.output_events.xml.gz'
# xmlpath_vehicles = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.drt__vehicles.xml.gz'
publictransport_ignore = True
debugging = False
picklecreation = True

# -------------------------------------------------------------------------------- #

def getsimulationname(path):
    your_os = platform.system()
    if your_os == 'Windows':
        text = path.split("\\")
    elif your_os == 'Darwin': # MacOs
        text = path.split("/")
    else:
        print(f'This program does not support {your_os} yet, maybe ask the programmer politely, or adjust this in the config')
        sys.exit('exiting program')
    simulationname = text[-1]
    return simulationname

def setpaths(path):
    # Betriebssystem dektieren und entscheiden wonach gesplitted wird
    simulationname = getsimulationname(path)
    xmlpath_nw = os.path.join(path, simulationname + r'.output_network.xml.gz')
    xmlpath_evts = os.path.join(path, simulationname + r'.output_events.xml.gz')
    xmlpath_vehicles = os.path.join(path, simulationname + r'.drt_vehicles.xml.gz')

    dbpath = ''
    if your_os == 'Windows':
        text = path.split("\\")
    elif your_os == 'Darwin': # MacOs
        text = path.split("/")
    else:
        print(f'This program does not support {your_os} yet, maybe ask the programmer politely, or adjust this in the config')
        sys.exit('exiting program')
    for elements in text:
        dbpath = dbpath + '/' + elements
    m_time = os.path.getmtime(xmlpath_evts)
    simulationdate = str(datetime.datetime.fromtimestamp(m_time).date())
    dbpath = dbpath + '/' + simulationname + '-' + simulationdate + '.db'
    dbpath = dbpath[1:]

    return xmlpath_nw, xmlpath_evts, xmlpath_vehicles, dbpath

def assigndirectorymanually():
    path_drt = r'/Users/dstobbe/Downloads/MATSIM Output/berlin-drt-v5.5-1pct'
    return path_drt

def askfordirectory():
    if manualdirectory == False:
        try:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename()

            if your_os == 'Windows':
                text = file_path.split("\\")
            elif your_os == 'Darwin': # MacOs
                text = file_path.split("/")
            else:
                print(f'This program does not support {your_os} yet, maybe ask the programmer politely, or adjust this in the config')
                sys.exit('exiting program')
            text.pop()
            path = ''
            for elements in text:
                path = path + '/' + elements
            print(path)
        except:
            assigndirectorymanually()
    elif manualdirectory == True:
        assigndirectorymanually()

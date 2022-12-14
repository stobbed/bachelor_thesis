# (CC) Dustin Stobbe, 2022

# configuration file, used to help with the configuration (ini) files and set paths

import os.path
import datetime
import platform
import sys
import configparser

# -------------------------------------------------------------------------------- #

your_os = platform.system()
def getsimulationname(path):
    """ retrieves the simulationname from the given path, by splitting the directory and only retrieving the folder name """
    your_os = platform.system()
    if your_os == 'Windows':
        text = path.split("/")
    elif your_os == 'Darwin': # MacOs
        text = path.split("/")
    else:
        print(f'This program does not support {your_os} yet, maybe ask the programmer politely, or adjust this in the config')
        sys.exit('exiting program')
    simulationname = text[-1]
    return simulationname

def setpaths(path):
    """ creates the necessary paths, needed for the database creation, by adding the simulation name plus xml.gz file names """
    
    simulationname = getsimulationname(path)
    xmlpath_nw = os.path.join(path, simulationname + r'.output_network.xml.gz')
    xmlpath_evts = os.path.join(path, simulationname + r'.output_events.xml.gz')
    xmlpath_vehicles = os.path.join(path, simulationname + r'.drt_vehicles.xml.gz')

    dbpath = ''
    text = path.split("/")
        
    for elements in text:
        dbpath = dbpath + '/' + elements

    # could use the simulation date for purposes of checking if the file is up to date
    m_time = os.path.getmtime(xmlpath_evts)
    simulationdate = str(datetime.datetime.fromtimestamp(m_time).date())

    dbpath = dbpath + '/' + simulationname + '.db'
    dbpath = dbpath[1:]

    return xmlpath_nw, xmlpath_evts, xmlpath_vehicles, dbpath

def getfromconfig(group, object):
    """ retrieves the selected data from config.ini file as string """

    config_obj = configparser.ConfigParser()
    config_obj.read("config.ini")

    config_group = config_obj[group]
    content = config_group[object]

    return content

def getfromvehicleconfig(group, object, standard = False):
    """ retrieves the selected data from vehicle.ini or if standard = True from vehiclestandards.ini configuration files """
    config_obj = configparser.ConfigParser()
    if standard == True:
        config_obj.read("vehiclestandards.ini")
    elif standard == False:
        config_obj.read("vehicle.ini")

    config_group = config_obj[group]
    content = config_group[object]

    return content

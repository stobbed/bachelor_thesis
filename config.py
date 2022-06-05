# This is a config file, adjust pathes in the marked area

import os.path
import datetime

# -------------------------------------------------------------------------------- #
# adjust path to simulation data and paramters in here

# path_drt = r'/Users/dstobbe/Downloads/MATSIM Output/hundekopf-rebalancing-1000vehicles-2seats'
path_drt = r'/Users/dstobbe/Downloads/MATSIM Output/berlin-drt-v5.5-1pct'

# xmlpath_nw = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.output_network.xml.gz'
# xmlpath_evts = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.output_events.xml.gz'
# xmlpath_vehicles = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.drt__vehicles.xml.gz'
publictransport_ignore = True
debugging = False
picklecreation = True

# -------------------------------------------------------------------------------- #

def setpaths(path):
    # Betriebssystem dektieren und entscheiden wonach gesplitted wird
    text = path_drt.split("/")
    simulationname = text[-1]

    xmlpath_nw = os.path.join(path_drt, simulationname + r'.output_network.xml.gz')
    xmlpath_evts = os.path.join(path_drt, simulationname + r'.output_events.xml.gz')
    xmlpath_vehicles = os.path.join(path_drt, simulationname + r'.drt_vehicles.xml.gz')

    # text = xmlpath_nw.split("/")
    # filename = text.pop()
    # filename = filename.split(".output")[0]
    # text.pop(0)

    dbpath = ''
    for elements in text:
        dbpath = dbpath + '/' + elements
    m_time = os.path.getmtime(xmlpath_evts)
    simulationdate = str(datetime.datetime.fromtimestamp(m_time).date())
    dbpath = dbpath + '/' + simulationname + '-' + simulationdate + '.db'
    dbpath = dbpath[1:]

    return xmlpath_nw, xmlpath_evts, xmlpath_vehicles, dbpath
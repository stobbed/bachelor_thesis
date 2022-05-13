# This is a config file, adjust pathes in the marked area

import os.path
import datetime

# -------------------------------------------------------------------------------- #
# adjust the paths in here

xmlpath_nw = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.output_network.xml.gz'
xmlpath_evts = '/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/output-b-drt-mpm-1pct/berlin-drt-v5.5-1pct.output_events.xml.gz'

# -------------------------------------------------------------------------------- #

text = xmlpath_nw.split("/")
filename = text.pop()
filename = filename.split(".output")[0]
text.pop(0)
dbpath = ''
for elements in text:
    dbpath = dbpath + '/' + elements
m_time = os.path.getmtime(xmlpath_evts)
simulationdate = str(datetime.datetime.fromtimestamp(m_time).date())
dbpath = dbpath + '/' + filename + '-' + simulationdate + '.db'
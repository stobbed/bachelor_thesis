# (CC) Dustin Stobbe, 2022

from sympy import rotations
from configuration import *
from database_operations import *
from processing import *

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

path_drt = "/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-2seats"
path_reference = "/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-2seats"

drt_scenario = getsimulationname(path_drt)
reference_scenario = getsimulationname(path_reference)

imagefolder = os.path.join("lca", str(drt_scenario) + "_VS_" + str(reference_scenario))
if not os.path.exists(imagefolder):
    os.mkdir(imagefolder)

charging = getfromconfig('vehicle_parameters', 'charging')

drt_excel = os.path.join("lca",str(drt_scenario), "results_" + drt_scenario + "_" + str(getfromconfig('vehicle_parameters', 'energymix')) + "_" + "normal" + ".xlsx")
reference_excel = os.path.join("lca",str(reference_scenario), "results_" + reference_scenario + "_" + str(getfromconfig('vehicle_parameters', 'energymix')) + "_" + "opportunity" + ".xlsx")

drtsc_lca_drt = pd.read_excel(os.path.join(drt_excel), sheet_name="LCA_results_DRT")
drtsc_lca_nondrt = pd.read_excel(os.path.join(drt_excel), sheet_name="LCA_results_non_DRT")
referencesc_lca_drt = pd.read_excel(os.path.join(reference_excel), sheet_name="LCA_results_DRT")
referencesc_lca_nondrt = pd.read_excel(os.path.join(reference_excel), sheet_name="LCA_results_non_DRT")

drtsc_totalco2_drt = drtsc_lca_drt._values[0][1]
drtsc_production_drt = drtsc_lca_drt._values[2][1]
drtsc_batteries_drt = drtsc_lca_drt._values[3][1]
drtsc_use_drt = drtsc_lca_drt._values[4][1] + drtsc_lca_drt._values[5][1]

drtsc_totalco2_nondrt = drtsc_lca_nondrt._values[0][1]
drtsc_production_nondrt = drtsc_lca_nondrt._values[2][1]
drtsc_batteries_nondrt = drtsc_lca_nondrt._values[3][1]
drtsc_use_nondrt = drtsc_lca_nondrt._values[4][1] + drtsc_lca_nondrt._values[5][1]

referencesc_totalco2_drt = referencesc_lca_drt._values[0][1]
referencesc_production_drt = referencesc_lca_drt._values[2][1]
referencesc_batteries_drt = referencesc_lca_drt._values[3][1]
referencesc_use_drt = referencesc_lca_drt._values[4][1] + referencesc_lca_drt._values[5][1]

referencesc_totalco2_nondrt = referencesc_lca_nondrt._values[0][1]
referencesc_production_nondrt = referencesc_lca_nondrt._values[2][1]
referencesc_batteries_nondrt = referencesc_lca_nondrt._values[3][1]
referencesc_use_nondrt = referencesc_lca_nondrt._values[4][1] + referencesc_lca_nondrt._values[5][1]

customcolor = [[0.69, 0.45, 0.15, 1], [0.54, 0.34, 0.11, 1], [0.34, 0.33, 0.31, 1], [0.35, 0.32, 0.31, 1], [0.13, 0.25, 0.59, 1], [0.24, 0.299, 0.45, 1]]

millionfactor = 1/1000000

names = (drt_scenario + " normal", reference_scenario + "opportunity")
data={"production vehicles DRT":[drtsc_production_drt * millionfactor, referencesc_production_drt * millionfactor], "production vehicles non DRT":[drtsc_production_nondrt * millionfactor, referencesc_production_nondrt * millionfactor], "additional batteries DRT":(drtsc_batteries_drt * millionfactor, referencesc_batteries_drt * millionfactor), "additional batteries non DRT":(drtsc_batteries_nondrt * millionfactor, referencesc_batteries_nondrt * millionfactor), "use phase DRT":(drtsc_use_drt * millionfactor, referencesc_use_drt * millionfactor), "use phase non DRT":(drtsc_use_nondrt * millionfactor, referencesc_use_nondrt * millionfactor)}
#gestacktes Balkendiagramm aus DF
df=pd.DataFrame(data,index=names)
ax2 = df.plot(kind="bar",stacked=True,figsize=(14,8), ylabel="in million tonnes $CO_2$ eq [t]", rot=0, color= customcolor)

# x_offset = -0.03
# y_offset = 0.02
# for p in ax2.patches:
#     b = p.get_bbox()
#     val = "{:.2f}".format(b.y1 + b.y0)        
#     ax2.annotate(val, ((b.x0 + b.x1)/2 + x_offset, b.y1 + y_offset))

plt.title("GHG comparison with " + str(getfromconfig('vehicle_parameters','energymix')) + " and " + "normal vs opportunity")
plt.legend(loc="upper right",bbox_to_anchor=(1, 1.15))
# plt.yticks(np.arange(0, referencesc_totalco2, 1000000000))
plt.yticks([(drtsc_totalco2_drt + drtsc_totalco2_nondrt) * millionfactor, (referencesc_totalco2_drt + referencesc_totalco2_nondrt) * millionfactor])
fig3 = plt.gcf()
fig3.savefig(os.path.join(imagefolder, str(getfromconfig('vehicle_parameters','energymix')) + "_" + "normal_vs_opportunity" + '_totalco2_comparison.png'), dpi=300)
# plt.show()

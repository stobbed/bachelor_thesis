from sympy import rotations
from configuration import *
from database_operations import *
from processing import *

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

path_drt = "/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-2seats"
path_reference = "/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-4seats"
path_3 = "/Users/dstobbe/Downloads/MATSIM Output/berlin-v5.5.3-10pct"

drt_scenario = getsimulationname(path_drt)
reference_scenario = getsimulationname(path_reference)
scenario_3 = getsimulationname(path_3)

names = (drt_scenario, reference_scenario, scenario_3)

imagefolder = os.path.join("lca", str(drt_scenario) + "_VS_" + str(reference_scenario) + "_VS_" + str(scenario_3))
if not os.path.exists(imagefolder):
    os.mkdir(imagefolder)

drt_excel = os.path.join("lca",str(drt_scenario), "results_" + drt_scenario + "_" + str(getfromconfig('vehicle_parameters', 'energymix')) + ".xlsx")
reference_excel = os.path.join("lca",str(reference_scenario), "results_" + reference_scenario + "_" + str(getfromconfig('vehicle_parameters', 'energymix')) + ".xlsx")
scenario3_excel = os.path.join("lca",str(scenario_3), "results_" + scenario_3 + "_" + str(getfromconfig('vehicle_parameters', 'energymix')) + ".xlsx")

drtsc_infos = pd.read_excel(os.path.join(drt_excel), sheet_name="vehicle_infos")
referencesc_infos = pd.read_excel(os.path.join(reference_excel), sheet_name="vehicle_infos")
scenario_3_infos = pd.read_excel(os.path.join(scenario3_excel), sheet_name="vehicle_infos")

drtsc_km = drtsc_infos._values[0][1]
drtsc_pkm = drtsc_infos._values[4][1]

referencesc_km = referencesc_infos._values[0][1]
referencesc_pkm = referencesc_infos._values[4][1]

scenario_3_km = scenario_3_infos._values[0][1]
scenario_3_pkm = scenario_3_infos._values[4][1]

millionfactor = 1/1000000

data={"km":[drtsc_km * millionfactor, referencesc_km * millionfactor, scenario_3_km * millionfactor], "pkm":(drtsc_pkm * millionfactor, referencesc_pkm * millionfactor, scenario_3_pkm * millionfactor)}
#gestacktes Balkendiagramm aus DF
km=pd.DataFrame(data,index=names)
ax4 = km.plot(kind="bar",stacked=False,figsize=(14,8), ylabel="vehicle km and pkm in millions [km]", rot=0)

x_offset = -0.05
y_offset = 0.02
for p in ax4.patches:
    b = p.get_bbox()
    val = "{:.0f}".format(b.y1 + b.y0)        
    ax4.annotate(val, ((b.x0 + b.x1)/2 + x_offset, b.y1 + y_offset))

plt.title("km comparison")
plt.legend(loc="upper right",bbox_to_anchor=(1, 1.15))
plt.yticks(np.arange(0, drtsc_pkm * millionfactor, 10000))
fig2 = plt.gcf()
fig2.savefig(os.path.join(imagefolder, str(getfromconfig('vehicle_parameters','energymix')) + '_km and pkm_comparison.png'), dpi=300)
# plt.show()

drtsc_lcatotal = pd.read_excel(os.path.join(drt_excel), sheet_name="LCA_results_total")
referencesc_lcatotal = pd.read_excel(os.path.join(reference_excel), sheet_name="LCA_results_total")
scenario_3_lcatotal = pd.read_excel(os.path.join(scenario3_excel), sheet_name="LCA_results_total")

drtsc_totalco2 = drtsc_lcatotal._values[0][1]
drtsc_production = drtsc_lcatotal._values[2][1]
drtsc_batteries = drtsc_lcatotal._values[3][1]
drtsc_use = drtsc_lcatotal._values[4][1] + drtsc_lcatotal._values[5][1]

referencesc_totalco2 = referencesc_lcatotal._values[0][1]
referencesc_production = referencesc_lcatotal._values[2][1]
referencesc_batteries = referencesc_lcatotal._values[3][1]
referencesc_use = (referencesc_lcatotal._values[4][1] + referencesc_lcatotal._values[5][1])

scenario_3_totalco2 = scenario_3_lcatotal._values[0][1]
scenario_3_production = scenario_3_lcatotal._values[2][1]
scenario_3_batteries = scenario_3_lcatotal._values[3][1]
scenario_3_use = scenario_3_lcatotal._values[4][1] + scenario_3_lcatotal._values[5][1]

names = (drt_scenario, reference_scenario, scenario_3)
data={"production vehicles":[drtsc_production * millionfactor, referencesc_production * millionfactor, scenario_3_production * millionfactor], "additional batteries":(drtsc_batteries * millionfactor, referencesc_batteries * millionfactor, scenario_3_batteries * millionfactor), "use phase":(drtsc_use * millionfactor, referencesc_use * millionfactor, scenario_3_use * millionfactor)}
#gestacktes Balkendiagramm aus DF
df=pd.DataFrame(data,index=names)
ax2 = df.plot(kind="bar",stacked=True,figsize=(14,8), ylabel="in million tonnes $CO_2$ eq [t]", rot=0)

# x_offset = -0.03
# y_offset = 0.02
# for p in ax2.patches:
#     b = p.get_bbox()
#     val = "{:.2f}".format(b.y1 + b.y0)        
#     ax2.annotate(val, ((b.x0 + b.x1)/2 + x_offset, b.y1 + y_offset))

plt.title("GHG comparison with " + str(getfromconfig('vehicle_parameters','energymix')) + " and " + str(getfromconfig('vehicle_parameters','charging')) + " charging")
plt.legend(loc="upper right",bbox_to_anchor=(1, 1.15))
# plt.yticks(np.arange(0, referencesc_totalco2, 1000000000))
plt.yticks([drtsc_totalco2 * millionfactor, referencesc_totalco2 * millionfactor, scenario_3_totalco2 * millionfactor])
fig3 = plt.gcf()
fig3.savefig(os.path.join(imagefolder, str(getfromconfig('vehicle_parameters','energymix')) + '_totalco2_comparison.png'), dpi=300)
# plt.show()
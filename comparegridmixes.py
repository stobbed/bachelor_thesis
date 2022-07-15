from sympy import rotations
from configuration import *
from database_operations import *
from processing import *

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

path_drt = "/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-4seats"
path_reference = "/Users/dstobbe/Downloads/MATSIM Output/berlin-v5.5.3-10pct"

drt_scenario = getsimulationname(path_drt)
reference_scenario = getsimulationname(path_reference)
charging = "normal"

drt_excel = os.path.join("lca",str(drt_scenario), "results_" + drt_scenario + "_" + "energy_2021_" + charging + ".xlsx")
reference_excel = os.path.join("lca",str(reference_scenario), "results_" + reference_scenario + "_" + "energy_2021_" + charging + ".xlsx")

drtsc_lcatotal = pd.read_excel(os.path.join(drt_excel), sheet_name="LCA_results_total")
referencesc_lcatotal = pd.read_excel(os.path.join(reference_excel), sheet_name="LCA_results_total")

drtsc_infos = pd.read_excel(os.path.join(drt_excel), sheet_name="vehicle_infos")
referencesc_infos = pd.read_excel(os.path.join(reference_excel), sheet_name="vehicle_infos")


drt_excel2 = os.path.join("lca",str(drt_scenario), "results_" + drt_scenario + "_" + "energy_2030_" + charging + ".xlsx")
reference_excel2 = os.path.join("lca",str(reference_scenario), "results_" + reference_scenario + "_" + "energy_2030_" + charging + ".xlsx")

drtsc_lcatotal2 = pd.read_excel(os.path.join(drt_excel2), sheet_name="LCA_results_total")
referencesc_lcatotal2 = pd.read_excel(os.path.join(reference_excel2), sheet_name="LCA_results_total")

drtsc_infos2 = pd.read_excel(os.path.join(drt_excel2), sheet_name="vehicle_infos")
referencesc_infos2 = pd.read_excel(os.path.join(reference_excel2), sheet_name="vehicle_infos")


drt_excel3 = os.path.join("lca",str(drt_scenario), "results_" + drt_scenario + "_" + "energy_100_green_" + charging + ".xlsx")
reference_excel3 = os.path.join("lca",str(reference_scenario), "results_" + reference_scenario + "_" + "energy_100_green_" + charging + ".xlsx")

drtsc_lcatotal3 = pd.read_excel(os.path.join(drt_excel3), sheet_name="LCA_results_total")
referencesc_lcatotal3 = pd.read_excel(os.path.join(reference_excel3), sheet_name="LCA_results_total")

drtsc_infos3 = pd.read_excel(os.path.join(drt_excel3), sheet_name="vehicle_infos")
referencesc_infos3 = pd.read_excel(os.path.join(reference_excel3), sheet_name="vehicle_infos")


style = dict(size=20, color='black')

millionfactor = 1/1000000

drtsc_production = drtsc_lcatotal._values[2][1]
referencesc_production = referencesc_lcatotal._values[2][1]

drtsc_production2 = drtsc_lcatotal2._values[2][1]
referencesc_production2 = referencesc_lcatotal2._values[2][1]

drtsc_production3 = drtsc_lcatotal3._values[2][1]
referencesc_production3 = referencesc_lcatotal3._values[2][1]


imagefolder = os.path.join("lca", str(drt_scenario) + "_VS_" + str(reference_scenario))
if not os.path.exists(imagefolder):
    os.mkdir(imagefolder)

plt.rcParams["figure.figsize"] = (16,10)
# CO2 and km in one graph
# fig4 , (ax1, ax2) = plt.subplots(2, sharex=True)

# separated graphs
fig4 , (ax1, ax2) = plt.subplots(1, 2)

drtsc_co2year = drtsc_lcatotal._values[7][1]
referencesc_co2year = referencesc_lcatotal._values[7][1]

drtsc_kmperyear = drtsc_infos._values[24][1] + drtsc_infos._values[25][1]
drtsc_pkmperyear = drtsc_infos._values[27][1] + drtsc_infos._values[28][1]

referencesc_drtvehicles = referencesc_infos._values[8][1]
referencesc_nondrtvehicles = referencesc_infos._values[9][1]

referencesc_kmperyear = referencesc_infos._values[24][1] + referencesc_infos._values[25][1]
referencesc_pkmperyear = referencesc_infos._values[27][1] + referencesc_infos._values[28][1]

#--
drtsc_co2year2 = drtsc_lcatotal2._values[7][1]
referencesc_co2year2 = referencesc_lcatotal2._values[7][1]

drtsc_kmperyear2 = drtsc_infos2._values[24][1] + drtsc_infos2._values[25][1]
drtsc_pkmperyear2 = drtsc_infos2._values[27][1] + drtsc_infos2._values[28][1]

referencesc_drtvehicles2 = referencesc_infos2._values[8][1]
referencesc_nondrtvehicles2 = referencesc_infos2._values[9][1]

referencesc_kmperyear2 = referencesc_infos2._values[24][1] + referencesc_infos2._values[25][1]
referencesc_pkmperyear2 = referencesc_infos2._values[27][1] + referencesc_infos2._values[28][1]

#--
drtsc_co2year3 = drtsc_lcatotal3._values[7][1]
referencesc_co2year3 = referencesc_lcatotal3._values[7][1]

drtsc_kmperyear3 = drtsc_infos3._values[24][1] + drtsc_infos3._values[25][1]
drtsc_pkmperyear3 = drtsc_infos3._values[27][1] + drtsc_infos3._values[28][1]

referencesc_drtvehicles3 = referencesc_infos3._values[8][1]
referencesc_nondrtvehicles3 = referencesc_infos3._values[9][1]

referencesc_kmperyear3 = referencesc_infos3._values[24][1] + referencesc_infos3._values[25][1]
referencesc_pkmperyear3 = referencesc_infos3._values[27][1] + referencesc_infos3._values[28][1]

#--

years = []

drt_co2values = []
drt_co2values2 = []
drt_co2values3 = []
drt_km = []
drt_pkm = []

reference_co2values = []
reference_co2values_wo_production = []
reference_km = []
reference_pkm = []

billion_factor = 1 / 1000000000

for x in range(0,int(getfromconfig('vehicle_parameters', 'timespan_in_years'))+1,1):
    drt_co2values.append((drtsc_production + (drtsc_co2year * x)) * millionfactor)
    drt_co2values2.append((drtsc_production2 + (drtsc_co2year2 * x)) * millionfactor)
    drt_co2values3.append((drtsc_production3 + (drtsc_co2year3 * x)) * millionfactor)
    years.append(x)

    reference_co2values.append((referencesc_production + (referencesc_co2year * x)) * millionfactor)
    reference_co2values_wo_production.append(referencesc_co2year * x * millionfactor)

    drt_km.append(drtsc_kmperyear * x * billion_factor)
    reference_km.append(referencesc_kmperyear * x * billion_factor)

    drt_pkm.append(drtsc_pkmperyear * x * billion_factor)
    reference_pkm.append(referencesc_pkmperyear * x * billion_factor)


ax1.grid(visible=True)
ax1.set_title("GHG [$CO_2$ eq]", style)
ax1.plot(years, drt_co2values, label=drt_scenario + "_2021", color="orange")
ax1.plot(years, drt_co2values2, label=drt_scenario + "_2030", color="blue")
ax1.plot(years, drt_co2values3, label=drt_scenario + "_100_green", color="green")
ax1.plot(years, reference_co2values, label=reference_scenario, color="black")

#plot reference case with production emissions, because they are already in the past
ax1.plot(years, reference_co2values_wo_production, label=reference_scenario + "_wo_production_emissions", color="purple")

ax1.set_ylabel("GHG in million tonnes $CO_2$ eq [t]", fontsize=17)
ax1.tick_params(axis='both', labelsize = 17)
ax1.legend(loc="lower left",bbox_to_anchor=(0, 0.81), fontsize=12)
ax1.set_xticks(np.arange(0, max(years)+1, 1))
ax1.set_yticks(np.arange(0, max(reference_co2values)+2, 2))
ax1.set_xlim(left=0, right=max(years))
ax1.set_ylim(bottom=0)

# secondy = plt.twinx()a
ax2.set_title("total pkm [km]", style)
ax2.grid(visible=True)
ax2.plot(years, drt_pkm, label=drt_scenario, color="purple")
ax2.plot(years, reference_pkm, label=reference_scenario, color="blue")
ax2.legend(loc="lower left",bbox_to_anchor=(0, 0.91), fontsize=12)
ax2.set_ylabel("total km in billion pkm for scenario [km]", fontsize=17)
ax2.set_xlim(left=0, right=max(years))
ax2.set_ylim(bottom=0)
ax2.set_xticks(np.arange(0, max(years)+1, 1))
# secondy.set_ylim(bottom=0, top=max(reference_km))
# secondy.set_ylabel("total km in billion km for scenario [km]", style)
ax2.tick_params(axis='both', labelsize = 17)
# secondy.set_yticks(np.arange(0, max(reference_km), 5), style)

plt.xlabel("time in years", style)
# plt.ylim(bottom=0, top=max(reference_co2values))
fig4.savefig(os.path.join(imagefolder, 'gridmixes_compared' + '_co2_peryear_comparison.png'), dpi=300)

plt.show()
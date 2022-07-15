from postprocessing import *
from lca import *

path_drt = "/Users/dstobbe/Downloads/MATSIM Output/berlin-rebalancing-10000vehicles-4seats"
path_reference = "/Users/dstobbe/Downloads/MATSIM Output/berlin-v5.5.3-10pct"

# drt_info = calculate_avg_vehicle(path_drt)
# drt_vehicles_drt, drt_vehicles_nondrt = scale_scenario(drt_info)
# openlca = olcaclient()
# openlca.lifecycleassessment(drt_vehicles_drt, drt_vehicles_nondrt, getsimulationname(path_drt))

# reference_info = calculate_avg_vehicle(path_reference)
# vehicles_drt, vehicles_nondrt = scale_scenario(reference_info)
# openlca.lifecycleassessment(vehicles_drt, vehicles_nondrt, getsimulationname(path_reference))

# compare_scnearios(path_drt, path_reference)


drtsc_totalco2 = 5726490.175
drtsc_production = 1203816.031
drtsc_batteries = 87245.83402
drtsc_use = 938595.0513 + 3496833.258

referencesc_totalco2 = 6044389.144
referencesc_production = 1226912.765
referencesc_batteries = 145409.7234
referencesc_use = 938595.1051 + 3733471.55

millionfactor = 1/1000000

names = ("results_berlin-rebalancing-10000vehicles-2seats_energy_2030_opportunity", "results_berlin-rebalancing-10000vehicles-2seats_energy_2030_normal")
data={"production vehicles":[drtsc_production * millionfactor, referencesc_production * millionfactor], "additional batteries":(drtsc_batteries * millionfactor, referencesc_batteries * millionfactor), "use phase":(drtsc_use * millionfactor, referencesc_use * millionfactor)}
#gestacktes Balkendiagramm aus DF
df=pd.DataFrame(data,index=names)
ax2 = df.plot(kind="bar",stacked=True,figsize=(15,8), ylabel="in million tonnes $CO_2$ eq [t]", rot=0)

# x_offset = -0.03
# y_offset = 0.02
# for p in ax2.patches:
#     b = p.get_bbox()
#     val = "{:.2f}".format(b.y1 + b.y0)        
#     ax2.annotate(val, ((b.x0 + b.x1)/2 + x_offset, b.y1 + y_offset))

plt.title("GHG comparison with " + str(getfromconfig('vehicle_parameters','energymix')) + " and " + str(getfromconfig('vehicle_parameters','charging')) + " charging")
plt.legend(loc="upper right",bbox_to_anchor=(1, 1.15))
# plt.yticks(np.arange(0, referencesc_totalco2, 1000000000))
plt.yticks([drtsc_totalco2 * millionfactor, referencesc_totalco2 * millionfactor])
fig3 = plt.gcf()
imagefolder = os.path.join("lca", str("results_berlin-rebalancing-10000vehicles-2seats_energy_2030_opportunity") + "_VS_" + str("results_berlin-rebalancing-10000vehicles-2seats_energy_2030_normal"))
fig3.savefig(os.path.join(imagefolder, str(2030) + "_" + "opportunity_vs_normal_" + 'charging_totalco2_comparison.png'), dpi=300)
plt.show()
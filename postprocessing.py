from sympy import rotations
from configuration import *
from database_operations import *
from processing import *

import matplotlib.pyplot as plt
import numpy as np

import warnings
warnings.simplefilter("ignore")

def scale_scenario(vehicleinfo: dict, pct_scenario: int = 10):

    # scalingfactor for non linear scaling
    scalingfactor = 100/pct_scenario

    m_to_km = 1000

    years = int(getfromconfig('vehicle_parameters', 'timespan_in_years'))
    battery_lifetime = int(getfromconfig('vehicle_parameters', 'battery_exchange_after_km'))
    #calculating the amount of days for the timespan
    weeksinyear = 52.14
    workdays = weeksinyear * 5        # Mo-Fr
    weekenddays = weeksinyear * 2     # Sa-So
    weekendfactor = 77.5 / 88.2       # = 0.85      http://www.mobilitaet-in-deutschland.de/pdf/MiD2017_Ergebnisbericht.pdf

    # consunption factor based on speed and road percentages
    # factors need to be adjusted, maybe put into config
    highwaypct_factor = 1.3
    countryroad_factor = 1
    intown_factor = 1.2

    drt_vehicleamount_scaled = 0
    
    vehicles_drt = {}

    if vehicleinfo['drt_vehicleamount'] > 0:
        drt_vehicleamount = vehicleinfo['drt_vehicleamount']
        drt_avg_totalkm_region = vehicleinfo['drt_avg_totalkm_region']
        drt_avg_totalkm_notregion = vehicleinfo['drt_avg_totalkm_notregion']
        drt_avg_totalpkm = vehicleinfo['drt_avg_totalpkm']
        drt_avg_intown_pct = vehicleinfo['drt_avg_intown_pct']
        drt_avg_countryroad_pct = vehicleinfo['drt_avg_countryroad_pct']
        drt_avg_highway_pct = vehicleinfo['drt_avg_highway_pct']
        drt_avg_speed = vehicleinfo['drt_avg_speed_pervehicle']
        drt_avg_speed_pct = vehicleinfo['drt_avg_speed_pct']
        drt_avg_passenger = vehicleinfo['drt_avg_passenger_amount']
        drt_avg_passenger_wihtout_empty = vehicleinfo['drt_avgpassenger_without_empty']
        
        charging = getfromconfig('vehicle_parameters', 'charging')
        # upscaling factors where x is 0.1 for 10%
        # Berlin
        # x^−0.637 (R2 = 0.9954)
        # x^−0.662 (R2 = 0.9975) 
        # x^−0.928 (R2 = 0.9999)
        drt_scalingfactor_vehicles = ((pct_scenario/100)**(-0.637))                     # = 4,335 for 10 pct
        drt_scalingfactor_km = ((pct_scenario/100)**(-0.928))                           # = 8,472 for 10 pct
        drt_scalingfactor_km_pervehicle = drt_scalingfactor_km / drt_scalingfactor_vehicles     # = 1,954 for 10 pct
        drt_scalingfactor_persons = 1.3     # NEEDS TO BE ADJUSTED

        # drt_vehiclesize = getfromconfig('vehicle_parameters', 'drt_vehiclesize')
        # if int(drt_vehiclesize) == 2:
        #     drt_size = "small"
        # elif int(drt_vehiclesize) == 4:
        #     drt_size = "medium"
        # elif int(drt_vehiclesize) == 7:
        #     drt_size = "large"
        # drt_vehicleslist = create_drtvehicleids_list(cursor)
        # query_capacity = ''' SELECT capacity from vehicles WHERE vehicle_id = ?'''
        # vehicles_2 = 0; vehicles_4 = 0; vehicles_7 = 0
        # for vehicle in drt_vehicleslist:
        #     db_output = query_db(query_capacity, cursor, vehicle)
        #     capacity = db_output[0][0]
        #     if int(capacity) == 2:
        #         vehicles_2 += 1
        #     if int(capacity) == 4:
        #         vehicles_4 += 1
        #     if int(capacity) == 7:
        #         vehicles_7 += 1

        # if vehicles_2 > 0:
        vehicles_drt['small'] = {}
            # vehicles_drt['small']['amount'] = int(vehicles_2 * drt_scalingfactor_vehicles)
        vehicles_drt['small']['amount'] = int(vehicleinfo['small_vehicles'] * drt_scalingfactor_vehicles)
        # if vehicles_4 > 0:
        vehicles_drt['medium'] = {}
            # vehicles_drt['medium']['amount'] = int(vehicles_4 * drt_scalingfactor_vehicles)
        vehicles_drt['medium']['amount'] = int(vehicleinfo['medium_vehicles'] * drt_scalingfactor_vehicles)
        # if vehicles_7 > 0:
        vehicles_drt['large'] = {}
            # vehicles_drt['large']['amount'] = int(vehicles_7 * drt_scalingfactor_vehicles)
        vehicles_drt['large']['amount'] = int(vehicleinfo['large_vehicles'] * drt_scalingfactor_vehicles)

        if drt_avg_speed_pct < .5:
            drt_speed_pct_factor = 1.2
        elif drt_avg_speed_pct >= .5 and drt_avg_speed_pct < .7:
            drt_speed_factor = 1.1
        elif drt_avg_speed_pct >= .7 and drt_avg_speed_pct < .9:
            drt_speed_factor = 1.05
        else:
            drt_speed_factor = 1

        drt_vehicleamount_scaled = drt_vehicleamount * drt_scalingfactor_vehicles
        drt_vehicleamount_scaled = int(drt_vehicleamount_scaled) + 1

        drt_avg_passenger_scaled = drt_avg_passenger * drt_scalingfactor_persons

        # per year
        drt_km_year_vehicle = ((workdays * drt_avg_totalkm_region) + (weekenddays * weekendfactor * drt_avg_totalkm_region)) / m_to_km
        drt_km_year_vehicle_scaled = (drt_km_year_vehicle * drt_scalingfactor_km_pervehicle)
        drt_km_year_fleet = (drt_km_year_vehicle * drt_vehicleamount)

        # -- for further use --- #
        drt_km_year_fleet_scaled = (drt_km_year_fleet * drt_scalingfactor_km_pervehicle * drt_scalingfactor_vehicles)
        drt_pkm_year_fleet_scaled = drt_km_year_fleet_scaled * drt_avg_passenger_scaled

        # for lifespan
        drt_km_lifespan_vehicle = (drt_km_year_vehicle * years)
        drt_km_lifespan_vehicle_scaled = (drt_km_lifespan_vehicle * drt_scalingfactor_km_pervehicle)
        drt_km_lifespan_fleet = (drt_km_lifespan_vehicle * drt_vehicleamount)

        # -- for further use --- #
        drt_km_lifespan_fleet_scaled = (drt_km_lifespan_fleet * drt_scalingfactor_km_pervehicle * drt_scalingfactor_vehicles)
        drt_pkm_lifespan_fleet_scaled = drt_km_lifespan_fleet_scaled * drt_avg_passenger_scaled

        drt_add_batteries_lifespan_vehicle = (drt_km_lifespan_vehicle_scaled/battery_lifetime) -1   # -1 due to one battery already beeing included in production
        if int(drt_add_batteries_lifespan_vehicle) < drt_add_batteries_lifespan_vehicle:
            drt_add_batteries_lifespan_vehicle += 1
        drt_add_batteries_lifespan_vehicle = int(drt_add_batteries_lifespan_vehicle)
        
        drt_consumption_km_amount = 0
        vehicles_drt['consumption'] = 0
        # would need to analyze per vehicle type here in order for pkm average to work properly

        for drt_size in vehicles_drt:
            if drt_size == "small" or drt_size == "medium" or drt_size == "large":
                consumption_type = "consumption_" + drt_size
                if charging == "opportunity":
                    consumption_type = consumption_type + "_opportunity"
                drt_consumption_100km = float(getfromvehicleconfig('energy_consumption', consumption_type))

                drt_totalroad_factor = (drt_avg_intown_pct * intown_factor) + (drt_avg_countryroad_pct * countryroad_factor) + (drt_avg_highway_pct * highwaypct_factor)
                drt_consumption_km = (drt_consumption_100km * drt_speed_factor * drt_totalroad_factor) / 100

                drt_consumption_km_amount += drt_consumption_km * vehicles_drt[drt_size]['amount']

                vehicles_drt[drt_size]['consumption_km'] = drt_consumption_km
                vehicles_drt[drt_size]['batteries'] = vehicles_drt[drt_size]['amount'] * drt_add_batteries_lifespan_vehicle
                vehicles_drt[drt_size]['km'] = drt_km_lifespan_fleet_scaled * (vehicles_drt[drt_size]['amount'] / drt_vehicleamount_scaled)
                vehicles_drt[drt_size]['pkm'] = drt_pkm_lifespan_fleet_scaled * (vehicles_drt[drt_size]['amount'] / drt_vehicleamount_scaled)
                vehicles_drt['consumption'] += drt_consumption_km * vehicles_drt[drt_size]['km']
        vehicles_drt['totalkm'] = drt_km_lifespan_fleet_scaled
        vehicles_drt['totalpkm'] = drt_pkm_lifespan_fleet_scaled
        vehicles_drt['km_per_vehicle_day'] = (drt_avg_totalkm_region / m_to_km) * drt_scalingfactor_km_pervehicle
        vehicles_drt['pkm_per_vehicle_day'] = ((drt_avg_totalkm_region / m_to_km) * drt_scalingfactor_km_pervehicle) * drt_avg_passenger_scaled
        vehicles_drt['km_per_vehicle_year'] = drt_km_year_vehicle_scaled
        vehicles_drt['pkm_per_vehicle_year'] = drt_km_year_vehicle_scaled * drt_avg_passenger_scaled
        vehicles_drt['total_batteries'] = drt_add_batteries_lifespan_vehicle * drt_vehicleamount_scaled
        vehicles_drt['avg_speed'] = vehicleinfo['drt_avg_speed_pervehicle']
        vehicles_drt['speed_pct'] = vehicleinfo['drt_avg_speed_pct']
        vehicles_drt['avg_passengers'] = vehicleinfo['drt_avg_passenger_amount'] * drt_scalingfactor_persons
        vehicles_drt['total_vehicles'] = drt_vehicleamount_scaled

        # vehicles_drt['consumption'] = drt_consumption_km_amount
        # vehicles_drt['consumption_lifespan_fleet'] = drt_consumption_km * drt_km_year_fleet_scaled

        # drt_consumption_year_fleet = drt_km_year_fleet_scaled * drt_consumption_km_average
        
        # drt_consumption_lifespan_fleet = drt_km_lifespan_fleet_scaled * drt_consumption_km_average

    
    # non drt vehicles
    vehicleamount = vehicleinfo['vehicleamount']
    avg_totalkm = vehicleinfo['avg_totalkm']
    avg_intown_pct = vehicleinfo['avg_intown_pct']
    avg_countryroad_pct = vehicleinfo['avg_countryroad_pct']
    avg_highway_pct = vehicleinfo['avg_highway_pct']
    avg_speed = vehicleinfo['avg_speed_pervehicle']
    avg_speed_pct = vehicleinfo['avg_speed_pct']


    share_small = float(getfromvehicleconfig('vehicle_distribution','share_small', True))
    share_medium = float(getfromvehicleconfig('vehicle_distribution','share_medium', True))
    share_large = float(getfromvehicleconfig('vehicle_distribution','share_large', True))
    share_plugin = float(getfromvehicleconfig('vehicle_distribution','share_plugin', True))
    share_electric = float(getfromvehicleconfig('vehicle_distribution','share_electric', True)) + 0.5 * share_plugin      # due to a non existent model of plugin hybrids
    share_petrol = float(getfromvehicleconfig('vehicle_distribution','share_petrol', True)) + 0.5 * share_plugin          # each petrol and electric gain half of the plugin percentage
    share_diesel = float(getfromvehicleconfig('vehicle_distribution','share_diesel', True))
    avg_passengers = float(getfromconfig('vehicle_parameters', 'average_utilization_pkw'))

    vehicleamount_scaled = vehicleamount * scalingfactor

    vehicles_nondrt = {}
    vehicles_nondrt['petrol'] = {}
    vehicles_nondrt['petrol']['small'] = {}
    vehicles_nondrt['petrol']['small']['amount'] = int(vehicleamount_scaled * share_petrol * share_small)
    vehicles_nondrt['petrol']['medium'] = {}
    vehicles_nondrt['petrol']['medium']['amount'] = int(vehicleamount_scaled * share_petrol * share_medium)
    vehicles_nondrt['petrol']['large'] = {}
    vehicles_nondrt['petrol']['large']['amount'] = int(vehicleamount_scaled * share_petrol * share_large)
    
    vehicles_nondrt['diesel'] = {}
    vehicles_nondrt['diesel']['small'] = {}
    vehicles_nondrt['diesel']['small']['amount'] = int(vehicleamount_scaled * share_diesel * share_small)
    vehicles_nondrt['diesel']['medium'] = {}
    vehicles_nondrt['diesel']['medium']['amount'] = int(vehicleamount_scaled * share_diesel * share_medium)
    vehicles_nondrt['diesel']['large'] = {}
    vehicles_nondrt['diesel']['large']['amount'] = int(vehicleamount_scaled * share_diesel * share_large)
    
    vehicles_nondrt['electric'] = {}
    vehicles_nondrt['electric']['small'] = {}
    vehicles_nondrt['electric']['small']['amount'] = int(vehicleamount_scaled * share_electric * share_small)
    vehicles_nondrt['electric']['medium'] = {}
    vehicles_nondrt['electric']['medium']['amount'] = int(vehicleamount_scaled * share_electric * share_medium)
    vehicles_nondrt['electric']['large'] = {}
    vehicles_nondrt['electric']['large']['amount'] = int(vehicleamount_scaled * share_electric * share_large)

    # per year
    km_year_vehicle = ((workdays * avg_totalkm) + (weekenddays * weekendfactor * avg_totalkm)) / m_to_km
    km_year_fleet_scaled = km_year_vehicle * vehicleamount_scaled
    pkm_year_fleet_scaled = km_year_fleet_scaled * avg_passengers

    km_lifespan_vehicle = km_year_vehicle * years
    km_lifespan_fleet_scaled = km_year_fleet_scaled * years
    pkm_lifespan_fleet_scaled = km_lifespan_fleet_scaled * avg_passengers

    vehicles_nondrt['petrol']['small']['km'] = km_lifespan_fleet_scaled * share_petrol * share_small
    vehicles_nondrt['petrol']['medium']['km'] = km_lifespan_fleet_scaled * share_petrol * share_medium
    vehicles_nondrt['petrol']['large']['km'] = km_lifespan_fleet_scaled * share_petrol * share_large

    vehicles_nondrt['diesel']['small']['km'] = km_lifespan_fleet_scaled * share_diesel * share_small
    vehicles_nondrt['diesel']['medium']['km'] = km_lifespan_fleet_scaled * share_diesel * share_medium
    vehicles_nondrt['diesel']['large']['km'] = km_lifespan_fleet_scaled * share_diesel * share_large

    vehicles_nondrt['electric']['small']['km'] = km_lifespan_fleet_scaled * share_electric * share_small
    vehicles_nondrt['electric']['medium']['km'] = km_lifespan_fleet_scaled * share_electric * share_medium
    vehicles_nondrt['electric']['large']['km'] = km_lifespan_fleet_scaled * share_electric * share_large

    vehicles_nondrt['electric']['small']['batteries'] = int((km_lifespan_vehicle / battery_lifetime)) * vehicleamount_scaled * share_electric * share_small
    vehicles_nondrt['electric']['medium']['batteries'] = int((km_lifespan_vehicle / battery_lifetime)) * vehicleamount_scaled * share_electric * share_medium
    vehicles_nondrt['electric']['large']['batteries'] = int((km_lifespan_vehicle / battery_lifetime)) * vehicleamount_scaled * share_electric * share_large

    consumption_petrol_small = float(getfromvehicleconfig('combustion_consumption', 'consumption_petrol_small', True)) / 100
    consumption_petrol_medium = float(getfromvehicleconfig('combustion_consumption', 'consumption_petrol_medium', True)) / 100
    consumption_petrol_large = float(getfromvehicleconfig('combustion_consumption', 'consumption_petrol_large', True)) / 100
    consumption_diesel_small = float(getfromvehicleconfig('combustion_consumption', 'consumption_diesel_small', True)) / 100
    consumption_diesel_medium = float(getfromvehicleconfig('combustion_consumption', 'consumption_diesel_medium', True)) / 100
    consumption_diesel_large = float(getfromvehicleconfig('combustion_consumption', 'consumption_diesel_large', True)) / 100

    consumption_electric_small = float(getfromvehicleconfig('energy_consumption', 'consumption_small', True)) / 100
    consumption_electric_medium = float(getfromvehicleconfig('energy_consumption', 'consumption_medium', True)) / 100
    consumption_electric_large = float(getfromvehicleconfig('energy_consumption', 'consumption_large', True)) / 100

    consumption_petrol = km_lifespan_fleet_scaled * share_petrol * ((share_small * consumption_petrol_small) + (share_medium * consumption_petrol_medium) + (share_large * consumption_petrol_large))
    consumption_diesel = km_lifespan_fleet_scaled * share_diesel * ((share_small * consumption_diesel_small) + (share_medium * consumption_diesel_medium) + (share_large * consumption_diesel_large))
    consumption_electric = km_lifespan_fleet_scaled * share_electric * ((share_small * consumption_electric_small) + (share_medium * consumption_electric_medium) + (share_large * consumption_electric_large))

    vehicles_nondrt['petrol']['consumption'] = consumption_petrol
    vehicles_nondrt['diesel']['consumption'] = consumption_diesel
    vehicles_nondrt['electric']['consumption'] = consumption_electric

    vehicles_nondrt['totalkm'] = km_lifespan_fleet_scaled
    vehicles_nondrt['totalpkm'] = pkm_lifespan_fleet_scaled
    vehicles_nondrt['km_per_vehicle_day'] = avg_totalkm / m_to_km
    vehicles_nondrt['pkm_per_vehicle_day'] = (avg_totalkm / m_to_km) * avg_passengers
    vehicles_nondrt['km_per_vehicle_year'] = km_year_vehicle
    vehicles_nondrt['pkm_per_vehicle_year'] = (km_year_vehicle) * avg_passengers
    vehicles_nondrt['avg_speed'] = vehicleinfo['avg_speed_pervehicle']
    vehicles_nondrt['speed_pct'] = vehicleinfo['avg_speed_pct']
    vehicles_nondrt['total_vehicles'] = vehicleamount_scaled

    return vehicles_drt, vehicles_nondrt


def compare_scnearios(path_drt, path_reference):
    
    drt_scenario = getsimulationname(path_drt)
    reference_scenario = getsimulationname(path_reference)

    drt_excel = os.path.join("lca","results_" + drt_scenario + ".xlsx")
    reference_excel = os.path.join("lca","results_" +  reference_scenario + ".xlsx")

    drtsc_lcatotal = pd.read_excel(os.path.join(drt_excel), sheet_name="LCA_results_total")
    referencesc_lcatotal = pd.read_excel(os.path.join(reference_excel), sheet_name="LCA_results_total")

    drtsc_infos = pd.read_excel(os.path.join(drt_excel), sheet_name="vehicle_infos")
    referencesc_infos = pd.read_excel(os.path.join(reference_excel), sheet_name="vehicle_infos")

    style = dict(size=20, color='black')

    millionfactor = 1/1000000

    # ------------------- vehicle amount comparison -------------------- #

    drtsc_drtvehicles = drtsc_infos._values[8][1]
    drtsc_nondrtvehicles = drtsc_infos._values[9][1]

    referencesc_drtvehicles = referencesc_infos._values[8][1]
    referencesc_nondrtvehicles = referencesc_infos._values[9][1]

    names = (drt_scenario, reference_scenario)
    data={"drt_vehicles_electric":[drtsc_drtvehicles, referencesc_drtvehicles], "non_drt_vehicles_combustion":(drtsc_nondrtvehicles * (float(getfromvehicleconfig('vehicle_distribution', 'share_petrol', True)) + float(getfromvehicleconfig('vehicle_distribution', 'share_diesel', True)) + (1/2) * float(getfromvehicleconfig('vehicle_distribution', 'share_plugin', True))), referencesc_nondrtvehicles * (float(getfromvehicleconfig('vehicle_distribution', 'share_petrol', True)) + float(getfromvehicleconfig('vehicle_distribution', 'share_diesel', True)) + (1/2) * float(getfromvehicleconfig('vehicle_distribution', 'share_plugin', True)))), "non_drt_vehicles_electric":(drtsc_nondrtvehicles * (float(getfromvehicleconfig('vehicle_distribution', 'share_electric', True)) + float(getfromvehicleconfig('vehicle_distribution', 'share_plugin', True))), referencesc_nondrtvehicles * (float(getfromvehicleconfig('vehicle_distribution', 'share_electric', True)) + float(getfromvehicleconfig('vehicle_distribution', 'share_plugin', True))))}
    #gestacktes Balkendiagramm aus DF
    va=pd.DataFrame(data,index=names)
    va.plot(kind="bar",stacked=True,figsize=(10,8), ylabel="in t $C0_{2}$ äq")

    plt.title("vehicle amount")
    plt.legend(loc="upper right", bbox_to_anchor=(1, 1.15))
    plt.ylabel("number of vehicles")
    plt.yticks([drtsc_drtvehicles + drtsc_nondrtvehicles, referencesc_drtvehicles + referencesc_nondrtvehicles])
    fig1 = plt.gcf()
    # plt.show()

    # ------------------- km comparison -------------------- #

    drtsc_km = drtsc_infos._values[0][1]
    drtsc_pkm = drtsc_infos._values[4][1]

    referencesc_km = referencesc_infos._values[0][1]
    referencesc_pkm = referencesc_infos._values[4][1]

    data={"km":[drtsc_km * millionfactor, referencesc_km * millionfactor], "pkm":(drtsc_pkm * millionfactor, referencesc_pkm * millionfactor)}
    #gestacktes Balkendiagramm aus DF
    km=pd.DataFrame(data,index=names)
    km.plot(kind="bar",stacked=False,figsize=(10,8), ylabel="vehicle km and pkm in millions")

    plt.title("km compariosn")
    plt.legend(loc="upper right",bbox_to_anchor=(1, 1.15))
    plt.yticks([drtsc_km * millionfactor, drtsc_pkm * millionfactor, referencesc_km * millionfactor, referencesc_pkm * millionfactor])
    fig1 = plt.gcf()
    # plt.show()

    # ------------------- total CO2 comparison -------------------- #

    drtsc_totalco2 = drtsc_lcatotal._values[0][1]
    drtsc_production = drtsc_lcatotal._values[2][1]
    drtsc_batteries = drtsc_lcatotal._values[3][1]
    drtsc_use = drtsc_lcatotal._values[4][1] + drtsc_lcatotal._values[5][1]

    referencesc_totalco2 = referencesc_lcatotal._values[0][1]
    referencesc_production = referencesc_lcatotal._values[2][1]
    referencesc_batteries = referencesc_lcatotal._values[3][1]
    referencesc_use = (referencesc_lcatotal._values[4][1] + referencesc_lcatotal._values[5][1])

    names = (drt_scenario, reference_scenario)
    data={"production vehicles":[drtsc_production * millionfactor, referencesc_production * millionfactor], "additional batteries":(drtsc_batteries * millionfactor, referencesc_batteries * millionfactor), "use phase":(drtsc_use * millionfactor, referencesc_use * millionfactor)}
    #gestacktes Balkendiagramm aus DF
    df=pd.DataFrame(data,index=names)
    df.plot(kind="bar",stacked=True,figsize=(10,8), ylabel="in million tonnes $C0_{2}$ äq")

    plt.title("GHG comparison")
    plt.legend(loc="upper right",bbox_to_anchor=(1, 1.15))
    # plt.yticks(np.arange(0, referencesc_totalco2, 1000000000))
    plt.yticks([drtsc_totalco2 * millionfactor, referencesc_totalco2 * millionfactor])
    fig1 = plt.gcf()
    # plt.show()

    # ------------------- CO2 per year comparison ----#------------ #

    plt.rcParams["figure.figsize"] = (16,10)
    plt.figure(4)
    
    drtsc_co2year = drtsc_lcatotal._values[7][1]
    referencesc_co2year = referencesc_lcatotal._values[7][1]

    drtsc_kmperyear = drtsc_infos._values[21][1] + drtsc_infos._values[22][1]
    drtsc_pkmperyear = drtsc_infos._values[24][1] + drtsc_infos._values[25][1]

    referencesc_drtvehicles = referencesc_infos._values[8][1]
    referencesc_nondrtvehicles = referencesc_infos._values[9][1]

    referencesc_kmperyear = referencesc_infos._values[21][1] + referencesc_infos._values[22][1]
    referencesc_pkmperyear = referencesc_infos._values[24][1] + referencesc_infos._values[25][1]

    years = []

    drt_co2values = []
    drt_km = []
    drt_pkm = []

    reference_co2values = []
    reference_km = []
    reference_pkm = []

    billion_factor = 1 / 1000000000

    for x in range(0,11,1):
        drt_co2values.append((drtsc_production + (drtsc_co2year * x)) * millionfactor)
        years.append(x)

        reference_co2values.append((referencesc_production + (referencesc_co2year * x)) * millionfactor)

        drt_km.append(drtsc_kmperyear * x * billion_factor)
        reference_km.append(referencesc_kmperyear * x * billion_factor)

        drt_pkm.append(drtsc_pkmperyear * x)
        reference_pkm.append(referencesc_pkmperyear * x)


    plt.grid(visible=True)
    plt.plot(years, drt_co2values, label="DRT", color="green")
    plt.plot(years, reference_co2values, label="reference", color="black")
    plt.ylabel("in million tonnes $C0_{2}$ äq", style)
    plt.tick_params(axis='both', labelsize = 17)
    plt.legend(loc="lower left",bbox_to_anchor=(0, 1.0), fontsize=17)
    plt.xticks(np.arange(0, max(years), 1))
    # plt.yticks(np.arange(0, max(reference_co2values), 2))

    secondy = plt.twinx()
    secondy.plot(years, drt_km, label="DRT", color="purple")
    secondy.plot(years, reference_km, label="reference", color="blue")
    secondy.legend(loc="lower left",bbox_to_anchor=(0.8, 1.0), fontsize=17)
    secondy.set_ylim(bottom=0)
    # # secondy.set_yticks(np.arange(0, max(reference_km)))


    plt.title("GHG and km", style)
    plt.xlabel("time in years", style)
    # plt.ylim(bottom=0, top=max(reference_co2values))
    plt.xlim(left=0, right=max(years))
    # fig2 = plt.gcf()
    # fig2.savefig(os.path.join('lca', 'co2peryearcomparison.png'), dpi=300)

    plt.show()

    print("test")
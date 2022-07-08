from sympy import rotations
from configuration import *
from database_operations import *
from processing import *

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

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
    # based on [Öko-Institut 2009] ÖKO-INSTITUT: RENEWBILITY „Stoffstromanalyse nachhaltige Mobilität im Kontext erneuerbarer Energien bis 2030“. (2009). – Öko-Institut e.V. (Büros Darmstadt und Berlin) and DLR-Institut für Verkehrsforschung (Berlin). - Endbericht an das Bundesministerium für Umwelt, Naturschutz und Reaktorsicherheit (BMU)
    # factors could be put into config
    highwaypct_factor = 1.3
    countryroad_factor = 1
    intown_factor = 1.4

    electric_highwaypct_factor = 1.55
    electric_countryroad_factor = 1
    electric_intown_factor = 1.1

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
        # source for scaling factors: https://pdf.sciencedirectassets.com/280203/1-s2.0-S1877050921X00075/1-s2.0-S1877050921007213/main.pdf?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEFIaCXVzLWVhc3QtMSJHMEUCIQCc6tYDCQfGro5Thl%2BQOaLcPNB4rTJhD2f3VSKt%2BN3M%2FAIgJ8j0oDkf3fDz%2Bc1RDQYXiXof9Y3U951%2FMOPCGv5yF5kq0gQIexAEGgwwNTkwMDM1NDY4NjUiDLj5Vj9YZjRQjcyCaiqvBBmZ2b%2FilIqT1McNkS7LuLkFYVPEeflzMQpVqULiDjsgoG%2B9XVhtbbLObcF9kpCLeVF5SEn5Nja2WUTC1o4d79qfsZNDKbApEHdJcm%2BNycjtcLFd3R3n0ggSrg46d6gYjl8okgaF6Zk9%2FzWnrERFmlWE2tVwp2dW5wgq5638PiV1z%2FW4KxF%2FDwtCXGtVeoFvqXaxglSQnGK0eSYybCkVddYDZLobFXo6h4ony%2BYJCSU4nl%2BioKh1acj1hEYvWArGFscpRsowyBa%2BzzLdf7Rf5RV80mpFrY7G%2F8SBFGvQz5TKom8g8Hpf0E4obexfPTW2VFpzRJYBgxEn2hL5JRad7r1m6EuqeEO9g1tXoqsUujj1jtr5Mibq5WvrELpb%2FNshy3h1apYoZTLWTN0iUKgu8ZlKqt1vFsM11oCyN1f69IwUmmGdkxOpiKNvSKx6J3CEcIsTGIC%2Bh1Zjvl1BcS8xpXfYqazE6LNeoreaK9Gd0mZHXy%2F7HZcjUawnhK6Gyed8ld7UarDMQzRYok4Ynq0KDXh81u3BCViRgSrQy4lou37oDK5w0FIwVIeJ1Vt%2BTZfOCK5Ao7cNpd15HKl%2Bcvs8uOX%2F2Ray4igdLXudZyaHUclKiP760RDLLPBw5D3RLrwqh0YFOhh1qLYmo%2FcVPjMv%2BhKWBGL6aOmwbbAcsT8uhWVwfaDXBWar1fl9dL9%2BbDI4gkTpIGMuIu2lN9Q5Wok5%2BGH%2FXAaJTXzRUohll5rAFhwwwqCHlgY6qQFGQ%2FSnlUn%2FJEVQz764OBLULlA6tvi45fMZvmdFOZl3mwXMB05q3Bt7y1k3LhgPg98dZzZIvK3aTU6vVkTUbqwfxQnt8gancp1f1i04ntoT%2FD%2BGTrd27x2Clk9NZgNAO7SBjSdbVl6Soe2wXW48PJAZwVuKMZGtXrytv5uWIbvrkkS1RTGcsl68i64T2JPkd6zcT9CWFUGgapyQINGafowXMqBikgRvZPuO&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220703T182230Z&X-Amz-SignedHeaders=host&X-Amz-Expires=300&X-Amz-Credential=ASIAQ3PHCVTYZVDVRKFB%2F20220703%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=37ad71991320ec58879fed994ce1e008a73ff52fe739bca03f96ce94f9df8b4c&hash=dce5b8f4aea15b018abb70fe5c9b5e640eea2ea1ca54fad70c9c71bfb5945082&host=68042c943591013ac2b2430a89b270f6af2c76d8dfd086a07176afe7c76c2c61&pii=S1877050921007213&tid=spdf-481f00d8-9eea-47c1-8810-670f87b49dfb&sid=9f2a069b5d05b748bf99fb183bca2dbc680cgxrqb&type=client&ua=4d5c525304565f095905&rr=7251a59f6fccb395
        # upscaling factors where x is 0.1 for 10%
        # Berlin
        # x^−0.637 (R2 = 0.9954)
        # x^−0.662 (R2 = 0.9975) 
        # x^−0.928 (R2 = 0.9999)
        drt_scalingfactor_vehicles = ((pct_scenario/100)**(-0.637))                     # = 4,335 for 10 pct
        drt_scalingfactor_km = ((pct_scenario/100)**(-0.928))                           # = 8,472 for 10 pct
        drt_scalingfactor_km_pervehicle = drt_scalingfactor_km / drt_scalingfactor_vehicles     # = 1,954 for 10 pct
        drt_scalingfactor_persons = 1.33     # NEEDS TO BE ADJUSTED

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
            drt_speed_factor = 1.2
        elif drt_avg_speed_pct >= .5 and drt_avg_speed_pct < .7:
            drt_speed_factor = 1.1
        elif drt_avg_speed_pct >= .7 and drt_avg_speed_pct < .9:
            drt_speed_factor = 1.05
        else:
            drt_speed_factor = 1

        drt_vehicleamount_scaled = drt_vehicleamount * drt_scalingfactor_vehicles
        drt_vehicleamount_scaled = int(drt_vehicleamount_scaled)

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

                drt_totalroad_factor = (drt_avg_intown_pct * electric_intown_factor) + (drt_avg_countryroad_pct * electric_countryroad_factor) + (drt_avg_highway_pct * electric_highwaypct_factor)
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

    totalroad_factor = (avg_intown_pct * intown_factor) + (avg_countryroad_pct * countryroad_factor) + (avg_highway_pct * highwaypct_factor)
    electric_totalroad_factor = (avg_intown_pct * electric_intown_factor) + (avg_countryroad_pct * electric_countryroad_factor) + (avg_highway_pct * electric_highwaypct_factor)

    if avg_speed_pct < .5:
        electric_speed_factor = 1.2
        speed_factor = 1.4
    elif avg_speed_pct >= .5 and avg_speed_pct < .7:
        electric_speed_factor = 1.1
        speed_factor = 1.3
    elif avg_speed_pct >= .7 and avg_speed_pct < .9:
        electric_speed_factor = 1.05
        speed_factor = 1.1
    else:
        electric_speed_factor = 1
        speed_factor = 1

    share_small = float(getfromvehicleconfig('vehicle_distribution','share_small', True))
    share_medium = float(getfromvehicleconfig('vehicle_distribution','share_medium', True))
    share_large = float(getfromvehicleconfig('vehicle_distribution','share_large', True))
    share_plugin = float(getfromvehicleconfig('vehicle_distribution','share_plugin', True))
    share_electric = float(getfromvehicleconfig('vehicle_distribution','share_electric', True)) + 0.5 * share_plugin      # due to a non existent model of plugin hybrids
    share_petrol = float(getfromvehicleconfig('vehicle_distribution','share_petrol', True)) + 0.5 * share_plugin          # each petrol and electric gain half of the plugin percentage
    share_diesel = float(getfromvehicleconfig('vehicle_distribution','share_diesel', True))
    avg_passengers = float(getfromconfig('vehicle_parameters', 'average_utilization_pkw'))

    vehicleamount_scaled = vehicleamount * scalingfactor
    pct_standstill = float(getfromconfig('settings', 'pct_standstill'))
    vehicleamount_w_standstill_scaled = vehicleamount_scaled / (1-pct_standstill)

    vehicles_nondrt = {}
    vehicles_nondrt['petrol'] = {}
    vehicles_nondrt['petrol']['small'] = {}
    vehicles_nondrt['petrol']['small']['amount'] = int(vehicleamount_w_standstill_scaled * share_petrol * share_small)
    vehicles_nondrt['petrol']['medium'] = {}
    vehicles_nondrt['petrol']['medium']['amount'] = int(vehicleamount_w_standstill_scaled * share_petrol * share_medium)
    vehicles_nondrt['petrol']['large'] = {}
    vehicles_nondrt['petrol']['large']['amount'] = int(vehicleamount_w_standstill_scaled * share_petrol * share_large)
    
    vehicles_nondrt['diesel'] = {}
    vehicles_nondrt['diesel']['small'] = {}
    vehicles_nondrt['diesel']['small']['amount'] = int(vehicleamount_w_standstill_scaled * share_diesel * share_small)
    vehicles_nondrt['diesel']['medium'] = {}
    vehicles_nondrt['diesel']['medium']['amount'] = int(vehicleamount_w_standstill_scaled * share_diesel * share_medium)
    vehicles_nondrt['diesel']['large'] = {}
    vehicles_nondrt['diesel']['large']['amount'] = int(vehicleamount_w_standstill_scaled * share_diesel * share_large)
    
    vehicles_nondrt['electric'] = {}
    vehicles_nondrt['electric']['small'] = {}
    vehicles_nondrt['electric']['small']['amount'] = int(vehicleamount_w_standstill_scaled * share_electric * share_small)
    vehicles_nondrt['electric']['medium'] = {}
    vehicles_nondrt['electric']['medium']['amount'] = int(vehicleamount_w_standstill_scaled * share_electric * share_medium)
    vehicles_nondrt['electric']['large'] = {}
    vehicles_nondrt['electric']['large']['amount'] = int(vehicleamount_w_standstill_scaled * share_electric * share_large)

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

    consumption_petrol = km_lifespan_fleet_scaled * share_petrol * speed_factor * totalroad_factor * ((share_small * consumption_petrol_small) + (share_medium * consumption_petrol_medium) + (share_large * consumption_petrol_large))
    consumption_diesel = km_lifespan_fleet_scaled * share_diesel * speed_factor * totalroad_factor * ((share_small * consumption_diesel_small) + (share_medium * consumption_diesel_medium) + (share_large * consumption_diesel_large))
    consumption_electric = km_lifespan_fleet_scaled * share_electric * electric_speed_factor * electric_totalroad_factor * ((share_small * consumption_electric_small) + (share_medium * consumption_electric_medium) + (share_large * consumption_electric_large))

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
    vehicles_nondrt['total_vehicles'] = vehicleamount_w_standstill_scaled

    return vehicles_drt, vehicles_nondrt


def compare_scnearios(path_drt, path_reference):
    
    drt_scenario = getsimulationname(path_drt)
    reference_scenario = getsimulationname(path_reference)

    drt_excel = os.path.join("lca",str(drt_scenario), "results_" + drt_scenario + ".xlsx")
    reference_excel = os.path.join("lca",str(reference_scenario), "results_" +  reference_scenario + ".xlsx")

    drtsc_lcatotal = pd.read_excel(os.path.join(drt_excel), sheet_name="LCA_results_total")
    referencesc_lcatotal = pd.read_excel(os.path.join(reference_excel), sheet_name="LCA_results_total")

    drtsc_infos = pd.read_excel(os.path.join(drt_excel), sheet_name="vehicle_infos")
    referencesc_infos = pd.read_excel(os.path.join(reference_excel), sheet_name="vehicle_infos")

    style = dict(size=20, color='black')

    millionfactor = 1/1000000

    imagefolder = os.path.join("lca", datetime.today().strftime('%Y-%m-%d_%H-%M-%S'))
    if not os.path.exists(imagefolder):
        os.mkdir(imagefolder)

    # ------------------- vehicle amount comparison -------------------- #

    drtsc_drtvehicles = drtsc_infos._values[8][1]
    drtsc_nondrtvehicles = drtsc_infos._values[12][1]

    referencesc_drtvehicles = referencesc_infos._values[8][1]
    referencesc_nondrtvehicles = referencesc_infos._values[12][1]

    names = (drt_scenario, reference_scenario)
    data={"drt_vehicles_electric":[drtsc_drtvehicles, referencesc_drtvehicles], "non_drt_vehicles_combustion":(drtsc_nondrtvehicles * (float(getfromvehicleconfig('vehicle_distribution', 'share_petrol', True)) + float(getfromvehicleconfig('vehicle_distribution', 'share_diesel', True)) + (1/2) * float(getfromvehicleconfig('vehicle_distribution', 'share_plugin', True))), referencesc_nondrtvehicles * (float(getfromvehicleconfig('vehicle_distribution', 'share_petrol', True)) + float(getfromvehicleconfig('vehicle_distribution', 'share_diesel', True)) + (1/2) * float(getfromvehicleconfig('vehicle_distribution', 'share_plugin', True)))), "non_drt_vehicles_electric":(drtsc_nondrtvehicles * (float(getfromvehicleconfig('vehicle_distribution', 'share_electric', True)) + float(getfromvehicleconfig('vehicle_distribution', 'share_plugin', True))), referencesc_nondrtvehicles * (float(getfromvehicleconfig('vehicle_distribution', 'share_electric', True)) + float(getfromvehicleconfig('vehicle_distribution', 'share_plugin', True))))}
    #gestacktes Balkendiagramm aus DF
    va=pd.DataFrame(data,index=names)
    va.plot(kind="bar",stacked=True,figsize=(10,8), ylabel="in t $C0_{2}$ eq", rot=0)

    plt.title("vehicle amount")
    plt.legend(loc="upper right", bbox_to_anchor=(1, 1.15))
    plt.ylabel("number of vehicles")
    plt.yticks([drtsc_drtvehicles + drtsc_nondrtvehicles, referencesc_drtvehicles + referencesc_nondrtvehicles])
    fig1 = plt.gcf()

    fig1.savefig(os.path.join(imagefolder, 'vehicleamount_comparison.png'), dpi=300)
    # plt.show()

    # ------------------- km comparison -------------------- #

    drtsc_km = drtsc_infos._values[0][1]
    drtsc_pkm = drtsc_infos._values[4][1]

    referencesc_km = referencesc_infos._values[0][1]
    referencesc_pkm = referencesc_infos._values[4][1]

    data={"km":[drtsc_km * millionfactor, referencesc_km * millionfactor], "pkm":(drtsc_pkm * millionfactor, referencesc_pkm * millionfactor)}
    #gestacktes Balkendiagramm aus DF
    km=pd.DataFrame(data,index=names)
    km.plot(kind="bar",stacked=False,figsize=(10,8), ylabel="vehicle km and pkm in millions", rot=0)

    plt.title("km compariosn")
    plt.legend(loc="upper right",bbox_to_anchor=(1, 1.15))
    plt.yticks([drtsc_km * millionfactor, drtsc_pkm * millionfactor, referencesc_km * millionfactor, referencesc_pkm * millionfactor])
    fig2 = plt.gcf()
    fig2.savefig(os.path.join(imagefolder, 'km and pkm_comparison.png'), dpi=300)
    # plt.show()

    # ------------------- total GHG comparison -------------------- #

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
    df.plot(kind="bar",stacked=True,figsize=(10,8), ylabel="in million tonnes $C0_{2}$ eq", rot=0)

    plt.title("GHG comparison")
    plt.legend(loc="upper right",bbox_to_anchor=(1, 1.15))
    # plt.yticks(np.arange(0, referencesc_totalco2, 1000000000))
    plt.yticks([drtsc_totalco2 * millionfactor, referencesc_totalco2 * millionfactor])
    fig3 = plt.gcf()
    fig3.savefig(os.path.join(imagefolder, 'totalco2_comparison.png'), dpi=300)
    # plt.show()

    # ------------------- CO2 per year comparison ----#------------ #

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

    years = []

    drt_co2values = []
    drt_km = []
    drt_pkm = []

    reference_co2values = []
    reference_km = []
    reference_pkm = []

    billion_factor = 1 / 1000000000

    for x in range(0,int(getfromconfig('vehicle_parameters', 'timespan_in_years')),1):
        drt_co2values.append((drtsc_production + (drtsc_co2year * x)) * millionfactor)
        years.append(x)

        reference_co2values.append((referencesc_production + (referencesc_co2year * x)) * millionfactor)

        drt_km.append(drtsc_kmperyear * x * billion_factor)
        reference_km.append(referencesc_kmperyear * x * billion_factor)

        drt_pkm.append(drtsc_pkmperyear * x * billion_factor)
        reference_pkm.append(referencesc_pkmperyear * x * billion_factor)


    ax1.grid(visible=True)
    ax1.set_title("GHG [$C0_{2}$ eq]", style)
    ax1.plot(years, drt_co2values, label="DRT", color="green")
    ax1.plot(years, reference_co2values, label="reference", color="black")
    ax1.set_ylabel("GHG in million tonnes $C0_{2}$ eq", fontsize=17)
    ax1.tick_params(axis='both', labelsize = 17)
    ax1.legend(loc="lower left",bbox_to_anchor=(0.8, 0), fontsize=17)
    ax1.set_xticks(np.arange(0, max(years)+1, 1))
    ax1.set_yticks(np.arange(0, max(reference_co2values)+2, 2))
    ax1.set_xlim(left=0, right=max(years))
    ax1.set_ylim(bottom=0)

    # secondy = plt.twinx()a
    ax2.set_title("total km [km]", style)
    ax2.grid(visible=True)
    ax2.plot(years, drt_pkm, label="DRT", color="purple")
    ax2.plot(years, reference_pkm, label="reference", color="blue")
    ax2.legend(loc="lower left",bbox_to_anchor=(0.8, 0), fontsize=17)
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
    fig4.savefig(os.path.join(imagefolder, 'co2_peryear_comparison.png'), dpi=300)

    plt.show()
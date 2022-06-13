from configuration import *

def scale_drtscenario(vehicleinfo: dict, pct_scenario: int = 10):
    if vehicleinfo['drt_vehicleamount']:
        drt_vehicleamount = vehicleinfo['drt_vehicleamount']
        drt_avg_totalkm_region = vehicleinfo['drt_avg_totalkm_region']
        drt_avg_totalpkm = vehicleinfo['drt_avg_totalpkm']
        drt_avg_intown_pct = vehicleinfo['drt_avg_intown_pct']
        drt_avg_countryroad_pct = vehicleinfo['drt_avg_countryroad_pct']
        drt_avg_highway_pct = vehicleinfo['drt_avg_highway_pct']
        drt_avg_speed = vehicleinfo['drt_avg_speed_pervehicle']
        drt_avg_speed_pct = vehicleinfo['drt_avg_speed_pct']
        drt_avg_passenger = vehicleinfo['drt_avg_passenger_amount']
        drt_avg_passenger_wihtout_empty = vehicleinfo['drt_avgpassenger_without_empty']

    vehicleamount = vehicleinfo['vehicleamount']
    avg_totalkm = vehicleinfo['avg_totalkm']
    avg_intown_pct = vehicleinfo['avg_intown_pct']
    avg_countryroad_pct = vehicleinfo['avg_countryroad_pct']
    avg_highway_pct = vehicleinfo['avg_highway_pct']
    avg_speed = vehicleinfo['avg_speed_pervehicle']
    avg_speed_pct = vehicleinfo['avg_speed_pct']

    if vehicleinfo['drt_vehicleamount']:
        # upscaling factors where x is 0.1 for 10%
        # Berlin
        # x^−0.637 (R2 = 0.9954)
        # x^−0.662 (R2 = 0.9975) 
        # x^−0.928 (R2 = 0.9999)
        scalingfactor_vehicles = ((pct_scenario/100)**(-0.637))                     # = 4,335
        scalingfactor_km = ((pct_scenario/100)**(-0.928))                           # = 8,472
        scalingfactor_km_pervehicle = scalingfactor_km / scalingfactor_vehicles     # = 1,954

        drt_vehicleamount_scaled = drt_vehicleamount * scalingfactor_vehicles

        drt_vehiclesize = getfromconfig('vehicle_parameters', 'drt_vehiclesize')
        if int(drt_vehiclesize) == 2:
            drt_size = "small"
        elif int(drt_vehiclesize) == 4:
            drt_size = "medium"
        elif int(drt_vehiclesize) == 7:
            drt_size = "large"
        charging = getfromconfig('vehicle_parameters', 'charging')
        years = int(getfromconfig('vehicle_parameters', 'timespan_in_years'))
        battery_lifetime = int(getfromconfig('vehicle_parameters', 'battery_exchange_after_km'))

    #calculating the amount of days for the timespan
    weeksinyear = 52.14
    workdays = weeksinyear * 5        # Mo-Fr
    weekenddays = weeksinyear * 2     # Sa-So
    weekendfactor = 77.5 / 88.2       # = 0.85      http://www.mobilitaet-in-deutschland.de/pdf/MiD2017_Ergebnisbericht.pdf

    if vehicleinfo['drt_vehicleamount']:
        consumption_type = "consumption_" + drt_size
        if charging == "opportunity":
            consumption_type = consumption_type + "_opportunity"

        drt_consumption_100km = int(getfromvehicleconfig('energy_consumption', consumption_type))

    # consunption factor based on speed and road percentages
    # factors need to be adjusted, maybe put into config
    highwaypct_factor = 1.3
    countryroad_factor = 1
    intown_factor = 1.15

    if vehicleinfo['drt_vehicleamount']:
        if drt_avg_speed_pct < .5:
            drt_speed_pct_factor = 1.2
        elif drt_avg_speed_pct >= .5 and drt_avg_speed_pct < .7:
            drt_speed_factor = 1.1
        elif drt_avg_speed_pct >= .7 and drt_avg_speed_pct < .9:
            drt_speed_factor = 1.05
        else:
            drt_speed_factor = 1

        drt_totalroad_factor = (drt_avg_intown_pct * intown_factor) + (drt_avg_countryroad_pct * countryroad_factor) + (drt_avg_highway_pct * highwaypct_factor)
        drt_consumption_km = (drt_consumption_100km * drt_speed_factor * drt_totalroad_factor) / 100

        m_to_km = 1000
        # per year
        drt_km_year_vehicle = ((workdays * drt_avg_totalkm_region) + (weekenddays * 0.85 * drt_avg_totalkm_region)) / m_to_km
        drt_km_year_vehicle_scaled = (drt_km_year_vehicle * scalingfactor_km_pervehicle)
        drt_km_year_fleet = (drt_km_year_vehicle * drt_vehicleamount)
        
        # -- for further use --- #
        drt_km_year_fleet_scaled = (drt_km_year_fleet * scalingfactor_km_pervehicle * scalingfactor_vehicles)
        drt_consumption_year_fleet = drt_km_year_fleet_scaled * drt_consumption_km
        
        # for lifespan
        drt_km_lifespan_vehicle = (drt_km_year_vehicle * years)
        drt_km_lifespan_vehicle_scaled = (drt_km_lifespan_vehicle * scalingfactor_km_pervehicle)
        drt_km_lifespan_fleet = (drt_km_lifespan_vehicle * drt_vehicleamount)

        # -- for further use --- #
        drt_km_lifespan_fleet_scaled = (drt_km_lifespan_fleet * scalingfactor_km_pervehicle * scalingfactor_vehicles)
        drt_consumption_lifespan_fleet = drt_km_lifespan_fleet_scaled * drt_consumption_km

        drt_add_batteries_lifespan_vehicle = (drt_km_lifespan_vehicle_scaled/battery_lifetime) -1   # -1 due to one battery already beeing included in production
        if int(drt_add_batteries_lifespan_vehicle) < drt_add_batteries_lifespan_vehicle:
            drt_add_batteries_lifespan_vehicle += 1
        drt_add_batteries_lifespan_vehicle = int(drt_add_batteries_lifespan_vehicle)

        drt_add_batteries_lifespan_fleet = drt_add_batteries_lifespan_vehicle * drt_vehicleamount_scaled

        print("test")
    


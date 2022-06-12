

def scale_scenario(vehicleinfo, path):

    vehicleamount = vehicleinfo['vehicleamount']
    avg_totalkm_region = vehicleinfo['avg_totalkm_region']
    avg_totalpkm = vehicleinfo['avg_totalpkm']
    avg_intown_pct = vehicleinfo['avg_intown_pct']
    avg_countryroad_pct = vehicleinfo['avg_countryroad_pct']
    avg_highway_pct = vehicleinfo['avg_highway_pct']

    avg_speed_pervehicle = vehicleinfo['avg_speed_pervehicle']



    # upscaling factors where x is 0.1 for 10%
    # Berlin
    # x−0.637 (R2 = 0.9954)
    # x−0.662 (R2 = 0.9975) 
    # x−0.928 (R2 = 0.9999)
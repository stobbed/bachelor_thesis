import pandas as pd
import os.path
from configuration import getfromconfig, getfromvehicleconfig
import olca

class olcaclient():
    def __init__(self, path) -> None:
        # setting up IPC connection (port may have to be adjusted)
        self._client = olca.Client(8080)
        self._setup = olca.CalculationSetup()
        # set calculation type (http://greendelta.github.io/olca-schema/html/CalculationType.html)
        self._setup.calculation_type = olca.CalculationType.SIMPLE_CALCULATION
        # set impact method
        self._setup.impact_method = self._client.find(olca.ImpactMethod, 'zeroCUTS')
        self._resultspath = os.path.join(path, 'results')
        self.drt_vehiclesize = int(getfromconfig('vehicle_parameters', 'drt_vehiclesize'))
        self.charging = getfromconfig('vehicle_parameters', 'charging')
        self.parameterdict = {}
        self.readparameters_from_config()
        self.redefinemultiple(self.parameterdict)

    def redefinition(self, paramatername, value):
        self._setup.parameter_redefs = []
        redef_Parameter = olca.ParameterRedef()
        redef_Parameter.name = paramatername
        redef_Parameter.value = value
        self._setup.parameter_redefs.append(redef_Parameter)

    def redefinemultiple(self, parameterdict: dict):
        self._setup.parameter_redefs = []
        for key, value in parameterdict.items():
            redef_Parameter = olca.ParameterRedef()
            redef_Parameter.name = key
            redef_Parameter.value = value
            self._setup.parameter_redefs.append(redef_Parameter)
    
    def readparameters_from_config(self):
        self.mass_electric_small = getfromvehicleconfig('mass_wo_battery','mass_electric_small')
        self.mass_electric_medium = getfromvehicleconfig('mass_wo_battery','mass_electric_medium')
        self.mass_electric_large = getfromvehicleconfig('mass_wo_battery','mass_electric_large')

        self.battery_small = getfromvehicleconfig('battery_size','battery_small')
        self.battery_medium = getfromvehicleconfig('battery_size','battery_medium')
        self.battery_large = getfromvehicleconfig('battery_size','battery_large')

        self.battery_small_opportunity = getfromvehicleconfig('battery_size','battery_small_opportunity')
        self.battery_medium_opportunity = getfromvehicleconfig('battery_size','battery_medium_opportunity')
        self.battery_large_opportunity = getfromvehicleconfig('battery_size','battery_large_opportunity')

        self.consumption_small = getfromvehicleconfig('energy_consumption','consumption_small')
        self.consumption_medium = getfromvehicleconfig('energy_consumption','consumption_medium')
        self.consumption_large = getfromvehicleconfig('energy_consumption','consumption_large')
        
        self.consumption_small_opportunity = getfromvehicleconfig('energy_consumption','consumption_small_opportunity')
        self.consumption_medium_opportunity = getfromvehicleconfig('energy_consumption','consumption_medium_opportunity')
        self.consumption_large_opportunity = getfromvehicleconfig('energy_consumption','consumption_large_opportunity')

        self.mass_petrol_small = getfromvehicleconfig('combustion_mass','mass_petrol_small', True)
        self.mass_petrol_medium = getfromvehicleconfig('combustion_mass','mass_petrol_medium', True)
        self.mass_petrol_large = getfromvehicleconfig('combustion_mass','mass_petrol_large', True)

        self.mass_diesel_small = getfromvehicleconfig('combustion_mass','mass_diesel_small', True)
        self.mass_diesel_medium = getfromvehicleconfig('combustion_mass','mass_diesel_medium', True)
        self.mass_diesel_large = getfromvehicleconfig('combustion_mass','mass_diesel_large', True)

        self.parameterdict['mass_electric_small_wo_battery'] = self.mass_electric_small
        self.parameterdict['mass_electric_medium_wo_battery'] = self.mass_electric_medium
        self.parameterdict['mass_electric_large_wo_battery'] = self.mass_electric_large

        self.parameterdict['battery_size_small'] = self.battery_small
        self.parameterdict['battery_size_medium'] = self.battery_medium
        self.parameterdict['battery_size_large'] = self.battery_large

        self.parameterdict['battery_size_small_opportunity'] = self.battery_small_opportunity
        self.parameterdict['battery_size_medium_opportunity'] = self.battery_medium_opportunity
        self.parameterdict['battery_size_large_opportunity'] = self.battery_large_opportunity


    def calculate_and_save(self, productname):
        productsystem = self._client.find(olca.ProductSystem, productname)
        self._setup.product_system = productsystem
        excelname = os.path.join(self._resultspath, productname + '.xlsx')
        try:
            openlca_result = self._client.calculate(self._setup)
            print("finished calculation for,", productname, "storing into Excel now")
            self._client.excel_export(openlca_result, excelname)
            self._client.dispose(openlca_result)
        except Exception as e:
            print('Berechnung hat nicht stattgefunden'+ e) 
        

    def lifecycleassessment(self, vehicles_drt, vehicles_nondrt):
        electricity_use = "electric use"
        battery_production = "battery production, Li-ion, rechargeable, prismatic | battery, Li-ion, rechargeable, prismatic | Cutoff, U"
        if not os.path.exists(os.path.join(self._resultspath, battery_production + '.xlsx')):
            self.calculate_and_save(battery_production)
        electric_production_battery_kg = pd.read_excel(os.path.join(self._resultspath, battery_production + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
        if not os.path.exists(os.path.join(self._resultspath, electricity_use + '.xlsx')):
            self.calculate_and_save(electricity_use)
        electricity_use_kWh = pd.read_excel(os.path.join(self._resultspath, electricity_use + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
        

        kWh_to_kg = 1000 / getfromvehicleconfig('battery_specs', 'energy_density', True)

        drt_batteries_kwh = 0
        batteries_kwh = 0
        drt_electric_production = 0
        electric_production = 0
        drt_electric_transport = 0
        electric_transport = 0
        drt_electric_consumption = 0
        electric_consumption = 0

        combustion_production = 0
        combustion_transport = 0
        combustion_consumption = 0

        if vehicles_drt != {}:
            for size in vehicles_drt:
                if size == 'small' or size == 'medium' or size == 'large':
                    electric_production_name = "drt production, electric, " + self.charging + ", " + size +  " size passenger car | Cutoff, U"
                    electric_transport_name = "transport only, drt, " + self.charging + ", " + size + " size, electric | Cutoff, U"
                    
                    if not os.path.exists(os.path.join(self._resultspath, electric_production_name + '.xlsx')):
                        self.calculate_and_save(electric_production_name)
                    if not os.path.exists(os.path.join(self._resultspath, electric_transport_name + '.xlsx')):
                        self.calculate_and_save(electric_transport_name)

                    electric_production_vehicle_kg = pd.read_excel(os.path.join(self._resultspath, electric_production_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
                    electric_transport_km = pd.read_excel(os.path.join(self._resultspath, electric_transport_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]

                    if size == 'small':
                        if self.charging == "opportunity":
                            drt_batteries_kwh += vehicles_drt[size]['batteries'] * self.battery_small_opportunity
                            drt_electric_production += electric_production_vehicle_kg * (self.mass_electric_small + (self.battery_small_opportunity * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                        else:
                            drt_batteries_kwh += vehicles_drt[size]['batteries'] * self.battery_small
                            drt_electric_production += electric_production_vehicle_kg * (self.mass_electric_small + (self.battery_small * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                        drt_electric_transport += electric_transport_km * vehicles_drt[size]['km']
                    elif size == 'medium':
                        if self.charging == "opportunity":
                            drt_batteries_kwh += vehicles_drt[size]['batteries'] * self.battery_medium_opportunity
                            drt_electric_production += electric_production_vehicle_kg * (self.mass_electric_medium + (self.battery_medium_opportunity * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                        else:
                            drt_batteries_kwh += vehicles_drt[size]['batteries'] * self.battery_medium
                            drt_electric_production += electric_production_vehicle_kg * (self.mass_electric_medium + (self.battery_medium * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                        drt_electric_transport += electric_transport_km * vehicles_drt[size]['km']
                    elif size == 'large':
                        if self.charging == "opportunity":
                            drt_batteries_kwh += vehicles_drt[size]['batteries'] * self.battery_large_opportunity
                            drt_electric_production += electric_production_vehicle_kg * (self.mass_electric_large + (self.battery_large_opportunity * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                        else:
                            drt_batteries_kwh += vehicles_drt[size]['batteries'] * self.battery_large
                            drt_electric_production += electric_production_vehicle_kg * (self.mass_electric_large + (self.battery_large * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                        drt_electric_transport += electric_transport_km * vehicles_drt[size]['km']
            
            drt_electric_production_batteries = (drt_batteries_kwh * kWh_to_kg) * electric_production_battery_kg
            drt_electric_consumption = vehicles_drt['consumption'] * electricity_use_kWh

        if vehicles_nondrt != {}:
            for fuel in vehicles_nondrt:
                for size in fuel:
                    if fuel == 'electric':
                        if size == 'small' or size == 'medium' or size == 'large':
                            electric_production_name = "drt production, electric, " + self.charging + ", " + size +  " size passenger car | Cutoff, U"
                            electric_transport_name = "transport only, drt, " + self.charging + ", " + size + " size, electric | Cutoff, U"

                            if not os.path.exists(os.path.join(self._resultspath, electric_production_name + '.xlsx')):
                                self.calculate_and_save(electric_production_name)
                            if not os.path.exists(os.path.join(self._resultspath, electric_transport_name + '.xlsx')):
                                self.calculate_and_save(electric_transport_name)

                            electric_production_vehicle_kg = pd.read_excel(os.path.join(self._resultspath, electric_production_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
                            electric_production_battery_kg = pd.read_excel(os.path.join(self._resultspath, battery_production + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
                            electric_transport_km = pd.read_excel(os.path.join(self._resultspath, electric_transport_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]

                            if size == 'small':
                                if self.charging == "opportunity":
                                    batteries_kwh += vehicles_nondrt[size]['batteries'] * self.battery_small_opportunity
                                    electric_production += electric_production_vehicle_kg * (self.mass_electric_small + (self.battery_small_opportunity * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                                else:
                                    batteries_kwh += vehicles_nondrt[size]['batteries'] * self.battery_small
                                    electric_production += electric_production_vehicle_kg * (self.mass_electric_small + (self.battery_small * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                                electric_transport += electric_transport_km * vehicles_nondrt[size]['km']
                            elif size == 'medium':
                                if self.charging == "opportunity":
                                    batteries_kwh += vehicles_nondrt[size]['batteries'] * self.battery_medium_opportunity
                                    electric_production += electric_production_vehicle_kg * (self.mass_electric_medium + (self.battery_medium_opportunity * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                                else:
                                    batteries_kwh += vehicles_nondrt[size]['batteries'] * self.battery_medium
                                    electric_production += electric_production_vehicle_kg * (self.mass_electric_medium + (self.battery_medium * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                                electric_transport += electric_transport_km * vehicles_nondrt[size]['km']
                            elif size == 'large':
                                if self.charging == "opportunity":
                                    batteries_kwh += vehicles_nondrt[size]['batteries'] * self.battery_large_opportunity
                                    electric_production += electric_production_vehicle_kg * (self.mass_electric_large + (self.battery_large_opportunity * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                                else:
                                    batteries_kwh += vehicles_nondrt[size]['batteries'] * self.battery_large
                                    electric_production += electric_production_vehicle_kg * (self.mass_electric_large + (self.battery_large * kWh_to_kg)) * vehicles_nondrt[size]['amount']
                                electric_transport += electric_transport_km * vehicles_nondrt[size]['km']
                    
                    else:
                        if size == 'small' or size == 'medium' or size == 'large':
                            nondrt_production_name = "passenger car production, " + fuel + ", " + size +  " size passenger car | Cutoff, U"
                            nondrt_transport_name = "transport only, passenger car, " + size + " size, electric | Cutoff, U"
                            fuel_name = fuel + " use"

                            if not os.path.exists(os.path.join(self._resultspath, electric_production_name + '.xlsx')):
                                self.calculate_and_save(electric_production_name)
                            if not os.path.exists(os.path.join(self._resultspath, electric_transport_name + '.xlsx')):
                                self.calculate_and_save(electric_transport_name)
                            if not os.path.exists(os.path.join(self._resultspath, fuel_name + '.xlsx')):
                                self.calculate_and_save(fuel_name)

                            production_vehicle_kg = pd.read_excel(os.path.join(self._resultspath, nondrt_production_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
                            transport_km = pd.read_excel(os.path.join(self._resultspath, electric_transport_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
                            

                            if size == 'small':
                                combustion_production += production_vehicle_kg * self.mass_electric_small * vehicles_nondrt[size]['amount']
                                combustion_transport += transport_km * vehicles_nondrt[size]['km']
                            elif size == 'medium':
                                combustion_production += production_vehicle_kg * self.mass_electric_medium * vehicles_nondrt[size]['amount']
                                combustion_transport += transport_km * vehicles_nondrt[size]['km']
                            elif size == 'large':
                                combustion_production += production_vehicle_kg * self.mass_electric_large * vehicles_nondrt[size]['amount']
                                combustion_transport += transport_km * vehicles_nondrt[size]['km']
                        
                combustion_consumption = vehicles_
            electric_consumption = vehicles_nondrt['consumption'] * electricity_use_kWh
            
            


    def lifecycleassessment_reference(self):

        # set name for production product system
        production_name = "passenger car production, " + drive + ", " + size + " size passenger car | Cutoff, U"

        # set name for transport product system
        transport_name = "transport only, passenger car, " + size + " size, " + drive + " | Cutoff, U"
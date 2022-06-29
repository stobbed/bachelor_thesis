import pandas as pd
import os.path
import xlsxwriter

from configuration import getfromconfig, getfromvehicleconfig
import olca

import warnings
warnings.simplefilter("ignore")

class olcaclient():
    def __init__(self) -> None:
        """ opens the connection to the OLCA client and also reads gridmix and charging strategy from config """

        # setting up IPC connection (port may have to be adjusted)
        self._client = olca.Client(8080)
        self._setup = olca.CalculationSetup()
        # set calculation type (http://greendelta.github.io/olca-schema/html/CalculationType.html)
        self._setup.calculation_type = olca.CalculationType.SIMPLE_CALCULATION
        # set impact method
        self._setup.impact_method = self._client.find(olca.ImpactMethod, 'zeroCUTS')
        if not os.path.exists('lca'):
            os.mkdir('lca')
        self._resultspath = 'lca'
        self.gridmix = getfromconfig('vehicle_parameters', 'energymix')
        self.charging = getfromconfig('vehicle_parameters', 'charging')
        self.parameterdict = {}
        self.readparameters_from_config()
        self.redefinemultiple(self.parameterdict)

    def redefinition(self, paramatername, value):
        """ redefines parameters, by adding it to the olca.parameterredef object """

        self._setup.parameter_redefs = []
        redef_Parameter = olca.ParameterRedef()
        redef_Parameter.name = paramatername
        redef_Parameter.value = value
        self._setup.parameter_redefs.append(redef_Parameter)

    def redefinemultiple(self, parameterdict: dict):
        """ redefines multiple parameters contained in the parameterdict dictionary by adding it to the olca.parameterredef object """
        
        self._setup.parameter_redefs = []
        for key, value in parameterdict.items():
            redef_Parameter = olca.ParameterRedef()
            redef_Parameter.name = key
            redef_Parameter.value = value
            self._setup.parameter_redefs.append(redef_Parameter)
    
    def readparameters_from_config(self):
        """ reads (adjusted) paramters from vehicle.ini and stores them in the redefinition dict to redefine the parameters inside OLCA """
        self.mass_electric_small = float(getfromvehicleconfig('mass_wo_battery','mass_electric_small'))
        self.mass_electric_medium = float(getfromvehicleconfig('mass_wo_battery','mass_electric_medium'))
        self.mass_electric_large = float(getfromvehicleconfig('mass_wo_battery','mass_electric_large'))

        self.battery_small = float(getfromvehicleconfig('battery_size','battery_small'))
        self.battery_medium = float(getfromvehicleconfig('battery_size','battery_medium'))
        self.battery_large = float(getfromvehicleconfig('battery_size','battery_large'))

        self.battery_small_opportunity = float(getfromvehicleconfig('battery_size','battery_small_opportunity'))
        self.battery_medium_opportunity = float(getfromvehicleconfig('battery_size','battery_medium_opportunity'))
        self.battery_large_opportunity = float(getfromvehicleconfig('battery_size','battery_large_opportunity'))

        self.consumption_small = float(getfromvehicleconfig('energy_consumption','consumption_small'))
        self.consumption_medium = float(getfromvehicleconfig('energy_consumption','consumption_medium'))
        self.consumption_large = float(getfromvehicleconfig('energy_consumption','consumption_large'))
        
        self.consumption_small_opportunity = float(getfromvehicleconfig('energy_consumption','consumption_small_opportunity'))
        self.consumption_medium_opportunity = float(getfromvehicleconfig('energy_consumption','consumption_medium_opportunity'))
        self.consumption_large_opportunity = float(getfromvehicleconfig('energy_consumption','consumption_large_opportunity'))

        self.mass_petrol_small = float(getfromvehicleconfig('combustion_mass','mass_petrol_small', True))
        self.mass_petrol_medium = float(getfromvehicleconfig('combustion_mass','mass_petrol_medium', True))
        self.mass_petrol_large = float(getfromvehicleconfig('combustion_mass','mass_petrol_large', True))

        self.mass_diesel_small = float(getfromvehicleconfig('combustion_mass','mass_diesel_small', True))
        self.mass_diesel_medium = float(getfromvehicleconfig('combustion_mass','mass_diesel_medium', True))
        self.mass_diesel_large = float(getfromvehicleconfig('combustion_mass','mass_diesel_large', True))

        # storing inside dictionary for redefinition purposes
        self.parameterdict['mass_electric_small_wo_battery'] = self.mass_electric_small
        self.parameterdict['mass_electric_medium_wo_battery'] = self.mass_electric_medium
        self.parameterdict['mass_electric_large_wo_battery'] = self.mass_electric_large

        self.parameterdict['battery_size_small'] = self.battery_small
        self.parameterdict['battery_size_medium'] = self.battery_medium
        self.parameterdict['battery_size_large'] = self.battery_large

        self.parameterdict['battery_size_small_opportunity'] = self.battery_small_opportunity
        self.parameterdict['battery_size_medium_opportunity'] = self.battery_medium_opportunity
        self.parameterdict['battery_size_large_opportunity'] = self.battery_large_opportunity


    def calculate_and_save(self, productname: str):
        """ calculating the in the input productname specified productsystem and saving its results in an excel file """
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
        

    def lifecycleassessment(self, vehicles_drt: dict, vehicles_nondrt: dict, simulationname: str):
        """ creates the lifecycle asssessment for one scenario when given the vehicles drt and vehicles non drt file after scaling """
        
        electricity_use = "electric use"
        battery_production = "battery production, Li-ion, rechargeable, prismatic | battery, Li-ion, rechargeable, prismatic | Cutoff, U"
        
        if not os.path.exists(os.path.join(self._resultspath, battery_production + '.xlsx')):
            self.calculate_and_save(battery_production)
        electric_production_battery_kg = pd.read_excel(os.path.join(self._resultspath, battery_production + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
        if not os.path.exists(os.path.join(self._resultspath, electricity_use + '.xlsx')):
            self.calculate_and_save(electricity_use)
        electricity_use_kWh = pd.read_excel(os.path.join(self._resultspath, electricity_use + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
        
        # converison factor for battery capacity to battery weight
        kWh_to_kg = 1000 / int(getfromvehicleconfig('battery_specs', 'energy_density', True))

        totaldrivenkm = 0
        totaldrivenpkm = 0
        drt_batteries_kwh = 0
        batteries_kwh = 0
        drt_electric_production_vehicle = 0
        drt_electric_production_batteries = 0
        electric_production_vehicle = 0
        drt_electric_transport = 0
        electric_transport = 0
        drt_electric_consumption = 0
        electric_consumption = 0

        combustion_production = 0
        combustion_transport = 0
        combustion_consumption = 0
        combustion_emissions = 0

        # conversion factor for combustion fuels to weight
        petrol_combined_density = ((0.9478 * 747.5) + ((1-0.9478) * 782))       # nach Florian Heining
        diesel_combined_density = ((0.9085 * 832.5) + ((1-0.9085) * 879))

        # if there are any DRT vehicles in the scenario this condition is true and the following is executed
        if vehicles_drt != {}:
            totaldrivenkm += vehicles_drt['totalkm']
            totaldrivenpkm += vehicles_drt['totalpkm']
            # loops through dictionary since the information is stored for each size in the dictionary
            for size, vehiclesize in vehicles_drt.items():
                if size == 'small' or size == 'medium' or size == 'large':
                    electric_production_name = "drt production, electric, " + self.charging + ", " + size +  " size passenger car | Cutoff, U"
                    electric_transport_name = "transport only, drt, " + self.charging + ", " + size + " size, electric | Cutoff, U"
                    
                    # Excel Dateien müssen überschrieben werden, da Parameter über Vehicle.ini Datei überarbeitet werden können und sonst nicht anständig
                    # berücksichtigt werden!

                    if not os.path.exists(os.path.join(self._resultspath, electric_production_name + '.xlsx')):
                        self.calculate_and_save(electric_production_name)
                    if not os.path.exists(os.path.join(self._resultspath, electric_transport_name + '.xlsx')):
                        self.calculate_and_save(electric_transport_name)

                    electric_production_vehicle_kg = pd.read_excel(os.path.join(self._resultspath, electric_production_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
                    electric_transport_km = pd.read_excel(os.path.join(self._resultspath, electric_transport_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]

                    if size == 'small':
                        if self.charging == "opportunity":
                            drt_batteries_kwh += vehiclesize['batteries'] * self.battery_small_opportunity
                            drt_electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_small + (self.battery_small_opportunity * kWh_to_kg)) * vehiclesize['amount']
                        else:
                            drt_batteries_kwh += vehiclesize['batteries'] * self.battery_small
                            drt_electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_small + (self.battery_small * kWh_to_kg)) * vehiclesize['amount']
                        drt_electric_transport += electric_transport_km * vehiclesize['km']
                    elif size == 'medium':
                        if self.charging == "opportunity":
                            drt_batteries_kwh += vehiclesize['batteries'] * self.battery_medium_opportunity
                            drt_electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_medium + (self.battery_medium_opportunity * kWh_to_kg)) * vehiclesize['amount']
                        else:
                            drt_batteries_kwh += vehiclesize['batteries'] * self.battery_medium
                            drt_electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_medium + (self.battery_medium * kWh_to_kg)) * vehiclesize['amount']
                        drt_electric_transport += electric_transport_km * vehiclesize['km']
                    elif size == 'large':
                        if self.charging == "opportunity":
                            drt_batteries_kwh += vehiclesize['batteries'] * self.battery_large_opportunity
                            drt_electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_large + (self.battery_large_opportunity * kWh_to_kg)) * vehiclesize['amount']
                        else:
                            drt_batteries_kwh += vehiclesize['batteries'] * self.battery_large
                            drt_electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_large + (self.battery_large * kWh_to_kg)) * vehiclesize['amount']
                        drt_electric_transport += electric_transport_km * vehiclesize['km']
            
            # emissions
            drt_electric_production_batteries = (drt_batteries_kwh * kWh_to_kg) * electric_production_battery_kg
            drt_electric_consumption = vehicles_drt['consumption'] * electricity_use_kWh

        # if there are any DRT vehicles in the scenario this condition is true and the following is executed
        if vehicles_nondrt != {}:
            totaldrivenkm += vehicles_nondrt['totalkm']
            totaldrivenpkm += vehicles_nondrt['totalpkm']
            # vehicle contains fuels as the first level
            for fuel, vehiclesizes in vehicles_nondrt.items():
                if fuel == 'electric':
                    # the second level is again size 
                    for size, vehiclesize in vehiclesizes.items():
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
                                # if self.charging == "opportunity":
                                #     batteries_kwh += vehiclesize['batteries'] * self.battery_small_opportunity
                                #     electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_small + (self.battery_small_opportunity * kWh_to_kg)) * vehiclesize['amount']
                                batteries_kwh += vehiclesize['batteries'] * self.battery_small
                                electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_small + (self.battery_small * kWh_to_kg)) * vehiclesize['amount']
                            elif size == 'medium':
                                # if self.charging == "opportunity":
                                #     batteries_kwh += vehiclesize['batteries'] * self.battery_medium_opportunity
                                #     electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_medium + (self.battery_medium_opportunity * kWh_to_kg)) * vehiclesize['amount']
                                batteries_kwh += vehiclesize['batteries'] * self.battery_medium
                                electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_medium + (self.battery_medium * kWh_to_kg)) * vehiclesize['amount']
                            elif size == 'large':
                                # if self.charging == "opportunity":
                                #     batteries_kwh += vehiclesize['batteries'] * self.battery_large_opportunity
                                #     electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_large + (self.battery_large_opportunity * kWh_to_kg)) * vehiclesize['amount']
                                batteries_kwh += vehiclesize['batteries'] * self.battery_large
                                electric_production_vehicle += electric_production_vehicle_kg * (self.mass_electric_large + (self.battery_large * kWh_to_kg)) * vehiclesize['amount']
                            
                            electric_transport += electric_transport_km * vehiclesize['km']
                    
                elif fuel == 'petrol' or fuel == 'diesel':
                    for size, vehiclesize in vehiclesizes.items():
                        if size == 'small' or size == 'medium' or size == 'large':
                            nondrt_production_name = "passenger car production, " + fuel + ", " + size +  " size passenger car | Cutoff, U"
                            nondrt_transport_name = "transport only, passenger car, " + size + " size, " + fuel + " | Cutoff, U"

                            if not os.path.exists(os.path.join(self._resultspath, nondrt_production_name + '.xlsx')):
                                self.calculate_and_save(nondrt_production_name)
                            if not os.path.exists(os.path.join(self._resultspath, nondrt_transport_name + '.xlsx')):
                                self.calculate_and_save(nondrt_transport_name)

                            production_vehicle_kg = pd.read_excel(os.path.join(self._resultspath, nondrt_production_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
                            transport_km = pd.read_excel(os.path.join(self._resultspath, nondrt_transport_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]

                            if size == 'small':
                                combustion_production += production_vehicle_kg * self.mass_electric_small * vehiclesize['amount']
                                combustion_transport += transport_km * vehiclesize['km']
                            elif size == 'medium':
                                combustion_production += production_vehicle_kg * self.mass_electric_medium * vehiclesize['amount']
                                combustion_transport += transport_km * vehiclesize['km']
                            elif size == 'large':
                                combustion_production += production_vehicle_kg * self.mass_electric_large * vehiclesize['amount']
                                combustion_transport += transport_km * vehiclesize['km']
                    if fuel == "petrol":
                        fuel_name = fuel + " use"
                        if not os.path.exists(os.path.join(self._resultspath, fuel_name + '.xlsx')):
                            self.calculate_and_save(fuel_name)
                        fuel_use = pd.read_excel(os.path.join(self._resultspath, fuel_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
                        combustion_emissions += vehiclesizes['consumption'] * (petrol_combined_density / 1000) * fuel_use
                    if fuel == "diesel":
                        fuel_name = fuel + " use"
                        if not os.path.exists(os.path.join(self._resultspath, fuel_name + '.xlsx')):
                            self.calculate_and_save(fuel_name)
                        fuel_use = pd.read_excel(os.path.join(self._resultspath, fuel_name + '.xlsx'), skiprows=3, nrows=1, sheet_name="Impacts", usecols="E", header=None, names=["Nutzung"]).iloc[0]["Nutzung"]
                        combustion_emissions += vehiclesizes['consumption'] * (diesel_combined_density / 1000) * fuel_use
                        
            electric_production_batteries = (batteries_kwh * kWh_to_kg) * electric_production_battery_kg
            electric_consumption = vehicles_nondrt['electric']['consumption'] * electricity_use_kWh
            
        totalemissions_production = drt_electric_production_vehicle + electric_production_vehicle + combustion_production
        totalemissions_transport = drt_electric_transport + electric_transport + combustion_transport
        totalemissions_batteries = drt_electric_production_batteries + electric_production_batteries
        totalemissions_use = drt_electric_consumption + electric_consumption + combustion_emissions

        totalemissions = totalemissions_production + totalemissions_transport + totalemissions_use + totalemissions_batteries

        # -------------------------------------- results creation ------------------------------------------ #

        # create excel results file
        if not os.path.exists(os.path.join(self._resultspath, str(simulationname))):
            os.mkdir(os.path.join(self._resultspath, str(simulationname)))
        workbook = xlsxwriter.Workbook(os.path.join(self._resultspath, str(simulationname), "results_" + str(simulationname) + ".xlsx"))

        kgtotonnes = 1/1000
        years = int(getfromconfig("vehicle_parameters", "timespan_in_years"))

        worksheet_tot = workbook.add_worksheet(name = "LCA_results_total")

        worksheet_tot.write(1, 0, "total CO2 emissions [t CO2-Eq]")
        worksheet_tot.write(1, 1, totalemissions * kgtotonnes)

        worksheet_tot.write(3, 0, "total emissions, production [t CO2-Eq]")
        worksheet_tot.write(3, 1, totalemissions_production * kgtotonnes)

        worksheet_tot.write(4, 0, "total emissions, batteries [t CO2-Eq]")
        worksheet_tot.write(4, 1, totalemissions_batteries * kgtotonnes)

        worksheet_tot.write(5, 0, "total emissions, transport [t CO2-Eq]")
        worksheet_tot.write(5, 1, totalemissions_transport * kgtotonnes)

        worksheet_tot.write(6, 0, "total emissions, use phase [t CO2-Eq]")
        worksheet_tot.write(6, 1, totalemissions_use * kgtotonnes)


        worksheet_tot.write(8, 0, "emissions per year, total wo production [t CO2-Eq]")
        worksheet_tot.write(8, 1, ((totalemissions - totalemissions_production) * kgtotonnes) / years)

        worksheet_tot.write(9, 0, "emissions per year, batteries [t CO2-Eq]")
        worksheet_tot.write(9, 1, (totalemissions_batteries * kgtotonnes) / years)

        worksheet_tot.write(10, 0, "emissions per year, transport [t CO2-Eq]")
        worksheet_tot.write(10, 1, (totalemissions_transport * kgtotonnes) / years)

        worksheet_tot.write(11, 0, "emissions per year, use phase [t CO2-Eq]")
        worksheet_tot.write(11, 1, (totalemissions_use * kgtotonnes) / years)


        worksheet_tot.write(13, 0, "emissions per averaged km, total wo production [g CO2-Eq]")
        worksheet_tot.write(13, 1, ((totalemissions - totalemissions_production) / kgtotonnes) / (years * totaldrivenkm))

        worksheet_tot.write(14, 0, "emissions per averaged km, batteries [g CO2-Eq]")
        worksheet_tot.write(14, 1, (totalemissions_batteries / kgtotonnes) / (years * totaldrivenkm))

        worksheet_tot.write(15, 0, "emissions per averaged km, transport [g CO2-Eq]")
        worksheet_tot.write(15, 1, (totalemissions_transport / kgtotonnes) / (years * totaldrivenkm))

        worksheet_tot.write(16, 0, "emissions per averaged km, use phase [g CO2-Eq]")
        worksheet_tot.write(16, 1, (totalemissions_use / kgtotonnes) / (years * totaldrivenkm))


        worksheet_tot.write(18, 0, "emissions per averaged pkm, total wo production [g CO2-Eq]")
        worksheet_tot.write(18, 1, ((totalemissions - totalemissions_production) / kgtotonnes) / (years * totaldrivenpkm))

        worksheet_tot.write(19, 0, "emissions per averaged pkm, batteries [g CO2-Eq]")
        worksheet_tot.write(19, 1, (totalemissions_batteries / kgtotonnes) / (years * totaldrivenpkm))

        worksheet_tot.write(20, 0, "emissions per averaged pkm, transport [g CO2-Eq]")
        worksheet_tot.write(20, 1, (totalemissions_transport / kgtotonnes) / (years * totaldrivenpkm))

        worksheet_tot.write(21, 0, "emissions per averaged pkm, use phase [g CO2-Eq]")
        worksheet_tot.write(21, 1, (totalemissions_use / kgtotonnes) / (years * totaldrivenpkm))

        width= len("emissions per averaged pkm, batteries [t CO2-Eq]")
        worksheet_tot.set_column(0,0, width)


        worksheet_drt = workbook.add_worksheet(name= "LCA_results_DRT")

        worksheet_drt.write(1, 0, "total CO2 emissions [t CO2-Eq]")
        worksheet_drt.write(1, 1, (drt_electric_production_vehicle + drt_electric_production_batteries + drt_electric_transport + drt_electric_consumption) * kgtotonnes)

        worksheet_drt.write(3, 0, "total emissions, production [t CO2-Eq]")
        worksheet_drt.write(3, 1, drt_electric_production_vehicle * kgtotonnes)

        worksheet_drt.write(4, 0, "total emissions, batteries [t CO2-Eq]")
        worksheet_drt.write(4, 1, drt_electric_production_batteries * kgtotonnes)

        worksheet_drt.write(5, 0, "total emissions, transport [t CO2-Eq]")
        worksheet_drt.write(5, 1, drt_electric_transport * kgtotonnes)

        worksheet_drt.write(6, 0, "total emissions, use [t CO2-Eq]")
        worksheet_drt.write(6, 1, drt_electric_consumption * kgtotonnes)

        worksheet_drt.set_column(0,0, width)


        worksheet_nondrt = workbook.add_worksheet(name= "LCA_results_non_DRT")

        worksheet_nondrt.write(1, 0, "total CO2 emissions [t CO2-Eq]")
        worksheet_nondrt.write(1, 1, ((electric_production_vehicle + combustion_production) + electric_production_batteries + (electric_transport + combustion_transport) + (electric_consumption + combustion_emissions)) * kgtotonnes)

        worksheet_nondrt.write(3, 0, "total emissions, production [t CO2-Eq]")
        worksheet_nondrt.write(3, 1, ((electric_production_vehicle + combustion_production) * kgtotonnes))

        worksheet_nondrt.write(4, 0, "total emissions, batteries [t CO2-Eq]")
        worksheet_nondrt.write(4, 1, electric_production_batteries * kgtotonnes)

        worksheet_nondrt.write(5, 0, "total emissions, transport [t CO2-Eq]")
        worksheet_nondrt.write(5, 1, ((electric_transport + combustion_transport) * kgtotonnes))

        worksheet_nondrt.write(6, 0, "total emissions, use [t CO2-Eq]")
        worksheet_nondrt.write(6, 1, ((electric_consumption + combustion_emissions) * kgtotonnes))

        worksheet_nondrt.set_column(0,0, width)

        worksheet_infos = workbook.add_worksheet(name = "vehicle_infos")

        if vehicles_drt != {}:
            worksheet_infos.write(1, 0, "totalkm [km]")
            worksheet_infos.write(1, 1, vehicles_drt['totalkm'] + vehicles_nondrt['totalkm'])

            worksheet_infos.write(2, 0, "totalkm_drt [km]")
            worksheet_infos.write(2, 1, vehicles_drt['totalkm'])

            worksheet_infos.write(3, 0, "totalkm_nondrt [km]")
            worksheet_infos.write(3, 1, vehicles_nondrt['totalkm'])


            worksheet_infos.write(5, 0, "totalpkm [km]")
            worksheet_infos.write(5, 1, vehicles_drt['totalpkm'] + vehicles_nondrt['totalpkm'])

            worksheet_infos.write(6, 0, "totalpkm_drt [km]")
            worksheet_infos.write(6, 1, vehicles_drt['totalpkm'])

            worksheet_infos.write(7, 0, "totalpkm_nondrt [km]")
            worksheet_infos.write(7, 1, vehicles_nondrt['totalpkm'])


            worksheet_infos.write(9, 0, "number_vehicles_drt [1]")
            worksheet_infos.write(9, 1, vehicles_drt['total_vehicles'])

            if vehicles_drt.get('small') != None:
                small_vehicles = vehicles_drt.get('small').get('amount')
            else:
                small_vehicles = 0
            if vehicles_drt.get('medium') != None:
                medium_vehicles = vehicles_drt.get('medium').get('amount')
            else:
                medium_vehicles = 0
            if vehicles_drt.get('large') != None:
                large_vehicles = vehicles_drt.get('large').get('amount')
            else:
                large_vehicles = 0

            worksheet_infos.write(10, 0, "number_small_vehicles_drt [1]")
            worksheet_infos.write(10, 1, small_vehicles)
            worksheet_infos.write(11, 0, "number_medium_vehicles_drt [1]")
            worksheet_infos.write(11, 1, medium_vehicles)
            worksheet_infos.write(12, 0, "number_large_vehicles_drt [1]")
            worksheet_infos.write(12, 1, large_vehicles)

            worksheet_infos.write(13, 0, "number_vehicles_nondrt [1]")
            worksheet_infos.write(13, 1, vehicles_nondrt['total_vehicles'])

            worksheet_infos.write(15, 0, "avg_speed_drt [km/h]")
            worksheet_infos.write(15, 1, vehicles_drt['avg_speed'])

            worksheet_infos.write(16, 0, "avg_speed_nondrt [km/h]")
            worksheet_infos.write(16, 1, vehicles_nondrt['avg_speed'])

            worksheet_infos.write(18, 0, "speed_pct_drt [1]")
            worksheet_infos.write(18, 1, vehicles_drt['speed_pct'])

            worksheet_infos.write(19, 0, "speed_pct_nondrt [1]")
            worksheet_infos.write(19, 1, vehicles_nondrt['speed_pct'])

            worksheet_infos.write(21, 0, "total_batteries_drt [1]")
            worksheet_infos.write(21, 1, vehicles_drt['total_batteries'])

            worksheet_infos.write(23, 0, "avg_passengers_drt [1]")
            worksheet_infos.write(23, 1, vehicles_drt['avg_passengers'])

            worksheet_infos.write(25, 0, "km_peryear_fleet_drt [km]")
            worksheet_infos.write(25, 1, vehicles_drt['totalkm'] / years)

            worksheet_infos.write(26, 0, "km_peryear_fleet_nondrt [km]")
            worksheet_infos.write(26, 1, vehicles_nondrt['totalkm'] / years)

            worksheet_infos.write(28, 0, "pkm_peryear_fleet_drt [km]")
            worksheet_infos.write(28, 1, vehicles_drt['totalpkm'] / years)

            worksheet_infos.write(29, 0, "pkm_peryear_fleet_nondrt [km]")
            worksheet_infos.write(29, 1, vehicles_nondrt['totalpkm'] / years)

            worksheet_infos.write(31, 0, "averaged_km_per_year_per_vehicle_drt [km]")
            worksheet_infos.write(31, 1, vehicles_drt['km_per_vehicle_year'])

            worksheet_infos.write(32, 0, "averaged_km_per_year_per_vehicle_nondrt [km]")
            worksheet_infos.write(32, 1, vehicles_nondrt['km_per_vehicle_year'])

            worksheet_infos.write(34, 0, "averaged_pkm_per_year_per_vehicle_drt [km]")
            worksheet_infos.write(34, 1, vehicles_drt['pkm_per_vehicle_year'])

            worksheet_infos.write(35, 0, "averaged_pkm_per_year_per_vehicle_nondrt [km]")
            worksheet_infos.write(35, 1, vehicles_nondrt['pkm_per_vehicle_year'])

            worksheet_infos.write(37, 0, "averaged_km_per_day_per_vehicle_drt [km]")
            worksheet_infos.write(37, 1, vehicles_drt['km_per_vehicle_day'])

            worksheet_infos.write(38, 0, "averaged_km_per_day_per_vehicle_nondrt [km]")
            worksheet_infos.write(38, 1, vehicles_nondrt['km_per_vehicle_day'])

            worksheet_infos.write(40, 0, "averaged_pkm_per_day_per_vehicle_drt [km]")
            worksheet_infos.write(40, 1, vehicles_drt['pkm_per_vehicle_day'])

            worksheet_infos.write(41, 0, "averaged_pkm_per_day_per_vehicle_nondrt [km]")
            worksheet_infos.write(41, 1, vehicles_nondrt['pkm_per_vehicle_day'])

        else:
            worksheet_infos.write(1, 0, "totalkm [km]")
            worksheet_infos.write(1, 1, vehicles_nondrt['totalkm'])

            worksheet_infos.write(2, 0, "totalkm_drt [km]")
            worksheet_infos.write(2, 1, 0)

            worksheet_infos.write(3, 0, "totalkm_nondrt [km]")
            worksheet_infos.write(3, 1, vehicles_nondrt['totalkm'])

            worksheet_infos.write(5, 0, "totalpkm [km]")
            worksheet_infos.write(5, 1, vehicles_nondrt['totalpkm'])

            worksheet_infos.write(6, 0, "totalpkm_drt [km]")
            worksheet_infos.write(6, 1, 0)

            worksheet_infos.write(7, 0, "totalpkm_nondrt [km]")
            worksheet_infos.write(7, 1, vehicles_nondrt['totalpkm'])

            worksheet_infos.write(9, 0, "number_vehicles_drt [1]")
            worksheet_infos.write(9, 1, 0)

            worksheet_infos.write(10, 0, "number_small_vehicles_drt [1]")
            worksheet_infos.write(10, 1, 0)
            worksheet_infos.write(11, 0, "number_medium_vehicles_drt [1]")
            worksheet_infos.write(11, 1, 0)
            worksheet_infos.write(12, 0, "number_large_vehicles_drt [1]")
            worksheet_infos.write(12, 1, 0)

            worksheet_infos.write(13, 0, "number_vehicles_nondrt [1]")
            worksheet_infos.write(13, 1, vehicles_nondrt['total_vehicles'])

            worksheet_infos.write(15, 0, "avg_speed_drt [km/h]")
            worksheet_infos.write(15, 1, 0)

            worksheet_infos.write(16, 0, "avg_speed_nondrt [km/h]")
            worksheet_infos.write(16, 1, vehicles_nondrt['avg_speed'])

            worksheet_infos.write(18, 0, "speed_pct_drt [1]")
            worksheet_infos.write(18, 1, 0)

            worksheet_infos.write(19, 0, "speed_pct_nondrt [1]")
            worksheet_infos.write(19, 1, vehicles_nondrt['speed_pct'])

            worksheet_infos.write(21, 0, "total_batteries_drt [1]")
            worksheet_infos.write(21, 1, 0)

            worksheet_infos.write(23, 0, "avg_passengers_drt [1]")
            worksheet_infos.write(23, 1, 0)

            worksheet_infos.write(25, 0, "km_peryear_fleet_drt [km]")
            worksheet_infos.write(25, 1, 0)

            worksheet_infos.write(26, 0, "km_peryear_fleet_nondrt [km]")
            worksheet_infos.write(26, 1, vehicles_nondrt['totalkm'] / years)

            worksheet_infos.write(28, 0, "pkm_peryear_fleet_drt [km]")
            worksheet_infos.write(28, 1, 0)

            worksheet_infos.write(29, 0, "pkm_peryear_fleet_nondrt [km]")
            worksheet_infos.write(29, 1, vehicles_nondrt['totalpkm'] / years)

            worksheet_infos.write(31, 0, "averaged_km_per_year_per_vehicle_drt [km]")
            worksheet_infos.write(31, 1, 0)

            worksheet_infos.write(32, 0, "averaged_km_per_year_per_vehicle_nondrt [km]")
            worksheet_infos.write(32, 1, vehicles_nondrt['km_per_vehicle_year'])

            worksheet_infos.write(34, 0, "averaged_pkm_per_year_per_vehicle_drt [km]")
            worksheet_infos.write(34, 1, 0)

            worksheet_infos.write(35, 0, "averaged_pkm_per_year_per_vehicle_nondrt [km]")
            worksheet_infos.write(35, 1, vehicles_nondrt['pkm_per_vehicle_year'])

            worksheet_infos.write(37, 0, "averaged_km_per_day_per_vehicle_drt [km]")
            worksheet_infos.write(37, 1, 0)

            worksheet_infos.write(38, 0, "averaged_km_per_day_per_vehicle_nondrt [km]")
            worksheet_infos.write(38, 1, vehicles_nondrt['km_per_vehicle_day'])

            worksheet_infos.write(40, 0, "averaged_pkm_per_day_per_vehicle_drt [km]")
            worksheet_infos.write(40, 1, 0)

            worksheet_infos.write(41, 0, "averaged_pkm_per_day_per_vehicle_nondrt [km]")
            worksheet_infos.write(41, 1, vehicles_nondrt['pkm_per_vehicle_day'])

        width= len("averaged_km_per_year_per_vehicle_nondrt [km]")
        worksheet_infos.set_column(0,0, width)

        workbook.close()
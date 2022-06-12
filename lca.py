from numpy import product
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
        self.mass_small = getfromvehicleconfig('mass_wo_battery','mass_electric_small')
        self.mass_medium = getfromvehicleconfig('mass_wo_battery','mass_electric_medium')
        self.mass_large = getfromvehicleconfig('mass_wo_battery','mass_electric_large')

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

        self.parameterdict['mass_electric_small_wo_battery'] = self.mass_small
        self.parameterdict['mass_electric_medium_wo_battery'] = self.mass_medium
        self.parameterdict['mass_electric_large_wo_battery'] = self.mass_large

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
        

    def lifecycleassessment_electric(self):
        
        if self.drt_vehiclesize == 2:
            drt_size = 'small'
        elif self.drt_vehiclesize == 4:
            drt_size = 'medium'
        elif self.drt_vehiclesize == 7:
            drt_size = 'large'
        else:
            print("there has been an error with your selected vehicle size")

        production_name = "drt production, electric, " + self.charging + ", " + drt_size +  " size passenger car | Cutoff, U"
        transport_name = "transport only, drt, " + self.charging + ", " + drt_size + " size, electric | Cutoff, U"
        fuel_name = "electric use"
        

        if not os.path.exists(os.path.join(self._resultspath, production_name + '.xlsx')):
            self.calculate_and_save(production_name)
        if not os.path.exists(os.path.join(self._resultspath, transport_name + '.xlsx')):
            self.calculate_and_save(transport_name)
        if not os.path.exists(os.path.join(self._resultspath, fuel_name + '.xlsx')):
            self.calculate_and_save(fuel_name)

    def lifecycleassessment_reference(self):

        # set name for production product system
        production_name = "passenger car production, " + drive + ", " + size + " size passenger car | Cutoff, U"

        # set name for transport product system
        transport_name = "transport only, passenger car, " + size + " size, " + drive + " | Cutoff, U"
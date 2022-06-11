from numpy import product
from config import *
import olca

class olcaclient():
    def __init__(self, path) -> None:
        self._client = olca.Client(8080)
        self._setup = olca.CalculationSetup()
        # set calculation type (http://greendelta.github.io/olca-schema/html/CalculationType.html)
        self._setup.calculation_type = olca.CalculationType.SIMPLE_CALCULATION
        # set impact method
        self._setup.impact_method = self._client.find(olca.ImpactMethod, 'zeroCUTS')
        self._resultspath = os.path.join(path, 'results')

    def redefinition(self, paramatername, value):
        self.setup.parameter_redefs = []
        redef_Parameter = olca.Parameterredef()
        redef_Parameter.name = paramatername
        redef_Parameter.value = value
        self.setup.parameter_redefs.append(redef_Parameter)

    def calculate_and_save(self, productname):
        productsystem = self._client.find(olca.ProductSystem, productname)
        self._setup.product_system = productsystem
        excelname = os.path.join(self._resultspath, productname + '-' + drt_vehiclesize + '-seats' + '.xlsx')
        try:
            openlca_result = self._client.calculate(self._setup)
            self._client.excel_export(openlca_result, excelname)
            self._client.dispose(openlca_result)
        except Exception as e:
            print('Berechnung hat nicht stattgefunden'+ e) 
        

    def lifecycleassessment_electric(self, chargingtype = 'normal'):

        # setting up IPC connection (port may have to be adjusted)
        
        if drt_vehiclesize == 2:
            drt_size = 'small'
        elif drt_vehiclesize == 4:
            drt_size = 'medium'
        elif drt_vehiclesize == 7:
            print("this drt vehicle size needs to be implemented first")
            pass
        else:
            print("there has been an error with your selected vehicle size")

        production_name = "passenger car production, electric, " + chargingtype + ", " + drt_size +  " size passenger car | Cutoff, U"
        transport_name = "transport only, passenger car, " + drt_size + " size, electric | Cutoff, U"
        fuel_name = "eletric use"
        
        self.calculate_and_save(production_name)
        self.calculate_and_save(transport_name)
        self.calculate_and_save(fuel_name)

    def lifecycleassessment_reference(self):

        # set name for production product system
        production_name = "passenger car production, " + drive + ", " + size + " size passenger car | Cutoff, U"

        # set name for transport product system
        transport_name = "transport only, passenger car, " + size + " size, " + drive + " | Cutoff, U"
#Hier kommt deine schlaue Doku hin :)
import olca

class Parameterredef():
    def __init__(self):
        pass
        #Hier und in die Klammer kommen deine Parameter hin
        #self.BeispielParameter = Beispielparameter

        #Hier kommt das definieren der Produktsysteme hin, bsp.
        #self.HerstellungAuto1 = 'Name dieses Produktsystems'

        #Hier evtl. Excelpfade, je nachdem wie du das machst

    def redefinition(self):
        self.setup.parameter_redefs = []
        Parameter = {Hier wieder deine Parameter}
        for key, value in Parameter.items():
            redef_Parameter = olca.Parameterredef()
            redef_Parameter.name = key
            redef_Parameter.value = value
            self.setup.parameter_redefs.append(redef_Parameter)

    def calculate(self):
        client = olca.Client(8080)
        self.setup.calculation_type = olca.CalculationType.SIMPLE_CALCULATION
        self.setup.product_system = client.find(olca.ProductSystem, Produktsystem)
        self.setup.impact_method = client.find(olca.ImpactMethod, 'IPCC 2013 GWP 100a')
        try:
            result = client.calculate(self.setup)
            client.excel_export(result, Excel_name)
            client.dispose(result)
        except Exception as e:
            print('Berechnung hat nicht stattgefunden'+ e) 

    def ausführen(self):
        self.calculate(Hier kommt das Produktsystem rein)

    
    # Integration in Main fehlt dann noch !
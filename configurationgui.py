# intializing the configgui starts a tkinter window and asks the user to set the paths
# for the drt scenario and the reference scenario, via clicking the open browser button
# additionally there is space for further configuration options

import tkinter as tk
from tkinter import ttk, HORIZONTAL, Button, Entry, Message, ttk, messagebox, Label, Tk
from tkinter import filedialog
from configuration import *
import tkinter.font as tkFont
import configparser

class configgui(tk.Tk, object):
    def __init__(self):
        super().__init__()

        # determines whether program ran succesfully or if the window was closed
        self.success = False

        # read in current config
        self.path_drt = getfromconfig('paths', 'path_drt')
        self.path_reference = getfromconfig('paths', 'path_reference')
        self.energymix = getfromconfig('vehicle_parameters', 'energymix')
        self.charging = getfromconfig('vehicle_parameters', 'charging')
        self.publictransport = getfromconfig('settings', 'publictransport_ignore')

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width/2)
        window_height = int(screen_height/2)

        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        #Set GUI surface
        self.resizable(False, False)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.title("Configuration GUI")

        entry_font = {"font": ("Courier", 15)}
        description = tkFont.Font(size=15,weight="bold")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=5)

        # DRT path label, note,  box and button to open directory browser
        self.path_drt_note = ttk.Label(self, text="Choose the path to the folder containing the MATSIM outputs of the DRT scenario")
        self.path_drt_note.grid(column=0, row=1, columnspan=3, pady=5)
        self.path_drt_note.configure(font=description)

        self.path_drt_label = ttk.Label(self, text="DRT path:")
        self.path_drt_label.grid(column=0, row=2, sticky=tk.E)

        self.path_drt_box = ttk.Entry(self, textvariable=tk.StringVar(), width=65, **entry_font)
        self.path_drt_box.grid(column=1, row=2, sticky=tk.W, pady=10)
        self.path_drt_box.insert(0, self.path_drt)

        self.path_drt_button = ttk.Button(self, text="Open browser", command = self.setdrtpath)
        self.path_drt_button.grid(column=2, row=2)


        # reference path label, box and button to open directory browser
        self.path_reference_note = ttk.Label(self, text="Choose the path to the folder containing the MATSIM outputs of the reference scenario")
        self.path_reference_note.grid(column=0, row=3, columnspan=3, pady=5)
        self.path_reference_note.configure(font=description)

        self.path_reference_label = ttk.Label(self, text="Reference path:")
        self.path_reference_label.grid(column=0, row=4, sticky=tk.E)        

        self.path_reference_box = ttk.Entry(self, textvariable=tk.StringVar(), width=65, **entry_font)
        self.path_reference_box.grid(column=1, row=4, sticky=tk.W, pady=10)
        self.path_reference_box.insert(0, self.path_reference)

        self.path_reference_button = ttk.Button(self, text="Open browser", command = self.setreferencepath)
        self.path_reference_button.grid(column=2, row=4)


        # vehicle size note, label and box
        self.energymix_note = ttk.Label(self, text="Select the grid mix that is to be used for the use phase of BEVs")
        self.energymix_note.grid(column=0, row=5, columnspan=3, pady=5)
        self.energymix_note.configure(font=description)

        self.energymix_label = ttk.Label(self, text="grid mix")
        self.energymix_label.grid(column=0, row=6, sticky=tk.E)

        self.energymix_combo = ttk.Combobox(self, textvariable=tk.IntVar(), values=["Greenmix", "today", "2030"], width = 10, justify=tk.CENTER)
        self.energymix_combo.grid(column=1, row=6, sticky=tk.W, pady=10)
        if self.energymix == "Greenmix":
            self.energymix_combo.current(0)
        elif self.energymix == "today":
            self.energymix_combo.current(1)
        else:
            self.energymix_combo.current(2)


        # definition of charging strategy, which ultimately determines the battery capacity
        self.charging_note = ttk.Label(self, text="choose charging strategy (opportunity: smaller battery) (normal: bigger battery)")
        self.charging_note.grid(column=0, row=7, columnspan=3, pady=5)
        self.charging_note.configure(font=description)

        self.charging_label = ttk.Label(self, text="charging strategy:")
        self.charging_label.grid(column=0, row=8, sticky=tk.E)

        self.charging_combo = ttk.Combobox(self, textvariable=tk.StringVar(), values=['opportunity', 'normal'], width = 10, justify=tk.CENTER)
        self.charging_combo.grid(column=1, row=8, sticky=tk.W, pady=10)
        if self.charging == 'opportunity':
            self.charging_combo.current(0)
        else:
            self.charging_combo.current(1)

        # definition of charging strategy, which ultimately determines the battery capacity
        self.publictransport_note = ttk.Label(self, text="choose whether to ignore public transport during DB creation or not (saves a bit of space if True)")
        self.publictransport_note.grid(column=0, row=9, columnspan=3, pady=5)
        self.publictransport_note.configure(font=description)

        self.publictransport_label = ttk.Label(self, text="ignore publictransport:")
        self.publictransport_label.grid(column=0, row=10, sticky=tk.E)

        self.publictransport_combo = ttk.Combobox(self, textvariable=tk.StringVar(), values=['True', 'False'], width = 10, justify=tk.CENTER)
        self.publictransport_combo.grid(column=1, row=10, sticky=tk.W, pady=10)
        if self.publictransport == 'True':
            self.publictransport_combo.current(0)
        else:
            self.publictransport_combo.current(1)

        # definition of charging strategy, which ultimately determines the battery capacity
        self.publictransport_note = ttk.Label(self, text="choose whether to ignore public transport during DB creation or not (saves a bit of space if True)")
        self.publictransport_note.grid(column=0, row=11, columnspan=3, pady=5)
        self.publictransport_note.configure(font=description)

        self.publictransport_label = ttk.Label(self, text="use csv")
        self.publictransport_label.grid(column=0, row=12, sticky=tk.E)

        self.publictransport_combo = ttk.Combobox(self, textvariable=tk.StringVar(), values=['True', 'False'], width = 10, justify=tk.CENTER)
        self.publictransport_combo.grid(column=1, row=12, sticky=tk.W, pady=10)
        if self.publictransport == 'True':
            self.publictransport_combo.current(0)
        else:
            self.publictransport_combo.current(1)

        # button that triggers the storing of the chosen specs and closes this GUI
        self.startbutton = ttk.Button(self, text="Start Script", command=lambda:[f() for f in [self.startscript, self.destroy]])
        self.startbutton.grid(column=1, row=14, sticky=tk.E, pady=10)

        self.vehicleparams_button = ttk.Button(self, text="Edit Vehicle Parameters", command=self.changevehicles)
        self.vehicleparams_button.grid(column=1, row=14, sticky=tk.W, pady=10)

        self.mainloop()

    def startscript(self):
        ''' retrieve paths from GUI and store them in the config.ini '''
        edit = configparser.ConfigParser()
        edit.read("config.ini")
        paths = edit['paths']
        vehicleparameters = edit['vehicle_parameters']
        settings = edit['settings']

        paths['path_drt'] = self.path_drt_box.get()
        paths['path_reference'] = self.path_reference_box.get()

        vehicleparameters['drt_vehiclesize'] = self.energymix_combo.get()
        vehicleparameters['charging'] = self.charging_combo.get()
        
        settings['publictransport_ignore'] = self.publictransport_combo.get()

        with open("config.ini", 'w') as file:
            edit.write(file)

        self.success = True

    def opendirectorywindow(self):
        ''' opens a directory browser window and returns the chose direcotry'''
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askdirectory()
        root.destroy()
        return file_path

    def setdrtpath(self):
        ''' calls the function that opens the browser window and updates the chosen directory in the GUI'''
        path = self.opendirectorywindow()
        if str(path).startswith("//"):
            path = path[1:]
        self.path_drt_box.delete(0, tk.END)
        self.path_drt_box.insert(0, path)

    def setreferencepath(self):
        ''' calls the function that opens the browser window and updates the chosen directory in the GUI'''
        path = self.opendirectorywindow()
        if str(path).startswith("//"):
            path = path[1:]
        self.path_reference_box.delete(0, tk.END)
        self.path_reference_box.insert(0, path)

    def changevehicles(self):
        self.vehicleparams = vehicleparams()
        
class vehicleparams(tk.Tk, object):
    def __init__(self):
        super().__init__()

        # read in current config
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

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width/2)
        window_height = int(screen_height/2)

        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        #Set GUI surface
        self.resizable(False, False)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.title("Vehicle Parameters")

        entry_font = {"font": ("Courier", 15)}
        description = tkFont.Font(size=15,weight="bold")
        title = tkFont.Font(size=15, weight="bold")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=3)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=3)

        self.small_label = ttk.Label(self, text="small")
        self.small_label.grid(column= 0, row=0, columnspan=2)
        self.small_label.configure(font=title)

        self.medium_label = ttk.Label(self, text="medium")
        self.medium_label.grid(column= 2, row=0, columnspan=2)
        self.medium_label.configure(font=title)

        self.large_label = ttk.Label(self, text="large")
        self.large_label.grid(column= 4, row=0, columnspan=2)
        self.large_label.configure(font=title)

        self.mass_small_label = ttk.Label(self, text="mass [kg]:")
        self.mass_small_label.grid(column=0, row=1, sticky=tk.E)
        self.mass_small_label.configure(font=description)

        self.mass_small_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.mass_small_box.grid(column=1, row=1, sticky=tk.E, pady=10)
        self.mass_small_box.insert(0, self.mass_small)

        self.mass_medium_label = ttk.Label(self, text="mass [kg]:")
        self.mass_medium_label.grid(column=2, row=1, sticky=tk.E)
        self.mass_medium_label.configure(font=description)

        self.mass_medium_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.mass_medium_box.grid(column=3, row=1, sticky=tk.E, pady=10)
        self.mass_medium_box.insert(0, self.mass_medium)

        self.mass_large_label = ttk.Label(self, text="mass [kg]:")
        self.mass_large_label.grid(column=4, row=1, sticky=tk.E)
        self.mass_large_label.configure(font=description)

        self.mass_large_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.mass_large_box.grid(column=5, row=1, sticky=tk.E, pady=10)
        self.mass_large_box.insert(0, self.mass_large)


        self.battery_small_label = ttk.Label(self, text="battery size [kWh]:")
        self.battery_small_label.grid(column=0, row=2, sticky=tk.E)
        self.battery_small_label.configure(font=description)

        self.battery_small_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.battery_small_box.grid(column=1, row=2, sticky=tk.E, pady=10)
        self.battery_small_box.insert(0, self.battery_small)

        self.battery_medium_label = ttk.Label(self, text="battery size [kWh]:")
        self.battery_medium_label.grid(column=2, row=2, sticky=tk.E)
        self.battery_medium_label.configure(font=description)

        self.battery_medium_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.battery_medium_box.grid(column=3, row=2, sticky=tk.E, pady=10)
        self.battery_medium_box.insert(0, self.battery_medium)

        self.battery_large_label = ttk.Label(self, text="battery size [kWh]:")
        self.battery_large_label.grid(column=4, row=2, sticky=tk.E)
        self.battery_large_label.configure(font=description)

        self.battery_large_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.battery_large_box.grid(column=5, row=2, sticky=tk.E, pady=10)
        self.battery_large_box.insert(0, self.battery_large)


        self.battery_small_opportunity_label = ttk.Label(self, text="battery size opportunity [kWh]:")
        self.battery_small_opportunity_label.grid(column=0, row=3, sticky=tk.E)
        self.battery_small_opportunity_label.configure(font=description)

        self.battery_small_opportunity_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.battery_small_opportunity_box.grid(column=1, row=3, sticky=tk.E, pady=10)
        self.battery_small_opportunity_box.insert(0, self.battery_small_opportunity)

        self.battery_medium_opportunity_label = ttk.Label(self, text="battery size opportunity [kWh]:")
        self.battery_medium_opportunity_label.grid(column=2, row=3, sticky=tk.E)
        self.battery_medium_opportunity_label.configure(font=description)

        self.battery_medium_opportunity_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.battery_medium_opportunity_box.grid(column=3, row=3, sticky=tk.E, pady=10)
        self.battery_medium_opportunity_box.insert(0, self.battery_medium_opportunity)

        self.battery_large_opportunity_label = ttk.Label(self, text="battery size opportunity [kWh]:")
        self.battery_large_opportunity_label.grid(column=4, row=3, sticky=tk.E)
        self.battery_large_opportunity_label.configure(font=description)

        self.battery_large_opportunity_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.battery_large_opportunity_box.grid(column=5, row=3, sticky=tk.E, pady=10)
        self.battery_large_opportunity_box.insert(0, self.battery_large_opportunity)


        self.consumption_small_label = ttk.Label(self, text="consumption [kWh/100km]:")
        self.consumption_small_label.grid(column=0, row=4, sticky=tk.E)
        self.consumption_small_label.configure(font=description)

        self.consumption_small_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.consumption_small_box.grid(column=1, row=4, sticky=tk.E, pady=10)
        self.consumption_small_box.insert(0, self.consumption_small)

        self.consumption_medium_label = ttk.Label(self, text="consumption [kWh/100km]:")
        self.consumption_medium_label.grid(column=2, row=4, sticky=tk.E)
        self.consumption_medium_label.configure(font=description)

        self.consumption_medium_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.consumption_medium_box.grid(column=3, row=4, sticky=tk.E, pady=10)
        self.consumption_medium_box.insert(0, self.consumption_medium)

        self.consumption_large_label = ttk.Label(self, text="consumption [kWh/100km]:")
        self.consumption_large_label.grid(column=4, row=4, sticky=tk.E)
        self.consumption_large_label.configure(font=description)

        self.consumption_large_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.consumption_large_box.grid(column=5, row=4, sticky=tk.E, pady=10)
        self.consumption_large_box.insert(0, self.consumption_large)


        self.consumption_small_opportunity_label = ttk.Label(self, text="consumption opportunity [kWh/100km]:")
        self.consumption_small_opportunity_label.grid(column=0, row=5, sticky=tk.E)
        self.consumption_small_opportunity_label.configure(font=description)

        self.consumption_small_opportunity_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.consumption_small_opportunity_box.grid(column=1, row=5, sticky=tk.E, pady=10)
        self.consumption_small_opportunity_box.insert(0, self.consumption_small_opportunity)

        self.consumption_medium_opportunity_label = ttk.Label(self, text="consumption opportunity [kWh/100km]:")
        self.consumption_medium_opportunity_label.grid(column=2, row=5, sticky=tk.E)
        self.consumption_medium_opportunity_label.configure(font=description)

        self.consumption_medium_opportunity_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.consumption_medium_opportunity_box.grid(column=3, row=5, sticky=tk.E, pady=10)
        self.consumption_medium_opportunity_box.insert(0, self.consumption_medium_opportunity)

        self.consumption_large_opportunity_label = ttk.Label(self, text="consumption opportunity [kWh/100km]:")
        self.consumption_large_opportunity_label.grid(column=4, row=5, sticky=tk.E)
        self.consumption_large_opportunity_label.configure(font=description)

        self.consumption_large_opportunity_box = ttk.Entry(self, textvariable=tk.IntVar(), width=6, **entry_font)
        self.consumption_large_opportunity_box.grid(column=5, row=5, sticky=tk.E, pady=10)
        self.consumption_large_opportunity_box.insert(0, self.consumption_large_opportunity)

        self.restorestandards_button = ttk.Button(self, text="restore standards", command=self.restorestandards)
        self.restorestandards_button.grid(column=1, row=6, sticky=tk.W, columnspan=4)

        self.saveparameters_button = ttk.Button(self, text="save parameters and close", command=lambda:[f() for f in [self.saveparameters, self.destroy]])
        self.saveparameters_button.grid(column=1, row=6, sticky=tk.E, columnspan=4)
        self.mainloop()

    def saveparameters(self):
        edit = configparser.ConfigParser()
        edit.read("vehicle.ini")
        mass_wo_battery = edit['mass_wo_battery']
        battery_size = edit['battery_size']
        energy_consumption = edit['energy_consumption']

        mass_wo_battery['mass_electric_small'] = self.mass_small_box.get()
        mass_wo_battery['mass_electric_medium'] = self.mass_medium_box.get()
        mass_wo_battery['mass_electric_large'] = self.mass_large_box.get()

        battery_size['battery_small'] = self.battery_small_box.get()
        battery_size['battery_medium'] = self.battery_medium_box.get()
        battery_size['battery_large'] = self.battery_large_box.get()

        battery_size['battery_small_opportunity'] = self.battery_small_opportunity_box.get()
        battery_size['battery_medium_opportunity'] = self.battery_medium_opportunity_box.get()
        battery_size['battery_large_opportunity'] = self.battery_large_opportunity_box.get()

        energy_consumption['consumption_small'] = self.consumption_small_box.get()
        energy_consumption['consumption_medium'] = self.consumption_medium_box.get()
        energy_consumption['consumption_large'] = self.consumption_large_box.get()

        energy_consumption['consumption_small_opportunity'] = self.consumption_small_opportunity_box.get()
        energy_consumption['consumption_medium_opportunity'] = self.consumption_medium_opportunity_box.get()
        energy_consumption['consumption_large_opportunity'] = self.consumption_large_opportunity_box.get()

        with open("vehicle.ini", 'w') as file:
            edit.write(file)

    def restorestandards(self):
        self.mass_small = getfromvehicleconfig('mass_wo_battery','mass_electric_small', True)
        self.mass_small_box.delete(0, tk.END)
        self.mass_small_box.insert(0, self.mass_small)
        self.mass_medium = getfromvehicleconfig('mass_wo_battery','mass_electric_medium', True)
        self.mass_medium_box.delete(0, tk.END)
        self.mass_medium_box.insert(0, self.mass_medium)
        self.mass_large = getfromvehicleconfig('mass_wo_battery','mass_electric_large', True)
        self.mass_large_box.delete(0, tk.END)
        self.mass_large_box.insert(0, self.mass_large)

        self.battery_small = getfromvehicleconfig('battery_size','battery_small', True)
        self.battery_small_box.delete(0, tk.END)
        self.battery_small_box.insert(0, self.battery_small)
        self.battery_medium = getfromvehicleconfig('battery_size','battery_medium', True)
        self.battery_medium_box.delete(0, tk.END)
        self.battery_medium_box.insert(0, self.battery_medium)
        self.battery_large = getfromvehicleconfig('battery_size','battery_large', True)
        self.battery_large_box.delete(0, tk.END)
        self.battery_large_box.insert(0, self.battery_large)

        self.battery_small_opportunity = getfromvehicleconfig('battery_size','battery_small_opportunity', True)
        self.battery_small_opportunity_box.delete(0, tk.END)
        self.battery_small_opportunity_box.insert(0, self.battery_small_opportunity)
        self.battery_medium_opportunity = getfromvehicleconfig('battery_size','battery_medium_opportunity', True)
        self.battery_medium_opportunity_box.delete(0, tk.END)
        self.battery_medium_opportunity_box.insert(0, self.battery_medium_opportunity)
        self.battery_large_opportunity = getfromvehicleconfig('battery_size','battery_large_opportunity', True)
        self.battery_large_opportunity_box.delete(0, tk.END)
        self.battery_large_opportunity_box.insert(0, self.battery_large_opportunity)

        self.consumption_small = getfromvehicleconfig('energy_consumption','consumption_small', True)
        self.consumption_small_box.delete(0, tk.END)
        self.consumption_small_box.insert(0, self.consumption_small)
        self.consumption_medium = getfromvehicleconfig('energy_consumption','consumption_medium', True)
        self.consumption_medium_box.delete(0, tk.END)
        self.consumption_medium_box.insert(0, self.consumption_medium)
        self.consumption_large = getfromvehicleconfig('energy_consumption','consumption_large', True)
        self.consumption_large_box.delete(0, tk.END)
        self.consumption_large_box.insert(0, self.consumption_large)

        self.consumption_small_opportunity = getfromvehicleconfig('energy_consumption','consumption_small_opportunity', True)
        self.consumption_small_opportunity_box.delete(0, tk.END)
        self.consumption_small_opportunity_box.insert(0, self.consumption_small_opportunity)
        self.consumption_medium_opportunity = getfromvehicleconfig('energy_consumption','consumption_medium_opportunity', True)
        self.consumption_medium_opportunity_box.delete(0, tk.END)
        self.consumption_medium_opportunity_box.insert(0, self.consumption_medium_opportunity)
        self.consumption_large_opportunity = getfromvehicleconfig('energy_consumption','consumption_large_opportunity', True)
        self.consumption_large_opportunity_box.delete(0, tk.END)
        self.consumption_large_opportunity_box.insert(0, self.consumption_large_opportunity)
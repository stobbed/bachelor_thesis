import tkinter as tk
from tkinter import ttk, HORIZONTAL, Button, Entry, Message, ttk, messagebox, Label, Tk
from tkinter import filedialog
from configuration import *
import tkinter.font as tkFont
import configparser

class configui(tk.Tk, object):
    def __init__(self):
        super().__init__()

        # read in current config

        self.path_drt = getfromconfig('paths', 'path_drt')
        self.path_reference = getfromconfig('paths', 'path_reference')
        self.drtvehiclesize = getfromconfig('vehicle_parameters', 'drt_vehiclesize')

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

        self.path_drt_note = ttk.Label(self, text="Choose the path to the folder containing the MATSIM outputs of the DRT scenario")
        self.path_drt_note.grid(column=0, row=1, columnspan=3, pady=5)
        self.path_drt_note.configure(font=description)

        self.path_drt_label = ttk.Label(self, text="DRT path:")
        self.path_drt_label.grid(column=0, row=2, sticky=tk.E)

        self.path_drt_box = ttk.Entry(self, textvariable=self.path_drt, width=65, **entry_font)
        self.path_drt_box.grid(column=1, row=2, sticky=tk.W, pady=10)
        self.path_drt_box.insert(0, self.path_drt)

        self.path_drt_button = ttk.Button(self, text="Open browser", command = self.setdrtpath)
        self.path_drt_button.grid(column=2, row=2)

        self.path_reference_note = ttk.Label(self, text="Choose the path to the folder containing the MATSIM outputs of the reference scenario")
        self.path_reference_note.grid(column=0, row=3, columnspan=3, pady=5)
        self.path_reference_note.configure(font=description)

        self.path_reference_label = ttk.Label(self, text="Reference path:")
        self.path_reference_label.grid(column=0, row=4, sticky=tk.E)        

        self.path_reference_box = ttk.Entry(self, textvariable=self.path_reference, width=65, **entry_font)
        self.path_reference_box.grid(column=1, row=4, sticky=tk.W, pady=10)
        self.path_reference_box.insert(0, self.path_reference)

        self.path_reference_button = ttk.Button(self, text="Open browser", command = self.setreferencepath)
        self.path_reference_button.grid(column=2, row=4)

        self.drtvehiclesize_note = ttk.Label(self, text="DRT vehicle size can only be 2 (small), 4 (medium) or 7 (large) at this moment")
        self.drtvehiclesize_note.grid(column=0, row=5, columnspan=3, pady=5)
        self.drtvehiclesize_note.configure(font=description)

        self.drtvehiclesize_label = ttk.Label(self, text="DRT vehicle size")
        self.drtvehiclesize_label.grid(column=0, row=6)

        self.drtvehiclesize_box = ttk.Entry(self, textvariable=self.drtvehiclesize, **entry_font)
        self.drtvehiclesize_box.grid(column=1, row=6, stick=tk.W, pady=10)
        self.drtvehiclesize_box.insert(0, self.drtvehiclesize)

        self.startbutton = ttk.Button(self, text="Start Script", command=lambda:[f() for f in [self.startscript, self.destroy]])
        self.startbutton.grid(column=0, row=7, columnspan=3)

        self.mainloop()

    def startscript(self):
        edit = configparser.ConfigParser()
        edit.read("config.ini")
        paths = edit['paths']
        vehicleparams = edit['vehicle_parameters']

        paths['path_drt'] = self.path_drt_box.get()
        paths['path_reference'] = self.path_reference_box.get()

        vehicleparams['drt_vehiclesize'] = self.drtvehiclesize_box.get()

        with open("config.ini", 'w') as file:
            edit.write(file)

    def opendirectorywindow(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askdirectory()
        root.destroy()
        return file_path

    def setdrtpath(self):
        path = self.opendirectorywindow()
        if str(path).startswith("//"):
            path = path[1:]
        self.path_drt_box.delete(0, tk.END)
        self.path_drt_box.insert(0, path)

    def setreferencepath(self):
        path = self.opendirectorywindow()
        if str(path).startswith("//"):
            path = path[1:]
        self.path_reference_box.delete(0, tk.END)
        self.path_reference_box.insert(0, path)
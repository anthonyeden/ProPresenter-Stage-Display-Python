"ProPresenter Stage Display App - Implements Clock, Current & Next Text"

import os
import json
from ProPresenterStageDisplayClientComms import ProPresenterStageDisplayClientComms
import Tkinter as tk
import time

__author__ = "Anthony Eden"
__copyright__ = "Copyright 2017, Anthony Eden / Media Realm"
__credits__ = ["Anthony Eden"]
__license__ = "GPL"
__version__ = "0.1"

class Application(tk.Frame):
    
    # Store the Tk root class
    root = None
    
    # Store the threaded class for ProPresenter
    ProPresenter = None
    
    # Store the labels on the screen
    labelCurrent = None
    labelNext = None
    labelClock = None
    
    # Store the last time string
    time_last = ""

    # The maximum length of each line on the screen - set in config file
    wordWrapLength = 1500
    
    def __init__(self, master = None):
        # Setup the application and display window
        
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.focus_set()
        self.root.attributes('-fullscreen', True)
        self.root.bind('<KeyPress>', self.close)
        
        # Get the config from JSON
        try:
            ConfigData_Filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.json")
            ConfigData_JSON = open(ConfigData_Filename).read()
            ConfigData = json.loads(ConfigData_JSON)
    
        except Exception, e:
            print
            print "##############################################"
            print "EXCEPTION: Cannot load and parse Config.JSON File: "
            print e
            print "##############################################"
            print
        
            exit()
        
        try:
            ProP_IPAddress = ConfigData['IPAddress']
            ProP_IPPort = int(ConfigData['IPPort'])
            ProP_Password = ConfigData['Password']
            self.wordWrapLength = int(ConfigData['WordWrapLength'])
        except Exception, e:
            print
            print "##############################################"
            print "EXCEPTION: Config file is missing a setting"
            print e
            print "##############################################"
            print
            
            exit()
        
        # Connect to ProPresenter and setup the necessary callbacks
        self.ProPresenter = ProPresenterStageDisplayClientComms(ProP_IPAddress, ProP_IPPort, ProP_Password)
        self.ProPresenter.addSubscription("CurrentSlide", self.updateSlideTextCurrent)
        self.ProPresenter.addSubscription("NextSlide", self.updateSlideTextNext)
        self.ProPresenter.start()
        
        self.setupMainInterface()

    def setupMainInterface(self):
        # Setup the interface widgets

        # Setup the main window for the application
        tk.Frame.__init__(
            self,
            None,
            background = "black"
        )
        self.grid(sticky = tk.N + tk.S + tk.E + tk.W)

        self.top = self.winfo_toplevel()
        
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 20)
        self.rowconfigure(2, weight = 20)
        self.columnconfigure(0, weight = 1)
        
        self.top.grid()
        self.top.rowconfigure(0, weight = 1)
        self.top.columnconfigure(0, weight = 1)
        
        self.grid_propagate(False)
        self.top.grid_propagate(False)
        
        # Clock Text Label
        self.labelClock = tk.Label(
            self,
            text = str("Clock"),
            font = ("Arial", 52, "bold"),
            background = "black",
            foreground = "#FFF",
            wraplength = self.wordWrapLength,
            anchor = tk.NW,
            justify = tk.LEFT
        )
        self.labelClock.grid(
            column = 0,
            row = 0,
            sticky = tk.W+tk.E+tk.N+tk.S,
            padx = 50,
            pady = 50
        )
        
        # Current Slide Text Label
        self.labelCurrent = tk.Label(
            self,
            text = "Waiting for data...",
            font = ("Arial", 52, "bold"),
            background = "black",
            foreground = "white",
            wraplength = self.wordWrapLength,
            anchor = tk.NW,
            justify = tk.LEFT
        )
        self.labelCurrent.grid(
            column = 0,
            row = 1,
            sticky = tk.W+tk.E+tk.N+tk.S,
            padx = 50,
            pady = 50
        )
        
        
        # Next Slide Text Label
        self.labelNext = tk.Label(
            self,
            text = "",
            font = ("Arial", 38, "bold"),
            background = "black",
            foreground = "white",
            wraplength = self.wordWrapLength,
            anchor = tk.NW,
            justify = tk.LEFT
        )
        self.labelNext.grid(
            column = 0,
            row = 2,
            sticky = tk.W+tk.E+tk.N+tk.S,
            padx = 50,
            pady = 50
        )
    
    def updateSlideTextCurrent(self, data):
        # Update the text label for the current slide
        if data['text'] is not None:
            self.labelCurrent.configure(text = data['text'].encode('utf-8'))
        else:
            self.labelCurrent.configure(text = "")

    def updateSlideTextNext(self, data):
        # Update the text label for the next slide
        if data['text'] is not None:
            self.labelNext.configure(text = data['text'].encode('utf-8'))
        else:
            self.labelNext.configure(text = "")
    
    def close(self, extra = None):
        # Terminate the application
        if self.ProPresenter is not None:
            self.ProPresenter.stop()
        
        self.root.destroy()
    
    def clock_tick(self):
        # Sets the clock time
        time_now = time.strftime('%I:%M:%S %p')
        
        # Update the timer on screen when the timer has incremented
        if time_now != self.time_last:
            self.time_last = time_now
            self.labelClock.config(text = time_now)
        
        self.labelClock.after(200, self.clock_tick)

if __name__ == "__main__":
    app = Application()
    app.master.title('ProPresenter Stage Display')
    app.clock_tick()
    app.mainloop()

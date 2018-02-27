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

    # Config data for ProPresenter
    ProP_IPAddress = None
    ProP_IPPort = None
    ProP_Password = None
    
    # Store the labels on the screen
    labelCurrent = None
    labelNext = None
    labelClock = None
    
    # Store the last time string
    time_last = ""

    # The maximum length of each line on the screen - set in config file
    wordWrapLength = 1500

    # Font sizes
    fontSizeClock = 52
    fontSizeCurrent = 52
    fontSizeNext = 36

    # Font name
    fontName = "Arial"
    fontStyle = "bold"
    fontUppercase = False
    fontAlign = tk.S + tk.W + tk.E
    fontJustify = tk.CENTER

    # Lower Third Mode?
    modeLowerThird = False

    # Merge every 2nd line (for lower thirds)
    mergeLines = False
    mergeLinesMin = 4
    mergeLinesJoinChar = ","
    mergeLinesStripTrailing = [".", ";", ",", " "]

    # Specify the padding for the screen
    padX = 50
    padY = 50

    # Do we need to attempt a reconnection?
    tryReconnect = False
    disconnectTime = 0

    def __init__(self, master = None):
        # Setup the application and display window
        
        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.focus_set()
        self.root.attributes('-fullscreen', True)
        self.root.bind('<KeyPress>', self.close)
        self.root.config(cursor = 'none')
        
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
            self.ProP_IPAddress = ConfigData['IPAddress']
            self.ProP_IPPort = int(ConfigData['IPPort'])
            self.ProP_Password = ConfigData['Password']
            self.wordWrapLength = int(ConfigData['WordWrapLength'])
            self.fontSizeClock = int(ConfigData['FontSizeClock'])
            self.fontSizeCurrent = int(ConfigData['FontSizeCurrent'])
            self.fontSizeNext = int(ConfigData['FontSizeNext'])

            if "LowerThirdMode" in ConfigData and ConfigData['LowerThirdMode'] is True:
                self.modeLowerThird = True

            if "FontName" in ConfigData:
                self.fontName = ConfigData['FontName']

            if "FontStyle" in ConfigData:
                self.fontStyle = ConfigData['FontStyle']

            if "FontUppercase" in ConfigData and ConfigData['FontUppercase'] is True:
                self.fontUppercase = True

            if "FontAlign" in ConfigData and ConfigData['FontAlign'] == "center":
                self.fontAlign = tk.S + tk.W + tk.E
                self.fontJustify = tk.CENTER

            if "FontAlign" in ConfigData and ConfigData['FontAlign'] == "left":
                self.fontAlign = tk.S + tk.W
                self.fontJustify = tk.LEFT

            if "FontAlign" in ConfigData and ConfigData['FontAlign'] == "right":
                self.fontAlign = tk.S + tk.E
                self.fontJustify = tk.RIGHT

            if "MergeLines" in ConfigData and ConfigData['MergeLines'] is True:
                self.mergeLines = True

            if "MergeLinesMin" in ConfigData:
                self.mergeLinesMin = int(ConfigData['MergeLinesMin'])

            if "MergeLinesJoinChar" in ConfigData:
                self.mergeLinesJoinChar = ConfigData['MergeLinesJoinChar']

            if "PadX" in ConfigData:
                self.padX = int(ConfigData['PadX'])

            if "PadY" in ConfigData:
                self.padY = int(ConfigData['PadY'])

        except Exception, e:
            print
            print "##############################################"
            print "EXCEPTION: Config file is missing a setting"
            print e
            print "##############################################"
            print
            
            exit()

        if self.modeLowerThird:
            self.setupMainInterface_LowerThird()
        else:
            self.setupMainInterface()

        self.connect()
        self.reconnect_tick()

    def connect(self):
        # Connect to ProPresenter and setup the necessary callbacks
        self.tryReconnect = False
        self.disconnectTime = 0

        self.ProPresenter = ProPresenterStageDisplayClientComms(self.ProP_IPAddress, self.ProP_IPPort, self.ProP_Password)
        self.ProPresenter.addSubscription("CurrentSlide", self.updateSlideTextCurrent)
        self.ProPresenter.addSubscription("NextSlide", self.updateSlideTextNext)
        self.ProPresenter.addSubscription("Connected", self.connected)
        self.ProPresenter.addSubscription("ConnectionFailed", self.connectFailed)
        self.ProPresenter.addSubscription("Disconnected", self.disconnected)
        self.ProPresenter.start()

    def connected(self, data):
        print "ProPresenter Connected"

    def connectFailed(self, error):
        self.tryReconnect = True
        
        if self.disconnectTime == 0:
            self.disconnectTime = time.time()
        
        print "ProPresenter Connect Failed", error
    
    def disconnected(self, error):
        self.tryReconnect = True
        
        if self.disconnectTime == 0:
            self.disconnectTime = time.time()
        
        print "ProPresenter Disconnected", error

    def reconnect_tick(self):
        if self.tryReconnect and self.disconnectTime < time.time() - 5:
            print "Attempting to reconnect to ProPresenter"
            self.connect()
        
        self.labelCurrent.after(2000, self.reconnect_tick)

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
            font = (self.fontName, self.fontSizeClock, self.fontStyle),
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
            padx = self.padX,
            pady = self.padY
        )
        
        # Current Slide Text Label
        self.labelCurrent = tk.Label(
            self,
            text = "Waiting for data...",
            font = (self.fontName, self.fontSizeCurrent, self.fontStyle),
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
            padx = self.padX,
            pady = self.padY
        )
        
        
        # Next Slide Text Label
        self.labelNext = tk.Label(
            self,
            text = "",
            font = (self.fontName, self.fontSizeNext, self.fontStyle),
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
            padx = self.padX,
            pady = self.padY
        )
    
    def setupMainInterface_LowerThird(self):
        # Setup the interface widgets - for lower third mode

        # Setup the main window for the application
        tk.Frame.__init__(
            self,
            None,
            background = "black",
            cursor = "none"
        )
        self.grid(sticky = tk.N + tk.S + tk.E + tk.W)

        self.top = self.winfo_toplevel()
        
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)
        
        self.top.grid()
        self.top.rowconfigure(0, weight = 1)
        self.top.columnconfigure(0, weight = 1)

        # Current Slide Text Label
        self.labelCurrent = tk.Label(
            self,
            text = "Waiting for data...",
            font = (self.fontName, self.fontSizeCurrent, self.fontStyle),
            background = "black",
            foreground = "white",
            wraplength = self.wordWrapLength,
            justify = self.fontJustify
        )
        self.labelCurrent.grid(
            column = 0,
            row = 0,
            sticky = self.fontAlign,
            padx = self.padX,
            pady = self.padY
        )

    def updateSlideTextCurrent(self, data):
        # Update the text label for the current slide
        if self.labelCurrent is None:
            return False

        if data['text'] is None:
            self.labelCurrent.configure(text = "")
            return None

        if self.mergeLines:
            # Prepare to remove every 2nd line break
            lines = data['text'].encode('utf-8').split("\n")
            textOutput = ""

            if len(lines) < self.mergeLinesMin:
                # No need to merge these lines
                textOutput = "\n".join(lines)
            else:
                # Join every 2nd line to the previous
                for i, line in enumerate(lines):

                    # Strip trailing or leading whitespace from each line
                    line = line.strip()

                    # Get rid of some trailing punctuation before the merge
                    if line[-1:] in self.mergeLinesStripTrailing:
                        line = line[:-1]

                    if i == 0:
                        textOutput = line
                    elif i % 2 == 0:
                        textOutput += "\n" + line
                    else:
                        textOutput += self.mergeLinesJoinChar.encode('utf-8') + " " + line
        else:
            textOutput = data['text'].encode('utf-8')

        if self.fontUppercase:
            self.labelCurrent.configure(text = textOutput.upper())
        elif not self.fontUppercase:
            self.labelCurrent.configure(text = textOutput)

    def updateSlideTextNext(self, data):
        # Update the text label for the next slide
        if self.labelNext is None:
            return False

        if data['text'] is not None and self.fontUppercase:
            self.labelNext.configure(text = data['text'].encode('utf-8').upper())
        elif data['text'] is not None and not self.fontUppercase:
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
        if self.labelClock is None:
            return False

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

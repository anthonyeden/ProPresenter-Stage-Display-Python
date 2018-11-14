"ProPresenter Stage Display App - Implements Clock, Current & Next Text"

import os
import json
from ProPresenterStageDisplayClientComms import ProPresenterStageDisplayClientComms
import Tkinter as tk
import time

__author__ = "Anthony Eden"
__copyright__ = "Copyright 2017-2018, Anthony Eden / Media Realm"
__credits__ = ["Anthony Eden"]
__license__ = "GPL"
__version__ = "1.0"

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

    # Allow splitting the text at a certain delimiter
    splitLinesChar = None

    # Specify the padding for the screen
    padX = 50
    padY = 50

    # Allow user-configurable background and text colours
    backgroundColour = "black"
    textColour = "white"

    # Store the next that needs to be rendered
    currentText = ""
    nextText = ""

    # Lower third padding
    lowerThirdHeight = 0
    lowerThirdContainer = None

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
            
            if "LowerThirdHeight" in ConfigData:
                self.lowerThirdHeight = int(ConfigData['LowerThirdHeight'])
            else:
                self.lowerThirdHeight = self.root.winfo_screenheight() - (self.padY * 2)
            
            if "BackgroundColour" in ConfigData:
                self.backgroundColour = ConfigData['BackgroundColour']

            if "TextColour" in ConfigData:
                self.textColour = ConfigData['TextColour']

            if "SplitLines" in ConfigData:
                self.splitLinesChar = ConfigData['SplitLines']

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
            background = self.backgroundColour
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
            background = self.backgroundColour,
            foreground = self.textColour,
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
            background = self.backgroundColour,
            foreground = self.textColour,
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
            background = self.backgroundColour,
            foreground = self.textColour,
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
            background = self.backgroundColour,
            cursor = "none"
        )
        self.grid(sticky = tk.N + tk.S + tk.E + tk.W)

        self.top = self.winfo_toplevel()
        
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)
        
        self.top.grid()
        self.top.rowconfigure(0, weight = 1)
        self.top.columnconfigure(0, weight = 1)

        self.lowerThirdContainer = tk.Frame(
            self,
            height = self.lowerThirdHeight,
            width = self.root.winfo_screenwidth() - (self.padX * 2),
            background = self.backgroundColour,
        )
        self.lowerThirdContainer.pack_propagate(0)
        self.lowerThirdContainer.place(x = self.padX, y = self.root.winfo_screenheight() - self.padY - self.lowerThirdHeight)

        self.labelCurrent = tk.Label(
            self.lowerThirdContainer,
            text = "Waiting for data...",
            font = (self.fontName, self.fontSizeCurrent, self.fontStyle),
            foreground = self.textColour,
            background = self.backgroundColour,
            wraplength = self.wordWrapLength,
            justify = self.fontJustify,
        )

        if self.fontJustify == tk.RIGHT:
            anchor = tk.E
        elif self.fontJustify == tk.LEFT:
            anchor = tk.W
        else:
            anchor = tk.CENTER

        if self.lowerThirdHeight == self.root.winfo_screenheight() - (self.padY * 2):
            # Anchor to bottom of screen - old behaviour is now the default
            expand = 0
            side = tk.BOTTOM
        else:
            # Centre align
            expand = 1
            side = tk.TOP

        self.labelCurrent.pack(fill = tk.Y, expand = expand, anchor = anchor, side = side)

    def updateSlideTextCurrent(self, data):
        # Update the text label for the current slide
        if self.labelCurrent is None:
            return False

        if data['text'] is None:
            self.currentText = ""
            return None

        if self.splitLinesChar is not None and data['text'] is not None and self.splitLinesChar in data['text']:
            data['text'] = data['text'].split(self.splitLinesChar)
            data['text'] = data['text'][0]

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

        # We want the text to be updated by the main thread, not the ProPresenter thread
        if self.fontUppercase:
            self.currentText = textOutput.upper()
        elif not self.fontUppercase:
            self.currentText = textOutput

    def updateSlideTextNext(self, data):
        # Update the text label for the next slide
        if self.labelNext is None:
            return False

        if self.splitLinesChar is not None and data['text'] is not None and self.splitLinesChar in data['text']:
            data['text'] = data['text'].split(self.splitLinesChar)
            data['text'] = data['text'][0]

        # We want the text to be updated by the main thread, not the ProPresenter thread
        if data['text'] is not None and self.fontUppercase:
            self.nextText = data['text'].encode('utf-8').upper()
        elif data['text'] is not None and not self.fontUppercase:
            self.nextText = data['text'].encode('utf-8')
        else:
            self.nextText = ""
    
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
    
    def updatetext_tick(self):
        # Update text from the main thread (to try and avoid redraw issues)

        if self.labelCurrent is not None:
            self.labelCurrent.configure(text = self.currentText)
            self.update_idletasks()
        
        if self.labelNext is not None:
            self.labelNext.configure(text = self.nextText)
            self.update_idletasks()

        if self.labelCurrent is not None:
            self.labelCurrent.after(100, self.updatetext_tick)

if __name__ == "__main__":
    app = Application()
    app.master.title('ProPresenter Stage Display')
    app.clock_tick()
    app.updatetext_tick()
    app.mainloop()

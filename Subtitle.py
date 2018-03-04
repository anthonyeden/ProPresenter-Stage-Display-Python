import pygame
import ptext
import os
import json
import time
import sys
from ProPresenterStageDisplayClientComms import ProPresenterStageDisplayClientComms

class Application():

    screen = None
    windowHeight = 0
    windowWidth = 0
        
    # Store the threaded class for ProPresenter
    ProPresenter = None

    # Config data for ProPresenter
    ProP_IPAddress = None
    ProP_IPPort = None
    ProP_Password = None
    
    # Do we need to attempt a reconnection?
    tryReconnect = False
    disconnectTime = 0

    data = None
    
    subtitle = None
    
    def __init__(self):

        pygame.init()
        pygame.mouse.set_visible(False)
        
        screenInfo = pygame.display.Info()
               
        self.screen = pygame.display.set_mode((screenInfo.current_w, screenInfo.current_h), pygame.FULLSCREEN)
        
        pygame.display.flip()
        
        self.windowWidth = pygame.display.get_surface().get_width()
        self.windowHeight = pygame.display.get_surface().get_height()
        
        try:
            ConfigData_Filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), "subtitle-config.json")
            ConfigData_JSON = open(ConfigData_Filename).read()
            ConfigData = json.loads(ConfigData_JSON)
    
        except Exception, e:
            print
            print "##############################################"
            print "EXCEPTION: Cannot load and parse subtitle-config.json File: "
            print e
            print "##############################################"
            print        
            exit()
        
        try:
            self.ProP_IPAddress = ConfigData['IPAddress']
            self.ProP_IPPort = int(ConfigData['IPPort'])
            self.ProP_Password = ConfigData['Password']

            self.subtitle = ConfigData['Subtitle']             
                
        except Exception, e:
            print
            print "##############################################"
            print "EXCEPTION: Config file is missing a setting"
            print e
            print "##############################################"
            print            
            exit()
       
        self.update("Waiting for data ....")
        
        self.connect()
        
        clock = pygame.time.Clock()
        done = False         
        while not done:
            self.reconnect_tick()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.ProPresenter.stop()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.ProPresenter.stop()
                    pygame.quit()
                    sys.exit()
            
            clock.tick(60)
 
    def connect(self):
        # Connect to ProPresenter and setup the necessary callbacks
        self.tryReconnect = False
        self.disconnectTime = 0

        self.ProPresenter = ProPresenterStageDisplayClientComms(self.ProP_IPAddress, self.ProP_IPPort, self.ProP_Password)
        self.ProPresenter.addSubscription("CurrentSlide", self.update)
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
            
    def update(self, data):
        print "Updating... "

        if not isinstance(data, basestring): 
            data = data['text'].encode('utf-8').rstrip().strip()
            
        if (self.data != data):
            self.data = data
            self.screen.fill(tuple(self.subtitle['bgcolor']))
        
            if (self.subtitle['align'] == 'left'):
                bottom = self.windowHeight - self.subtitle['marginBottom']
                midtop = None
                left = self.subtitle['marginLeft']
            else:
                bottom = self.windowHeight - self.subtitle['marginBottom']
                midtop = (self.windowWidth / 2, 0)
                left = None
            
            ptext.draw(data, 
                bottom      = bottom, 
                midtop      = midtop,
                left        = left,                
                align       = str(self.subtitle['align']), 
                sysfontname = str(self.subtitle['sysfontname']), 
                fontsize    = float(self.subtitle['fontsize']), 
                color       = tuple(self.subtitle['color']), 
                shadow      = tuple(self.subtitle['shadow']), 
                scolor      = tuple(self.subtitle['scolor']), 
                owidth      = float(self.subtitle['owidth']), 
                ocolor      = tuple(self.subtitle['ocolor']))
            
            pygame.display.flip()
            
            print data
 
if __name__ == '__main__':
        app = Application()

"""ProPresenter Stage Display Client (Communication Class). An Open-Source Python Client for the ProPresenter6 Stage Display XML Feed."""

import socket
import errno
import time
import threading
import xml.etree.ElementTree as ET

__author__ = "Anthony Eden"
__copyright__ = "Copyright 2017, Anthony Eden / Media Realm"
__credits__ = ["Anthony Eden"]
__license__ = "GPL"
__version__ = "0.1"


class ProPresenterStageDisplayClientComms(threading.Thread):
    """This class handles all the communications with the ProPresenter Stage Display server."""

    # The handle for the socket connection to ProPresenter
    sock = None

    # A list of data types to subscribe to (with callbacks)
    dataSubscriptions = []

    # Should we be shutting down this thread? Set via self.stop()
    _stop = False
    
    # Store the password used to connect to the ProPresenter Stage Display socket
    password = ""

    def __init__(self, host, port, password):
        """Setup the class"""

        self.sock = None
        self.host = host
        self.port = port
        self.password = password
        self.dataSubscriptions = []

        # Start the thread
        threading.Thread.__init__(self)

    def stop(self):
        """Attempt to close this thread."""
        self._stop = True

    def run(self):
        """Create a socket connection to the ProPresenter server"""

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((self.host, self.port))
        except:
            # End the thread and call a callback
            self.doCallback("ConnectionFailed", "")
            self.stop()
        else:
            self.doCallback("Connected", "")
            self.sock.setblocking(0)
            self.loop()

    def loop(self):
        """A method that keeps going forever, and handles all the communication with the open ProPresenter socket."""

        # Login to ProPresenter
        self.sendCommand("<StageDisplayLogin>"+self.password+"</StageDisplayLogin>\r\n")

        while True:
            if self._stop is True:
                # End the thread
                self.sock.close()
                break

            # Try and receive data from ProPresenter
            recvData = self.recvUntilNewline()

            if recvData is False:
                self.sock.close()
                break

            if recvData is not None:
                self.processReceivedData(recvData)

            # Lower this number to receive data quicker
            time.sleep(0.1)

    def recvUntilNewline(self):
        """Receive data until we get to the end of a message."""
        totalData = ""
        inBlock = False

        while True:
            try:
                thisData = self.sock.recv(1024)

                if thisData == "":
                    # Connection closed
                    self.sock.close()
                    self.doCallback("Disconnected", "")
                    return False

                else:
                    totalData += thisData

            except socket.error, e:
                if e.args[0] != errno.EWOULDBLOCK:
                    self.sock.close()
                    self.doCallback("Disconnected", e)
                    return False

            else:
                # Check if we're in a data block
                if totalData[:80] == '<StageDisplayData>':
                    inBlock = True

                # Check if the datablock is over
                if "</StageDisplayData>" in totalData[-25:]:
                    return totalData
            
                if self._stop is True:
                    # End the thread
                    self.sock.close()
                    break

    def processReceivedData(self, recvData):
        """Process the received data from ProPresenter. Attempts to parse it and trigger the subscribed callback."""
        
        try:
            tree = ET.fromstring(recvData)
        except:
            # This is an unexpected data type. Ignore it for now...
            pass
        else:
        
            for fields in tree.findall('Fields'):
                for slideElement in fields.findall('Field'):
                    if 'identifier' in slideElement.attrib:
                        dataType = slideElement.attrib['identifier']
                        
                        # This dict will have all the data to return to our callbacks
                        returnData = {}
                        
                        # Send the actual text
                        returnData['text'] = slideElement.text
                        
                        # Send all the attributes
                        for i, key in enumerate(slideElement.attrib):
                            returnData[key] = slideElement.attrib[key]
                        
                        # Trigger a callback
                        self.doCallback(dataType, returnData)

    def sendCommand(self, msg):
        """Buffer a command to send."""
        self.sock.send(msg + "\r\n")
    
    def addSubscription(self, subType, callbackObj, limit=False, filters={}):
        """Add a subscription to the list of data subscriptions."""
        self.dataSubscriptions.append({
            "commandType": subType,
            "callback": callbackObj,
            "limit": limit
        })

    def doCallback(self, dataType, returnData):
        # Loop over every subscription
        for subI, subX in enumerate(self.dataSubscriptions):

            # If the subscribed command type matches the message's command type
            if dataType == subX['commandType']:

                # Execute the callback!
                subX['callback'](returnData)

                # Check if we need to decrement the limit
                if self.dataSubscriptions[subI]['limit'] is not False:
                    self.dataSubscriptions[subI]['limit'] = self.dataSubscriptions[subI]['limit'] - 1

                # Check if we need to remove this subscription
                if self.dataSubscriptions[subI]['limit'] <= 0 and self.dataSubscriptions[subI]['limit'] is not False:
                    self.dataSubscriptions.pop(subI)

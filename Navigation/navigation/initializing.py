import signal
import sys
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
from mission_control import MissionControl
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand
from communication.usb import Usb
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver

class Initializing():
    
    def __init__(self):
        self.lowLevelController = LowLevelController()
        self.missionControl = MissionControl(lowLevelController, Navigator(), PylonDetector())
        #TODO signal.signal(signal.SIGINT, stop)
        if Usb.hasWifiDongle():
            self.webserver = Webserver(missionControl)
            self.webserver.start()

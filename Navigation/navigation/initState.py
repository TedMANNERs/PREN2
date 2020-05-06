import signal
import sys
import logging
from mission_control import MissionControl
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand
from communication.usb import Usb
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver

class InitState():
    def __init__(self, missionControl: MissionControl):
        self.missionControl = missionControl

    #TODO: Does putting it into horwbotstatemachine make more sense? What about inheriting from NestedState?
    def initialize(self):
        self.missionControl.initialize()
        if Usb.hasWifiDongle():
            self.webserver = Webserver(self.missionControl)
            self.webserver.start()
        print("init_prepare")

import signal
import sys
from mission_control import MissionControl
from communication.lowLevelController import LowLevelController
from communication.usb import Usb
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver

def main():
    print("Start Navigation Software")
    missionControl = MissionControl(LowLevelController(), Navigator(), PylonDetector())
    #missionControl.start() #uncomment for testing
    signal.signal(signal.SIGINT, missionControl.stop) #intercept abort signal (e.g. Ctrl+C)
    
    if Usb.hasWifiDongle():
        webserver = Webserver(missionControl)
        webserver.start()
        pass

if __name__ == "__main__":
    main()
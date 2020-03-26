import signal
import sys
from mission_control import MissionControl
from communication.lowLevelController import LowLevelController
from communication.usb import Usb
from debugGui import app

def main():
    print("Start Navigation Software")
    missionControl = MissionControl(LowLevelController())
    #missionControl.start() #uncomment for testing
    signal.signal(signal.SIGINT, missionControl.stop) #intercept abort signal (e.g. Ctrl+C)
    
    if Usb.hasWifiDongle():
        app.start_webserver()

if __name__ == "__main__":
    main()
from mission_control import MissionControl
from communication.lowLevelController import LowLevelController
from communication.usb import Usb
from debugGui import app

def main():
    missionControl = MissionControl(LowLevelController())
    missionControl.start()
    
    if Usb.hasWifiDongle():
        app.start_server()

if __name__ == "__main__":
    main()

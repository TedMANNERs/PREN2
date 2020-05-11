#!/usr/bin/env python3
"""
This is the entry point of the Horwbot Navigation Software. 
*more header text goes here*

use "-O" argument to run the program in release mode (Removes asserts and __debug__).
"""
import signal
import sys
import logging
logging.basicConfig(filename='logs/horwlog.log', filemode='w', format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
from mission_control import MissionControl
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand
from communication.usb import Usb
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver

def main():
    
    def stop(sig, frame):
        logging.info("Ctrl + C pressed, terminating...")
        missionControl.stop()
        lowLevelController.stopListening()
        sys.exit(0)

    logging.info("Start Navigation Software")
    lowLevelController = LowLevelController()
    missionControl = MissionControl(lowLevelController, Navigator(), PylonDetector())
    signal.signal(signal.SIGINT, stop) #intercept abort signal (e.g. Ctrl+C)
    
    if Usb.hasWifiDongle():
        webserver = Webserver(missionControl)
        webserver.start()
    
    while True:
        value = input("Enter command: 1=Start, 2=Stop, 3X=Audio (X: 1=ShortBeep, 2=LongBeep), 4X=LED (X: 0=off, 1=on), <Enter>=Terminate\n")
        if value == "":
            missionControl.stop()
            break
        handle_command(value, missionControl, lowLevelController)
        
    lowLevelController.stopListening()


def handle_command(command, missionControl, lowLevelController):
    if command == "1":
        missionControl.start()
    elif command == "2":
        lowLevelController.sendStop()
        missionControl.stop()
    elif command.startswith("3"):
        if command.endswith("1"):
            lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        elif command.endswith("2"):
            lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        else:
            logging.error("Invalid audio command!")
    elif command.startswith("4"):
        if command.endswith("0"):
            lowLevelController.sendLED(LEDCommand.Off)
        elif command.endswith("1"):
            lowLevelController.sendLED(LEDCommand.On)
        else:
            logging.error("Invalid LED command!")
    else:
        logging.error("Invalid LED command!")

if __name__ == "__main__":
    main()
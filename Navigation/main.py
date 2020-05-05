#!/usr/bin/env python3
"""
This is the entry point of the Horwbot Navigation Software. 
*more header text goes here*
"""
import signal
import sys
import logging
from mission_control import MissionControl
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand
from communication.usb import Usb
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver
from navigation.horwbotstatemachine import HorwbotStateMachine

def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s', level=logging.DEBUG)

    def stop(sig, frame):
        logging.info("Ctrl + C pressed, terminating...")
        state_machine.stop() #TODO: Fix pylint error
        sys.exit(0)
        
    lowLevelController = LowLevelController()
    missionControl = MissionControl(lowLevelController, Navigator(), PylonDetector())
    state_machine = HorwbotStateMachine(missionControl)
    signal.signal(signal.SIGINT, stop) #intercept abort signal (e.g. Ctrl+C)
    logging.info("State = %s", state_machine.states)
    state_machine.initialize() #TODO: Fix pylint error

    # TODO: Migrate the code below to state machine

    # logging.info("Start Navigation Software")
    # lowLevelController = LowLevelController()
    # missionControl = MissionControl(lowLevelController, Navigator(), PylonDetector())
    # signal.signal(signal.SIGINT, stop) #intercept abort signal (e.g. Ctrl+C)
    
    # if Usb.hasWifiDongle():
    #     webserver = Webserver(missionControl)
    #     webserver.start()
    
    # while True:
    #     value = input("Enter command: 1=Start, 2=Stop, 3X=Audio (X: 1=ShortBeep, 2=LongBeep), 4X=LED (X: 0=off, 1=on), <Enter>=Terminate\n")
    #     if value == "":
    #         missionControl.stop()
    #         break
    #     handle_command(value, missionControl, lowLevelController)
        
    # lowLevelController.stopListening()


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
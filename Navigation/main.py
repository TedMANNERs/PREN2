#!/usr/bin/env python3
"""
This is the entry point of the Horwbot Navigation Software. 
*more header text goes here*

use "-O" argument to run the program in release mode (Removes asserts and __debug__).
"""
import signal
import sys
import logging
from communication.lowLevelController import AudioCommand, LEDCommand
from navigation.horwbotstatemachine import HorwbotStateMachine
from mission_control import MissionControl
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from communication.lowLevelController import LowLevelController

def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s', level=logging.DEBUG)
    logging.getLogger('transitions').setLevel(logging.INFO)

    def stop(sig, frame):
        logging.info("Ctrl + C pressed, terminating...")
        mission_control.abort()
        sys.exit(0)
        
    logging.info("Start Navigation Software")
    state_machine = HorwbotStateMachine()
    mission_control = MissionControl(LowLevelController(), Navigator(), PylonDetector(), state_machine)
    signal.signal(signal.SIGINT, stop) #intercept abort signal (e.g. Ctrl+C)
    logging.info("State = %s", state_machine.states)
    mission_control.initialize()
    
    while True:
        value = input("Enter command: 1=Start, 2=Stop, 3X=Audio (X: 1=ShortBeep, 2=LongBeep), 4X=LED (X: 0=off, 1=on), q=Terminate\n")
        if value == "q":
            break
        try:
            handle_command(value, mission_control)
        except Exception as error:
            logging.error(error)
        
    mission_control.abort()


def handle_command(command, mission_control: MissionControl):
    if command == "1":
        mission_control.start()
    elif command == "2":
        mission_control.stop()
    elif command.startswith("3"):
        if command.endswith("1"):
            mission_control.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        elif command.endswith("2"):
            mission_control.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        else:
            logging.error("Invalid audio command!")
    elif command.startswith("4"):
        if command.endswith("0"):
            mission_control.lowLevelController.sendLED(LEDCommand.Off)
        elif command.endswith("1"):
            mission_control.lowLevelController.sendLED(LEDCommand.On)
        else:
            logging.error("Invalid LED command!")
    else:
        logging.error("Invalid command!")

if __name__ == "__main__":
    main()
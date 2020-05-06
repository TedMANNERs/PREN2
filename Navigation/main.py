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

def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s', level=logging.DEBUG)

    def stop(sig, frame):
        logging.info("Ctrl + C pressed, terminating...")
        state_machine.abort() #TODO: Fix pylint error
        sys.exit(0)
        
    logging.info("Start Navigation Software")
    state_machine = HorwbotStateMachine()
    signal.signal(signal.SIGINT, stop) #intercept abort signal (e.g. Ctrl+C)
    logging.info("State = %s", state_machine.states)
    state_machine.initialize() #TODO: Fix pylint error
    
    while True:
        value = input("Enter command: 1=Start, 2=Stop, 3X=Audio (X: 1=ShortBeep, 2=LongBeep), 4X=LED (X: 0=off, 1=on), <Enter>=Terminate\n")
        if value == "":
            break
        handle_command(value, state_machine)
        
    state_machine.abort() #TODO: Fix pylint error


def handle_command(command, state_machine: HorwbotStateMachine):
    if command == "1":
        state_machine.start()
    elif command == "2":
        state_machine.stop()
    elif command.startswith("3"):
        if command.endswith("1"):
            state_machine.missionControl.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        elif command.endswith("2"):
            state_machine.missionControl.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        else:
            logging.error("Invalid audio command!")
    elif command.startswith("4"):
        if command.endswith("0"):
            state_machine.missionControl.lowLevelController.sendLED(LEDCommand.Off)
        elif command.endswith("1"):
            state_machine.missionControl.lowLevelController.sendLED(LEDCommand.On)
        else:
            logging.error("Invalid LED command!")
    else:
        logging.error("Invalid LED command!")

if __name__ == "__main__":
    main()
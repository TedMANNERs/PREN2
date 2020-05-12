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
from horwbot_state_machine import HorwbotStateMachine
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from communication.lowLevelController import LowLevelController

def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s', level=logging.DEBUG)
    logging.getLogger('transitions').setLevel(logging.INFO)

    def abort(sig, frame):
        logging.info("Ctrl + C pressed, terminating...")
        state_machine.abort()
        sys.exit(0)
    
    try:
        logging.info("Start Navigation Software")
        llc = LowLevelController()
        state_machine = HorwbotStateMachine(llc, PylonDetector(), Navigator())
        signal.signal(signal.SIGINT, abort) #intercept abort signal (e.g. Ctrl+C)
        logging.info("State = %s", state_machine.state)
        state_machine.initialize()
    except Exception as e:
        logging.error(e)
        state_machine.fail(e)
    
    while True:
        value = input("Enter command: 1=Start, 2=Stop, 3X=Audio (X: 1=ShortBeep, 2=LongBeep), 4X=LED (X: 0=off, 1=on), q=Terminate\n")
        if value == "q":
            break
        try:
            handle_command(value, state_machine, llc)
        except Exception as e:
            logging.error(e)
            state_machine.fail(e)
        
    state_machine.abort()


def handle_command(command, state_machine: HorwbotStateMachine, llc: LowLevelController):
    if command == "1":
        state_machine.start()
    elif command == "2":
        state_machine.stop()
    elif command.startswith("3"):
        if command.endswith("1"):
            llc.sendPlayAudio(AudioCommand.ShortBeep)
        elif command.endswith("2"):
            llc.sendPlayAudio(AudioCommand.LongBeep)
        else:
            logging.error("Invalid audio command!")
    elif command.startswith("4"):
        if command.endswith("0"):
            llc.sendLED(LEDCommand.Off)
        elif command.endswith("1"):
            llc.sendLED(LEDCommand.On)
        else:
            logging.error("Invalid LED command!")
    else:
        logging.error("Invalid command!")

if __name__ == "__main__":
    main()
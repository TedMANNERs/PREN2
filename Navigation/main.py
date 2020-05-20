#!/usr/bin/env python3
"""
This is the entry point of the Horwbot Navigation Software. 
*more header text goes here*

use "-O" argument to run the program in release mode (Removes asserts and __debug__).
"""
import signal
import sys
import logging
from threading import Thread
from communication.lowLevelController import AudioCommand, LEDCommand
from mission_control import MissionControl
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from communication.lowLevelController import LowLevelController
from debugGui.debugInfo import DebugInfo

def main():
    logging.basicConfig(
        format='%(asctime)s {%(module)s:%(lineno)d} %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler("horwlog.log",mode='a'),
            logging.StreamHandler()
        ]
    )
    logging.getLogger('transitions').setLevel(logging.INFO)
    _isRunning = True

    def abort(sig, frame):
        logging.info("Ctrl + C pressed, terminating...")
        mission_control.abort()
        _isRunning = False
        sys.exit(0)
    
    def updateDebugWindows(): 
        while _isRunning:
            DebugInfo.showLatestFrame()
            DebugInfo.showStateDiagram()
    try:
        logging.info("Start Navigation Software")
        llc = LowLevelController()
        mission_control = MissionControl(llc, PylonDetector(), Navigator())
        signal.signal(signal.SIGINT, abort) #intercept abort signal (e.g. Ctrl+C)
        logging.info("State = %s", mission_control.state)
        isSimulation = len(sys.argv) >= 2 and sys.argv[1] == "simulation"
        mission_control.initialize(isSimulation)
    except Exception as e:
        logging.error(e)
        mission_control.fail(e)

    if __debug__:
        debugWindowThread = Thread(target=updateDebugWindows)
        debugWindowThread.start()

    while True:
        value = input("Enter command: 1=Start, 2=Stop, 3X=Audio (X: 1=ShortBeep, 2=LongBeep), 4X=LED (X: 0=off, 1=on), q=Terminate\n")
        if value == "q":
            break
        try:
            handle_command(value, mission_control, llc)
        except Exception as e:
            logging.error(e)
            mission_control.fail(e)
        
    mission_control.abort()

def handle_command(command, mission_control: MissionControl, llc: LowLevelController):
    if command == "1":
        mission_control.start()
    elif command == "2":
        mission_control.stop()
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
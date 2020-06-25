#!/usr/bin/env python3
import logging
import os,sys,time
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import numpy as np
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand
from navigation.navigator import Navigator
from common.dataTypes import TargetVector
from common.timer import Timer

def move(llc: LowLevelController, getVectorFunction):
    timer = Timer()
    timer.start()
    while(timer.getElapsedTime() < 5): #Seconds
        llc.sendTargetVector(getVectorFunction())
        time.sleep(0.05)
    timer.stop()
    llc.sendStop()

def llc_test():
    logging.basicConfig(
        format='%(asctime)s %(levelname)s {%(module)s:%(lineno)d}     %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG
    )

    llc = LowLevelController()
    navigator = Navigator()

    llc.startListening()
    time.sleep(2)
    llc.sendStart()
    while True:
        value = input("Enter command: w=Forward, s=Reverse, a=TurnLeft, d=TurnRight, q=Terminate\n")
        if value == "q":
            llc.sendStop()
            time.sleep(1)
            llc.stopListening()
            break
        try:
            if value == "w":
                move(llc, navigator._getMoveStraightVector)
            elif value == "s":
                move(llc, navigator._getReverseVector)
            elif value == "a":
                move(llc, navigator._getTurnLeftVector)
            elif value == "d":
                move(llc, navigator._getTurnRightVector)
        except Exception as e:
            logging.exception(e)
    

if __name__ == "__main__":
    llc_test()

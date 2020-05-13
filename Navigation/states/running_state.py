import threading
import logging
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand
from imageDetection.pylonDetector import PylonDetector
from navigation.navigator import Navigator
from states.running.searching_state import SearchingState
from states.running.navigating_state import NavigatingState
from states.running.reversing_state import ReversingState
from states.running.crossingObstacle_state import CrossingObstacleState
from states.running.emergency_state import EmergencyState
from states.running.parcoursCompleted_state import ParcoursCompletedState

class RunningState(NestedState):
    def __init__(self, llc: LowLevelController, detector: PylonDetector, navigator: Navigator, mission_control):
        self.lowLevelController = llc
        self.pylonDetector = detector
        self.navigator = navigator
        self.mission_control = mission_control

        self.substate = None

        super().__init__(name='running', on_enter=self.onEnter, on_exit=self.onExit, initial='searching')
        self.add_substates([
                    SearchingState(self, llc, detector, navigator),
                    NavigatingState(self, llc, detector, navigator),
                    ReversingState(self),
                    CrossingObstacleState(self),
                    EmergencyState(self),
                    ParcoursCompletedState(self)
                ])

    def onEnter(self, event):
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendLED(LEDCommand.On)
        self._isRunning = True
        self._loopThread = threading.Thread(target=self._loop)
        self._loopThread.start()

    def onExit(self, event):
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.sendLED(LEDCommand.Off)
        self._isRunning = False

    def _loop(self):
        try:
            while (self._isRunning):
                if self.substate:
                    self.substate.loop()
        except Exception as e:
            logging.error("Substate: %s, %s", self.substate, e)
            self.mission_control.fail(e)
import threading
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand
from imageDetection.pylonDetector import PylonDetector
from navigation.navigator import Navigator
from states.running.searching_state import SearchingState

class RunningState(NestedState):
    def __init__(self, llc: LowLevelController, detector: PylonDetector, navigator: Navigator, state_machine):
        self.lowLevelController = llc
        self.pylonDetector = detector
        self.navigator = navigator
        self.substate = None
        super().__init__(name='running', on_enter=self.onEnter, on_exit=self.onExit, initial='searching')
        self.add_substates([
                    SearchingState(llc, detector, navigator, self),
                    NestedState(name='movingToPylon'),
                    NestedState(name='reversing'),
                    NestedState(name='crossingObstacle'),
                    NestedState(name='emergencyMode'),
                    NestedState(name='parcourCompleted')
                ])

    def onEnter(self):
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendLED(LEDCommand.On)
        self._isRunning = True
        self._loopThread = threading.Thread(target=self._loop)
        self._loopThread.start()

    def onExit(self):
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.sendLED(LEDCommand.Off)
        self._isRunning = False

    def _loop(self):
        while (self._isRunning):
            if self.substate:
                self.substate.loop()
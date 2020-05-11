from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand
from imageDetection.pylonDetector import PylonDetector
from navigation.navigator import Navigator
from states.running.searching_state import SearchingState

class RunningState(NestedState):
    def __init__(self, llc: LowLevelController, detector: PylonDetector, navigator: Navigator):
        self.lowLevelController = llc
        self.pylonDetector = detector
        self.navigator = navigator
        super().__init__(name='running', on_enter=self.onEnter, on_exit=self.onExit, initial='searching', children=[
                    SearchingState(llc, detector, navigator),
                    NestedState(name='movingToPylon'),
                    'reversing', 'crossingObstacle', 'emergencyMode',
                    NestedState(name='parcourCompleted')
                ])

    def onEnter(self):
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendLED(LEDCommand.On)

    def onExit(self):
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.sendLED(LEDCommand.Off)
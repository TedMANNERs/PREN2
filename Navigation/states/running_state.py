from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand

class RunningState(NestedState):
    def __init__(self, lowLevelController: LowLevelController):
        self.lowLevelController = lowLevelController
        super().__init__(name='running', on_enter=self.onEnter, initial='searching', children=[
                    NestedState(name='searching'),
                    NestedState(name='movingToPylon'),
                    'reversing', 'crossingObstacle', 'emergencyMode',
                    NestedState(name='parcourCompleted')
                ])

    def onEnter(self):
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendLED(LEDCommand.On)
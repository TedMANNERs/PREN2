from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand

class ErrorState(NestedState):
    def __init__(self, lowLevelController: LowLevelController):
        self.lowLevelController = lowLevelController
        super().__init__(name='error', on_enter=self.onEnter)

    def onEnter(self):
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand

class AbortedState(NestedState):
    def __init__(self, lowLevelController: LowLevelController):
        self.lowLevelController = lowLevelController
        super().__init__(name='aborted', on_enter=self.onEnter)

    def onEnter(self):
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.LongBeep)
        self.lowLevelController.sendLED(LEDCommand.Off)
        self.lowLevelController.stopListening()
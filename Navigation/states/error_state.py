from transitions.extensions.nesting import NestedState
from transitions import MachineError
from communication.lowLevelController import LowLevelController, AudioCommand, LEDCommand

class ErrorState(NestedState):
    def __init__(self, lowLevelController: LowLevelController):
        self.lowLevelController = lowLevelController
        super().__init__(name='error', on_enter=self.onEnter, on_exit=self.onExit)

    def onEnter(self, event):
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        self.lowLevelController.sendPlayAudio(AudioCommand.ShortBeep)
        error = event.args[0]
        if isinstance(error, MachineError):
            if event.source_name == 'ready':
                event.machine.recoverReady()
            elif event.source_name ==  'running':
                event.machine.recoverRunning()
            else:
                event.machine.abort()

    def onExit(self, event):
        pass
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, AudioCommand

class AbortedState(NestedState):
    def __init__(self, lowLevelController: LowLevelController):
        self.lowLevelController = lowLevelController
        super().__init__(name='aborted', on_enter=self.onEnter)

    def onEnter(self, event):
        self.lowLevelController.stopListening()

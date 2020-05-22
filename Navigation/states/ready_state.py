from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController

class ReadyState(NestedState):
    def __init__(self, llc: LowLevelController):
        self.llc = llc
        super().__init__(name='ready', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self, event):
        pass

    def onExit(self, event):
        pass

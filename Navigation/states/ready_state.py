from transitions.extensions.nesting import NestedState

class ReadyState(NestedState):
    def __init__(self):
        super().__init__(name='ready', on_exit=self.onExit, on_enter=self.onEnter)
    
    def onExit(self):
        pass

    def onEnter(self):
        pass
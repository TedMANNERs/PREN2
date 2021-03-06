from transitions.extensions.nesting import NestedState

class ReversingState(NestedState):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(name='reversing', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self, event):
        self.parent.substate = self

    def loop(self):
        pass

    def onExit(self, event):
        pass
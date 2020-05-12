from transitions.extensions.nesting import NestedState

class MovingToPylonState(NestedState):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(name='movingToPylon', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self):
        self.parent.substate = self

    def loop(self):
        pass

    def onExit(self):
        pass
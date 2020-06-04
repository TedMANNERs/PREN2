import logging
from transitions.extensions.nesting import NestedState

class EmergencyState(NestedState):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(name='emergency', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self, event):
        self.parent.substate = self
        logging.info("EMERGENCY TRIGGERED - Stopping...")
        self.parent.mission_control.stop()

    def loop(self):
        pass

    def onExit(self, event):
        pass
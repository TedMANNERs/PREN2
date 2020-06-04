import logging
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController

class ParcoursCompletedState(NestedState):
    def __init__(self, llc: LowLevelController):
        self.llc = llc
        super().__init__(name='parcoursCompleted', on_enter=self.onEnter)
    
    def onEnter(self, event):
        logging.info("PARCOURS COMPLETED")
        self.llc.stopListening()
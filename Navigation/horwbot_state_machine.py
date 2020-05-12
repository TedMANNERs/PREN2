import cv2
import numpy as np
import logging
from transitions.extensions.nesting import NestedState
from transitions.extensions import HierarchicalGraphMachine
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver
from debugGui.debugInfo import DebugInfo
from communication.lowLevelController import LowLevelController
from states.init_state import InitState
from states.ready_state import ReadyState
from states.aborted_state import AbortedState
from states.running_state import RunningState
from states.error_state import ErrorState

class HorwbotStateMachine(HierarchicalGraphMachine):
    def __init__(self, llc: LowLevelController, detector: PylonDetector, navigator: Navigator):
        states = [InitState(llc, detector), ReadyState(), ErrorState(llc), AbortedState(llc), RunningState(llc, detector, navigator, self)]
        transitions = [
            { 'trigger': 'initialize', 'source': 'init', 'dest': 'ready'},
            { 'trigger': 'start', 'source': 'ready', 'dest': 'running'},
            { 'trigger': 'moveToPylon', 'source': 'running_searching', 'dest': 'running_movingToPylon'},
            { 'trigger': 'reverse', 'source': 'running_searching', 'dest': 'running_reversing'},
            { 'trigger': 'cross', 'source': 'running_searching', 'dest': 'running_crossingObstacle'},
            { 'trigger': 'abort', 'source': ['ready', 'running'], 'dest': 'aborted'},
            { 'trigger': 'stop', 'source': 'running', 'dest': 'ready'},
            { 'trigger': 'panic', 'source': 'running_searching', 'dest': 'running_emergencyMode'},
            { 'trigger': 'search', 'source': ['running_movingToPylon', 'running_reversing', 'running_crossingObstacle', 'running_emergencyMode'], 'dest': 'running_searching'},
            { 'trigger': 'search', 'source': 'running_searching', 'dest': '='},
            { 'trigger': 'endParcour', 'source': 'running_searching', 'dest': 'running_parcourCompleted'},
            { 'trigger': 'recover', 'source': 'error', 'dest': 'ready'},
            { 'trigger': 'fail', 'source': '*', 'dest': 'error'}
        ]
        super().__init__(model=self, states=states, transitions=transitions, initial='init', after_state_change='on_state_changed')

    def on_state_changed(self):
        graph = self.model.get_graph()
        buffer = graph.pipe(format='png')
        nparr = np.fromstring(buffer, np.uint8)
        DebugInfo.stateDiagram = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if __debug__:
            DebugInfo.showStateDiagram()

    def execute_moveForward(self): pass
       
    def execute_moveBackward(self): pass
    
    def execute_crossing(self): pass
        
    def execute_goToEmergency(self): pass
    
    def execute_backToSearch(self): pass

    def execute_stayInSearch(self): pass

    def execute_endParcour(self): pass

    def execute_errorHandling(self): pass

    def execute_goToError(self): pass

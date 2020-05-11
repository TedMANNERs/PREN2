import cv2
import numpy as np
import logging
from transitions.extensions.nesting import NestedState
from transitions.extensions import HierarchicalGraphMachine
from mission_control import MissionControl
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver
from debugGui.debugInfo import DebugInfo
from communication.lowLevelController import LowLevelController

class HorwbotStateMachine(HierarchicalGraphMachine):
    def __init__(self):
        states = ['init', 'ready', 'error', 'aborted',
            {'name': 'running', 'initial': 'searching', 'children':[
                    NestedState(name='searching', on_enter=['searching_on_enter']),
                    NestedState(name='movingToPylon', on_enter=['movingToPylon_on_enter']),
                    'reversing', 'crossingObstacle', 'emergencyMode',
                    NestedState(name='parcourCompleted', on_enter=['parcourCompleted_on_enter'])
                ]
            }]
        transitions = [
            { 'trigger': 'initialized', 'source': 'init', 'dest': 'ready'},
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
    
    def parcourCompleted_on_enter(self):
        logging.info("Mission was successful!")

    def searching_on_enter(self):
        try:
            self.missionControl.search()
        except Exception as error:
            logging.error(error)
            self.fail()

    def movingToPylon_on_enter(self):
        self.missionControl.moveToNextPylon()

    def execute_moveForward(self): pass
       
    def execute_moveBackward(self): pass
    
    def execute_crossing(self): pass
        
    def execute_goToEmergency(self): pass
    
    def execute_backToSearch(self): pass

    def execute_stayInSearch(self): pass

    def execute_endParcour(self): pass

    def execute_errorHandling(self): pass

    def execute_goToError(self): pass

from transitions.extensions.nesting import NestedState
from transitions.extensions import HierarchicalGraphMachine
from navigation.initState import InitState
from mission_control import MissionControl
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver
from communication.lowLevelController import LowLevelController


class HorwbotStateMachine(HierarchicalGraphMachine):
    def __init__(self):
        states = [NestedState(name='init', on_exit=['init_on_exit']), 'ready', 'error', 'aborted',{'name': 'running', 'children':['searching', 'movingToPylon', 'reversing', 'crossingObstacle', 'emergencyMode', 'parcourCompleted']}]
        transitions = [
                { 'trigger': 'initialize', 'source': 'init', 'dest': 'ready', 'prepare': 'execute_initialize'},
                { 'trigger': 'start', 'source': 'ready', 'dest': 'running_searching', 'prepare': 'execute_start'},
                { 'trigger': 'moveForward', 'source': 'running_searching', 'dest': 'running_movingToPylon'},
                { 'trigger': 'reverse', 'source': 'running_searching', 'dest': 'running_reversing'},
                { 'trigger': 'cross', 'source': 'running_searching', 'dest': 'running_crossingObstacle'},
                { 'trigger': 'abort', 'source': ['ready', 'running'], 'dest': 'aborted', 'prepare': 'execute_abort'},
                { 'trigger': 'stop', 'source': 'running', 'dest': 'ready', 'prepare': 'execute_stop'},
                { 'trigger': 'panic', 'source': 'running_searching', 'dest': 'running_emergencyMode'},
                { 'trigger': 'search', 'source': ['running_movingToPylon', 'running_reversing', 'running_crossingObstacle', 'running_emergencyMode'], 'dest': 'running_searching'},
                { 'trigger': 'search', 'source': 'running_searching', 'dest': '='},
                { 'trigger': 'endParcour', 'source': 'running_searching', 'dest': 'running_parcourCompleted'},
                { 'trigger': 'recover', 'source': 'error', 'dest': 'ready'},
                { 'trigger': 'fail', 'source': '*', 'dest': 'error'}
        ]
        super().__init__(model=self, states=states, transitions=transitions, initial='init')
        lowLevelController = LowLevelController()
        self.missionControl = MissionControl(lowLevelController, Navigator(), PylonDetector())
        self.initState = InitState(self.missionControl)

    def init_on_exit(self): 
        print("Exit init")

    def execute_initialize(self):
        self.initState.initialize()
       
    def execute_abort(self):
        self.missionControl.abort()

    def execute_stop(self):
        self.missionControl.stop()
       
    def execute_start(self):
        self.missionControl.start()

    def execute_moveForward(self): pass
       
    def execute_moveBackward(self): pass
    
    def execute_crossing(self): pass
        
    def execute_goToEmergency(self): pass
    
    def execute_backToSearch(self): pass

    def execute_stayInSearch(self): pass

    def execute_endParcour(self): pass

    def execute_errorHandling(self): pass

    def execute_goToError(self): pass

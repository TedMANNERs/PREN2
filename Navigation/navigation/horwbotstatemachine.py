from transitions.extensions.nesting import NestedState
from transitions.extensions import HierarchicalMachine as Machine
from navigation.initState import InitState
from mission_control import MissionControl


class HorwbotStateMachine:
    
    states = [NestedState(name='init', on_exit=['init_on_exit']), 'ready', 'error', 'stopped', {'name': 'running', 'children':['searching', 'movingToPylon', 'reversing', 'crossingObstacle', 'emergencyMode', 'parcourCompleted']}]
    transitions = [
            { 'trigger': 'initialize', 'source': 'init', 'dest': 'ready', 'prepare': 'execute_initialize'},
            { 'trigger': 'startSearching', 'source': 'ready', 'dest': 'running_searching'},
            { 'trigger': 'moveForward', 'source': 'running_searching', 'dest': 'running_movingToPylon'},
            { 'trigger': 'moveBackward', 'source': 'running_searching', 'dest': 'running_reversing'},
            { 'trigger': 'crossing', 'source': 'running_searching', 'dest': 'running_crossingObstacle'},
            { 'trigger': 'stop', 'source': 'running', 'dest': 'stopped', 'prepare': 'execute_stop'},
            { 'trigger': 'goToEmergency', 'source': 'running_searching', 'dest': 'running_emergencyMode'},
            { 'trigger': 'backToSearch', 'source': ['running_movingToPylon', 'running_reversing', 'running_crossingObstacle', 'running_emergencyMode'], 'dest': 'running_searching'},
            { 'trigger': 'stayInSearch', 'source': 'running_searching', 'dest': '='},
            { 'trigger': 'endParcour', 'source': 'running_searching', 'dest': 'running_parcourCompleted'},
            { 'trigger': 'errorHandling', 'source': 'error', 'dest': 'ready'},
            { 'trigger': 'goToError', 'source': '*', 'dest': 'error'}
    ]

    def __init__(self, missionControl: MissionControl):
        self.missionControl = missionControl
        self.machine = Machine(model=self, states=HorwbotStateMachine.states, transitions=HorwbotStateMachine.transitions, initial='init')
        self.initState = InitState(self.missionControl)

    def init_on_exit(self): 
        print("Exit init")

    def execute_initialize(self): 
        self.initState.initialize()
       
    def execute_stop(self):
        self.missionControl.stop()
        self.missionControl.lowLevelController.stopListening()
       
    def execute_startSearching(self): pass

    def execute_moveForward(self): pass
       
    def execute_moveBackward(self): pass
    
    def execute_crossing(self): pass
        
    def execute_goToEmergency(self): pass
    
    def execute_backToSearch(self): pass

    def execute_stayInSearch(self): pass

    def execute_endParcour(self): pass

    def execute_errorHandling(self): pass

    def execute_goToError(self): pass

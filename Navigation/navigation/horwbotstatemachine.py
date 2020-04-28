from transitions.extensions import HierarchicalMachine as Machine
from navigation.initializing import Initializing


class HorwbotStateMachine(object):
    init_instance = None
    state = ['init', 'ready', 'error', {'name': 'running', 'children':['searching', 'movingToPylon', 'reversing', 'crossingObstacle', 'stopped', 'emergencyMode', 'parcourCompleted']}]
    transitions = [
            { 'trigger': 'initializing', 'source': 'init', 'dest': 'ready', 'prepare': 'execute_initializing'},
            { 'trigger': 'startSearching', 'source': 'ready', 'dest': 'running_searching'},
            { 'trigger': 'moveForward', 'source': 'running_searching', 'dest': 'running_movingToPylon'},
            { 'trigger': 'moveBackward', 'source': 'running_searching', 'dest': 'running_reversing'},
            { 'trigger': 'crossing', 'source': 'running_searching', 'dest': 'running_crossingObstacle'},
            { 'trigger': 'stopping', 'source': 'running_searching', 'dest': 'running_stopped'},
            { 'trigger': 'goToEmergency', 'source': 'running_searching', 'dest': 'running_emergencyMode'},
            { 'trigger': 'backToSearch', 'source': ['running_movingToPylon', 'running_reversing', 'running_crossingObstacle', 'running_stopped', 'running_emergencyMode'], 'dest': 'running_searching'},
            { 'trigger': 'stayInSearch', 'source': 'running_searching', 'dest': '='},
            { 'trigger': 'endParcour', 'source': 'running_searching', 'dest': 'running_parcourCompleted'},
            { 'trigger': 'errorHandling', 'source': 'error', 'dest': 'ready'},
            { 'trigger': 'goToError', 'source': '*', 'dest': 'error'}
    ]

    def __init__(self):
        self.machine = Machine(model=self, states=HorwbotStateMachine.state, transitions=HorwbotStateMachine.transitions, initial='init')

    def execute_initializing(self): 
        self.init_instance = Initializing()
        self.init_instance.initializing_navigation_components()
       
    def execute_startSearching(self): pass

    def execute_moveForward(self): pass
       
    def execute_moveBackward(self): pass
    
    def execute_crossing(self): pass
      
    def execute_stopping(self): pass
        
    def execute_goToEmergency(self): pass
    
    def execute_backToSearch(self): pass

    def execute_stayInSearch(self): pass

    def execute_endParcour(self): pass

    def execute_errorHandling(self): pass

    def execute_goToError(self): pass

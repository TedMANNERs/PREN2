from transitions.extensions import HierarchicalMachine as Machine

class HorwbotStateMachine(object):
    state = ['init', 'ready', 'error', {'name': 'running', 'children':['searching', 'movingToPylon', 'reversing', 'crossingObstacle', 'stopped', 'emergencyMode', 'parcourCompleted']}]
    transitions = [
            { 'trigger': 'initializing', 'source': 'init', 'dest': 'ready', 'prepare': 'hello'},
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

    def hello(self): print("Hello")

m = HorwbotStateMachine()
print(m.state)
m.initializing()


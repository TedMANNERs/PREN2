from transitions.extensions import HierarchicalMachine as Machine

class HorwbotStateMachine(object):
    state = ['init', 'ready', 'error', {'name': 'running', 'children':['searching', 'movingToPylon', 'reversing', 'crossingObstacle', 'stopped', 'emergencyMode', 'parcourCompleted']}]
    transitions = [
            ['initializing', 'init', 'ready'],
            ['startSearching', 'ready', 'running_searching'],
            ['moveForward', 'running_searching', 'running_movingToPylon'],
            ['moveBackward', 'running_searching', 'running_reversing'],
            ['crossing', 'running_searching', 'running_crossingObstacle'],
            ['stopping', 'running_searching', 'running_stopped'],
            ['goToEmergency', 'running_searching', 'running_emergencyMode'],
            ['backToSearch', ['running_movingToPylon', 'running_reversing', 'running_crossingObstacle', 'running_stopped', 'running_emergencyMode'], 'running_searching'],
            ['stayInSearch', 'running_searching', '='],
            ['endParcour', 'running_searching', 'running_parcourCompleted'], 
            ['errorHandling', 'error', 'ready'],
            ['goToError', '*', 'error']
    ]

    def __init__(self):
        self.machine = Machine(model=self, states=HorwbotStateMachine.state, transitions=HorwbotStateMachine.transitions, initial='init')




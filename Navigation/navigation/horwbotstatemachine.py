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

    def __init__(self, name):
        self.name = name
        self.machine = Machine(model=self, states=HorwbotStateMachine.state, transitions=HorwbotStateMachine.transitions, initial='init')



# Tests
# TODO Extract to Testclass
# TODO Extend tests
m = HorwbotStateMachine("m")
print(m.state)
m.initializing()
print(m.state)
m.startSearching()
print(m.state)
m.moveForward()
print(m.state)
m.backToSearch()
print(m.state)
m.moveBackward()
print(m.state)
m.backToSearch()
print(m.state)
m.crossing()
print(m.state)
m.backToSearch()
print(m.state)
m.stopping()
print(m.state)
m.backToSearch()
print(m.state)
m.goToEmergency()
print(m.state)
m.backToSearch()
print(m.state)
m.goToError()
print(m.state)
m.errorHandling()
print(m.state)
m.startSearching()
print(m.state)
m.endParcour()
print(m.state)




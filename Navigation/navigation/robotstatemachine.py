from statemachine import StateMachine, State

class RobotStateMachine(StateMachine):

    #Defining States
    ready = State('Ready', initial=True)
    searching = State('Searching')
    movingToPylon = State('MovingToPylon')
    reversing = State('Reversing')
    crossingObstacle = State('CrossingObstacle')
    stopped = State('Stopped')
    emergencyMode = State('EmergencyMode')
    parcoursCompleted = State('ParcoursCompleted')

    #Transitions
    startSearching = ready.to(searching)
    moveForward = searching.to(movingToPylon)
    moveBackward = searching.to(reversing)
    crossing = searching.to(crossingObstacle)
    stopping = searching.to(stopped)
    backToSearchFromMovingForward = movingToPylon.to(searching)
    backToSearchFromMoveBackward = reversing.to(searching)
    backtoSearchFromCrossing = crossingObstacle.to(searching)
    backToSearchFromStopped = stopped.to(searching)
    stayInSearch = searching.to.itself()
    goToEmergency = searching.to(emergencyMode)
    backToSearchFromEmergency = emergencyMode.to(searching)
    endParcour = searching.to(parcoursCompleted)

#Test States and Transitions
rstm = RobotStateMachine()
print(rstm.current_state)
rstm.startSearching()
print(rstm.current_state)
rstm.moveForward()
print(rstm.current_state)
rstm.backToSearchFromMovingForward()
print(rstm.current_state)
rstm.moveBackward()
print(rstm.current_state)
rstm.backToSearchFromMoveBackward()
print(rstm.current_state)
rstm.crossing()
print(rstm.current_state)
rstm.backtoSearchFromCrossing()
print(rstm.current_state)
rstm.stopping()
print(rstm.current_state)
rstm.backToSearchFromStopped()
print(rstm.current_state)
rstm.goToEmergency()
print(rstm.current_state)
rstm.backToSearchFromEmergency()
print(rstm.current_state)
rstm.endParcour()
print(rstm.current_state)




























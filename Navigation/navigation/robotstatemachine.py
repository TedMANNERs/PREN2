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
    error = State('Error')

    #Transitions
    startSearching = ready.to(searching)
    readyToError = ready.to(error)
    errorToReady = error.to(ready)

    #TODO Find out if a SubStateMachine is Possible
    searchingToError = searching.to(error)
    movingToPylonToError = movingToPylon.to(error)
    reversingToError = reversing.to(error)
    crossingObstacleToError = crossingObstacle.to(error)
    stoppedToError = stopped.to(error)
    emergencyModeToError = emergencyMode.to(error)

    moveForward = searching.to(movingToPylon)
    moveBackward = searching.to(reversing)
    crossing = searching.to(crossingObstacle)
    stopping = searching.to(stopped)

    #TODO Look if a loop like (searching.to(movingToPylon) | movingToPylon.to(searching))
    backToSearchFromMovingForward = movingToPylon.to(searching)
    backToSearchFromMoveBackward = reversing.to(searching)
    backtoSearchFromCrossing = crossingObstacle.to(searching)
    backToSearchFromStopped = stopped.to(searching)

    stayInSearch = searching.to.itself()
    goToEmergency = searching.to(emergencyMode)
    backToSearchFromEmergency = emergencyMode.to(searching)
    endParcour = searching.to(parcoursCompleted)

#Test States and Transitions
#TODO Extract in a test Class
rstm = RobotStateMachine()
print(rstm.current_state)
rstm.readyToError()
print(rstm.current_state)
rstm.errorToReady()
print(rstm.current_state)
rstm.startSearching()
print(rstm.current_state)
rstm.searchingToError()
print(rstm.current_state)
rstm.errorToReady()
print(rstm.current_state)
rstm.startSearching()
print(rstm.current_state)
rstm.moveForward()
print(rstm.current_state)
rstm.movingToPylonToError()
print(rstm.current_state)
rstm.errorToReady()
print(rstm.current_state)
rstm.startSearching()
print(rstm.current_state)
rstm.moveBackward()
print(rstm.current_state)
rstm.reversingToError()
print(rstm.current_state)
rstm.errorToReady()
print(rstm.current_state)
rstm.startSearching()
print(rstm.current_state)
rstm.crossing()
print(rstm.current_state)
rstm.crossingObstacleToError()
print(rstm.current_state)
rstm.errorToReady()
print(rstm.current_state)
rstm.startSearching()
print(rstm.current_state)
rstm.stopping()
print(rstm.current_state)
rstm.stoppedToError()
print(rstm.current_state)
rstm.errorToReady()
print(rstm.current_state)
rstm.startSearching()
print(rstm.current_state)
rstm.goToEmergency()
print(rstm.current_state)
rstm.emergencyModeToError()
print(rstm.current_state)
rstm.errorToReady()
print(rstm.current_state)
rstm.startSearching()
print(rstm.current_state)
rstm.stayInSearch()
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




























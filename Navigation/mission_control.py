from communication.subscriber import Subscriber

class MissionControl(Subscriber):
    def __init__(self, lowLevelController):
        self.lowLevelController = lowLevelController
        self.lowLevelController.startListening()
        self.lowLevelController.subscribe(self)
        self.isMissionSuccessful = True #TODO: change to false when code is ready
        self.isMissionCancelled = False

    def start(self):
        print("Mission Control started")
        #selfTest.run()
        #lowLevelController.subscribe(self)
        self.__runMission()

    def __runMission(self):
        while not self.isMissionSuccessful:
            if self.isMissionCancelled:
                print("Mission was cancelled!")
                break

            #targetVector = navigation.getNextTargetVector()
            #self.lowLevelController.sendTargetVector(targetVector)

        print("Mission was successful!")

    def stop(self):
        print("Mission Control stopped")
        self.lowLevelController.stopListening()

    # Is called when new data from the LLC is received.
    def onCommandReceived(self, command):
        print(command)
        #TODO: Implement command handlers
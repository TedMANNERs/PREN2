class MissionControl:
    def __init__(self, communication):
        self.communication = communication
        self.isMissionSuccessful = True #TODO: change to false when code is ready
        self.isMissionCancelled = False

    def start(self):
        print("Mission Control started")
        #selfTest.run()
        #communication.subscribe(self)
        self.__runMission()

    def __runMission(self):
        while not self.isMissionSuccessful:
            if self.isMissionCancelled:
                print("Mission was cancelled!")
                break

            #targetVector = navigation.getNextTargetVector()
            #communication.sendVector(targetVector)

        print("Mission was successful!")

    # Is called when new data from the LLC is received.
    #def onDataReceived(self):
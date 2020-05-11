import logging
from communication.subscriber import Subscriber
from communication.lowLevelController import CommandType, Command
from horwbot_state_machine import HorwbotStateMachine

class MissionControl(Subscriber):
    def __init__(self, state_machine: HorwbotStateMachine):
        self.state_machine = state_machine

    def start(self):
        logging.info("Starting Mission Control")
        self.state_machine.start()

    def stop(self):
        logging.info("Stopping Mission Control")
        self.state_machine.stop()

    def abort(self):
        logging.info("Aborting...")
        self.state_machine.abort()

    # Is called when new data from the LLC is received.
    def onCommandReceived(self, command: Command):
        logging.debug("MissionControl: Received command = %s", command)
        if command.commandType == CommandType.Start:
            self.start()
        elif command.commandType == CommandType.SendSensorData:
            logging.info(command.data)
            #TODO: Implement handling of sensor data
            pass
        elif command.commandType == CommandType.Stop:
            self.stop()
        else:
            raise ValueError("A command of type '{0}' should never be received!".format(command.commandType))

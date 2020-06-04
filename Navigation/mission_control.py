import cv2
import numpy as np
import logging
import distutils
from transitions.extensions.nesting import NestedState
from transitions.extensions import LockedHierarchicalGraphMachine
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver
from debugGui.debugInfo import DebugInfo
from communication.lowLevelController import LowLevelController, CommandType, Command
from communication.subscriber import Subscriber
from states.init_state import InitState
from states.ready_state import ReadyState
from states.aborted_state import AbortedState
from states.running_state import RunningState
from states.error_state import ErrorState
from states.parcoursCompleted_state import ParcoursCompletedState
from configreader import parser
from distutils.util import strtobool

#TODO: Replace strings with constants
class MissionControl(LockedHierarchicalGraphMachine, Subscriber):
    def __init__(self, llc: LowLevelController, detector: PylonDetector, navigator: Navigator):
        states = [InitState(llc, detector), ReadyState(llc), ErrorState(llc), AbortedState(llc), RunningState(llc, detector, navigator, self), ParcoursCompletedState(llc)]
        transitions = [
            { 'trigger': 'initialize', 'source': 'init', 'dest': 'ready'},
            { 'trigger': 'start', 'source': 'ready', 'dest': 'running'},
            { 'trigger': 'navigate', 'source': 'running_searching', 'dest': 'running_navigating'},
            { 'trigger': 'reverse', 'source': 'running_searching', 'dest': 'running_reversing'},
            { 'trigger': 'cross', 'source': 'running_searching', 'dest': 'running_crossingObstacle'},
            { 'trigger': 'abort', 'source': ['ready', 'running', 'error'], 'dest': 'aborted'},
            { 'trigger': 'stop', 'source': 'running', 'dest': 'ready'},
            { 'trigger': 'panic', 'source': 'running_searching', 'dest': 'running_emergency'},
            { 'trigger': 'search', 'source': ['running_navigating', 'running_reversing', 'running_crossingObstacle', 'running_emergency'], 'dest': 'running_searching'},
            { 'trigger': 'endParcours', 'source': 'running_navigating', 'dest': 'parcoursCompleted'},
            { 'trigger': 'recoverReady', 'source': 'error', 'dest': 'ready'},
            { 'trigger': 'recoverRunning', 'source': 'error', 'dest': 'running'},
            { 'trigger': 'fail', 'source': ['init', 'ready', 'running'], 'dest': 'error'}
        ]
        
        super().__init__(model=self, states=states, transitions=transitions, initial='init', send_event=True, queued=True)
        ENABLE_STATE_DIAGRAM = bool(strtobool(parser.get("debug", "ENABLE_STATE_DIAGRAM")))
        if ENABLE_STATE_DIAGRAM:
            self.before_state_change = self.update_state_diagram
            self.after_state_change = self.update_state_diagram


    def update_state_diagram(self, event):
        graph = self.model.get_graph()
        buffer = graph.pipe(format='png')
        nparr = np.fromstring(buffer, np.uint8)
        DebugInfo.stateDiagram = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Is called when new data from the LLC is received.
    def onCommandReceived(self, command: Command):
        #logging.debug("MissionControl: Received command = %s", command)
        if command.commandType == CommandType.Start:
            self.start()
        elif command.commandType == CommandType.SendSensorData:
            #logging.info(command.data)
            #TODO: Implement handling of sensor data
            pass
        elif command.commandType == CommandType.Stop:
            self.stop()
        else:
            raise ValueError("A command of type '{0}' should never be received!".format(command.commandType))

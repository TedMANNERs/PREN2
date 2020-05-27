import time
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController
from imageDetection.pylonDetector import PylonDetector
from debugGui.webserver import Webserver
from camera.camera_provider import CameraProvider
from configreader import parser
from distutils.util import strtobool

class InitState(NestedState):
    ENABLE_WEBSERVER = bool(strtobool(parser.get("debug", "ENABLE_WEBSERVER")))
    def __init__(self, lowLevelController: LowLevelController, pylonDetector: PylonDetector):
        self.lowLevelController = lowLevelController
        self.pylonDetector = pylonDetector
        super().__init__(name='init', on_exit=self.onExit)

    def onExit(self, event):
        isSimulation = event.args[0]
        # Init camera
        CameraProvider.initialize(isSimulation)
        # Init YOLO
        self.pylonDetector.initialize()
        # Start listening for commands from the LLC
        self.lowLevelController.startListening()
        self.lowLevelController.subscribe(event.machine)
        time.sleep(0.5)
        print("START_SOFTWARE")
        self.lowLevelController.sendStart()
        if self.ENABLE_WEBSERVER:
            self.webserver = Webserver()
            self.webserver.start()
        

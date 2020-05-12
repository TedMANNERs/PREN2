from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController
from imageDetection.pylonDetector import PylonDetector
from communication.usb import Usb
from debugGui.webserver import Webserver
from camera.camera_provider import CameraProvider

class InitState(NestedState):
    def __init__(self, lowLevelController: LowLevelController, pylonDetector: PylonDetector):
        self.lowLevelController = lowLevelController
        self.pylonDetector = pylonDetector
        super().__init__(name='init', on_exit=self.onExit)

    def onExit(self, event):
        # Init camera
        CameraProvider.initialize()
        # Init YOLO
        self.pylonDetector.initialize()
        # Start listening for commands from the LLC
        self.lowLevelController.startListening()
        self.lowLevelController.subscribe(self)
        if Usb.hasWifiDongle():
            self.webserver = Webserver()
            self.webserver.start()
        pass
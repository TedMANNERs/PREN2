import logging
import time
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, LowLevelControllerException
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector, Label
from debugGui.debugInfo import DebugInfo
from camera.camera_provider import CameraProvider
from common.timer import Timer
from configreader import parser
from distutils.util import strtobool

class NavigatingState(NestedState):
    ENABLE_BOX_DRAWING = bool(strtobool(parser.get("debug", "ENABLE_BOX_DRAWING")))
    def __init__(self, parent, lowLevelController: LowLevelController, pylonDetector: PylonDetector, navigator: Navigator):
        self.parent = parent
        self.lowLevelController = lowLevelController
        self.pylonDetector = pylonDetector
        self.navigator = navigator
        self.lap = 0
        super().__init__(name='navigating', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self, event):
        self.parent.substate = self
        self.lapTimer = Timer()
        self.lapTimer.start()
        self.timer = Timer()
        self.timer.start()

    def loop(self):
        frame = CameraProvider.getCamera().getFrame()
        detections, frame_resized = self.pylonDetector.findObjects(frame)

        pylons = []
        for detection in detections:
            detection = self.pylonDetector.calculateDistance(detection, frame_resized)
            if detection[0] == Label.Pylon.value:
                self.timer.reset()
                pylons.append(detection) # Filter pylons from all detections

            if self.lap >= 2:
                self.parent.mission_control.endParcours()
            if detection[0] == Label.LyingPylon.value and detection[3] < 3500 and self.lapTimer.getElapsedTime() > 3:
                logging.info("LAP COMPLETED")
                self.lap += 1
                self.lapTimer.reset()
            
            if self.ENABLE_BOX_DRAWING:
                frame_resized = self.pylonDetector.drawBox(detection, frame_resized)
        
        if self.timer.getElapsedTime() > 2: # Seconds
                self.timer.stop()
                self.parent.mission_control.search()
                return

        DebugInfo.latestFrame =  frame_resized
        targetVector = self.navigator.getNavigationTargetVector(pylons, frame_resized, self.timer)
        try:
            self.lowLevelController.sendTargetVector(targetVector)
        except LowLevelControllerException as e:
            logging.error(e)
            self.parent.mission_control.stop()

    def onExit(self, event):
        pass
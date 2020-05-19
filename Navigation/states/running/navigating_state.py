import logging
import time
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, LowLevelControllerException
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector, Label
from debugGui.debugInfo import DebugInfo
from camera.camera_provider import CameraProvider
from common.timer import Timer

class NavigatingState(NestedState):
    def __init__(self, parent, lowLevelController: LowLevelController, pylonDetector: PylonDetector, navigator: Navigator):
        self.parent = parent
        self.lowLevelController = lowLevelController
        self.pylonDetector = pylonDetector
        self.navigator = navigator
        super().__init__(name='navigating', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self, event):
        self.parent.substate = self
        self.timer = Timer()
        self.timer.start()

    def loop(self):
        frame = CameraProvider.getCamera().getFrame()
        detections, frame_resized = self.pylonDetector.findObjects(frame)
        detections = self.pylonDetector.calculateDistances(detections, frame_resized)
        DebugInfo.latestFrame =  self.pylonDetector.drawBoxes(detections, frame_resized)
        
        if any(x[0] == Label.Pylon.value for x in detections):
            self.timer.reset()
        elif self.timer.getElapsedTime() > 2: # Seconds
            self.timer.stop()
            self.parent.mission_control.search()
            return

        pylons = [x for x in detections if x[0] == Label.Pylon.value] # Filter pylons from all detections
        targetVector = self.navigator.getNavigationTargetVector(pylons, frame_resized, self.timer)
        try:
            self.lowLevelController.sendTargetVector(targetVector)
        except LowLevelControllerException as e:
            logging.error(e)
            self.parent.mission_control.stop()

    def onExit(self, event):
        pass
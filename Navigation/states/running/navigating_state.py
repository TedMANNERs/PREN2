import logging
import time
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, LowLevelControllerException
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector
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
        detectedPylons, frame_resized = self.pylonDetector.findPylons(frame)
        detectedPylons = self.pylonDetector.calculateDistances(detectedPylons, frame_resized)
        DebugInfo.latestFrame =  self.pylonDetector.drawBoxes(detectedPylons, frame_resized)
        
        if detectedPylons:
            self.timer.reset()
        elif self.timer.getElapsedTime() > 2:
            self.timer.stop()
            self.parent.mission_control.search()
            return

        targetVector = self.navigator.getNavigationTargetVector(detectedPylons, frame_resized, self.timer)
        try:
            self.lowLevelController.sendTargetVector(targetVector)
        except LowLevelControllerException as e:
            logging.error(e)
            self.parent.mission_control.stop()

    def onExit(self, event):
        pass
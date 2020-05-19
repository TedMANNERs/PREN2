import logging
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, LowLevelControllerException
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector, Label
from debugGui.debugInfo import DebugInfo
from camera.camera_provider import CameraProvider

class SearchingState(NestedState):
    def __init__(self, parent, lowLevelController: LowLevelController, pylonDetector: PylonDetector, navigator: Navigator):
        self.parent = parent
        self.lowLevelController = lowLevelController
        self.pylonDetector = pylonDetector
        self.navigator = navigator
        super().__init__(name='searching', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self, event):
        self.parent.substate = self

    def loop(self):
        frame = CameraProvider.getCamera().getFrame()
        detections, frame_resized = self.pylonDetector.findObjects(frame)
        detections = self.pylonDetector.calculateDistances(detections, frame_resized)
        DebugInfo.latestFrame =  self.pylonDetector.drawBoxes(detections, frame_resized)
        
        if any(x[0] == Label.Pylon.value for x in detections):
            #logging.debug(detections)
            self.parent.mission_control.navigate()
        else:
            targetVector = self.navigator.getSearchTargetVector()
            try:
                self.lowLevelController.sendTargetVector(targetVector)
            except LowLevelControllerException as e:
                logging.error(e)
                self.parent.mission_control.stop()

    def onExit(self, event):
        pass
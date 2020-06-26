import logging
from transitions.extensions.nesting import NestedState
from communication.lowLevelController import LowLevelController, LowLevelControllerException
from navigation.navigator import Navigator
from imageDetection.pylonDetector import PylonDetector, Label
from debugGui.debugInfo import DebugInfo
from camera.camera_provider import CameraProvider
from configreader import parser
from distutils.util import strtobool
from common.timer import Timer
from timeit import default_timer as perfTimer

class SearchingState(NestedState):
    ENABLE_BOX_DRAWING = bool(strtobool(parser.get("debug", "ENABLE_BOX_DRAWING")))
    def __init__(self, parent, lowLevelController: LowLevelController, pylonDetector: PylonDetector, navigator: Navigator):
        self.parent = parent
        self.lowLevelController = lowLevelController
        self.pylonDetector = pylonDetector
        self.navigator = navigator
        super().__init__(name='searching', on_enter=self.onEnter, on_exit=self.onExit)
    
    def onEnter(self, event):
        self.parent.substate = self
        self.timer = Timer()
        self.timer.start()

    def loop(self):
        t_start = perfTimer()
        frame = CameraProvider.getCamera().getFrame()
        detections, frame_resized = self.pylonDetector.findObjects(frame)

        for detection in detections:
            if detection[0] == Label.Pylon.value:
                logging.debug("### PYLON DETECTED ###")
                self.parent.mission_control.navigate()
                return
                
            detection = self.pylonDetector.calculateDistance(detection, frame_resized)
            if self.ENABLE_BOX_DRAWING:
                frame_resized = self.pylonDetector.drawBox(detection, frame_resized)

        if self.timer.getElapsedTime() > 6: # Seconds
            self.parent.mission_control.panic()
            return

        DebugInfo.latestFrame =  frame_resized
        targetVector = self.navigator.getSearchTargetVector()
        try:
            self.lowLevelController.sendTargetVector(targetVector)
        except LowLevelControllerException as e:
            logging.error(e)
            self.parent.mission_control.stop()
        t_end = perfTimer()
        total = t_end - t_start
        if total > 1:
            logging.debug("Searching State Looptime = {0}".format(t_end - t_start))
        
    def onExit(self, event):
        pass

import cv2

class DebugInfo:
    latestFrame = None
    stateDiagram = None
    
    def __init__(self, latestFrame, stateDiagram):
        self.latestFrame = latestFrame
        self.stateDiagram = stateDiagram

    @staticmethod
    def getLatest():
        return DebugInfo(DebugInfo.latestFrame, DebugInfo.stateDiagram)

    @staticmethod
    def showLatestFrame():
        if DebugInfo.latestFrame is not None:
            cv2.imshow("Horwbot Image Detection", DebugInfo.latestFrame)
            cv2.waitKey(1)
            
    @staticmethod
    def showStateDiagram():
        if DebugInfo.stateDiagram is not None:
            cv2.namedWindow("Horwbot State Machine", cv2.WINDOW_NORMAL)
            cv2.imshow("Horwbot State Machine", DebugInfo.stateDiagram)
            cv2.waitKey(1)
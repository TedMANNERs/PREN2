import threading
import struct
import cv2
import socketserver
import numpy as np
from camera.base_camera import BaseCamera

# See https://docs.python.org/3.6/library/socketserver.html for more info
class CameraSimulationRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        # Read message length
        raw_message_length = self.request.recv(4)
        message_length = struct.unpack('I', raw_message_length)[0]

        # Read message itself
        data = bytearray()
        while len(data) < message_length:
            packet = self.request.recv(message_length - len(data))
            if not packet:
                return None
            data.extend(packet)

        frame_bytes = np.asarray(data, dtype=np.uint8)
        frame = cv2.imdecode(frame_bytes, cv2.IMREAD_COLOR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if frame is not None:
            self.server.frame = frame

class CameraSimulationServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)
        self.frame = np.zeros((5,5,3), np.uint8)

class CameraSimulation(BaseCamera):
    
    def __init__(self):
        self._server = CameraSimulationServer(("localhost", 6048), CameraSimulationRequestHandler)
        serverThread = threading.Thread(target=self._serve)
        serverThread.start()

    def getFrame(self):
        return self._server.frame

    def _serve(self):
        self._server.serve_forever()
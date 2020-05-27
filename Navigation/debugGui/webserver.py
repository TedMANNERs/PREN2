#!/usr/bin/env python3
from importlib import import_module
import os
import cv2
import logging
import threading
from time import sleep
from flask import Flask, render_template, Response, request, stream_with_context
from debugGui.debugInfo import DebugInfo

class Webserver:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/video_feed", "video_feed", self.video_feed)
        self.app.add_url_rule("/stream_logs", "stream_logs", self.stream_logs)
        self.app.add_url_rule("/state_diagram_feed", "state_diagram_feed", self.state_diagram_feed)
        self.__thread = threading.Thread(target=self._run, daemon=True)
        
    def index(self):
        """One Pager of the Debug Gui"""
        return render_template('index.html')
        
    def video_feed(self):
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(self._create_stream_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def state_diagram_feed(self):
        return Response(self._create_state_diagram_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def stream_logs(self):
        def _generate_logs():
            with open('horwlog.log') as f:
                while True:
                    data= f.read()
                    if not data:
                        break
                    yield data
        return Response(stream_with_context(_generate_logs()), mimetype="text/plain") 

    def start(self):
        logging.info("Starting webserver")
        self.__thread.start()

    def _run(self):
        self.app.run(host='0.0.0.0', port=8080, threaded=True)

    # TODO: Implement update mechanism for all debug info -> update data from client (javscript with ajax)?
    def _create_state_diagram_generator(self):
        """Video streaming generator function."""
        while True:
            if DebugInfo.stateDiagram is None:
                continue
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode(".jpg", DebugInfo.stateDiagram)[1].tobytes() + b'\r\n')

    def _create_stream_generator(self):
        """Video streaming generator function."""
        while True:
            if DebugInfo.latestFrame is None:
                continue
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode(".jpg", DebugInfo.latestFrame)[1].tobytes() + b'\r\n')

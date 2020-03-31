#!/usr/bin/env python
from importlib import import_module
import os
import cv2
from flask import Flask, render_template, Response
from mission_control import MissionControl

class Webserver:
    def __init__(self, mission_control: MissionControl):
        self.mission_control = mission_control
        self.app = Flask(__name__)
        self.app.add_url_rule("/", "index", self.index)
        self.app.add_url_rule("/video_feed", "video_feed", self.video_feed)
        
    def index(self):
        """One Pager of the Debug Gui"""
        return render_template('index.html')
        
    def video_feed(self):
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(self._create_stream_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def start(self):
        print("Start webserver")
        self.app.run(host='0.0.0.0', port=8080, threaded=True)

    def _create_stream_generator(self):
        """Video streaming generator function."""
        while True:
            debugInfo = self.mission_control.getDebugInfo() # TODO: Implement update mechanism for all debug info -> update data from client (javscript with ajax)?
            if debugInfo.latestFrame is None:
                continue
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + cv2.imencode(".jpg", debugInfo.latestFrame)[1].tobytes() + b'\r\n')

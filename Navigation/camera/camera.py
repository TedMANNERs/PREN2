import time
from base_camera import BaseCamera
import os


class Camera(BaseCamera):
    """1. Fake implementation of the Camera Module to Test the Livestream with 3 Pictures
       2. Make sure u change the os.chdir to the path of the pictures"""
    
    os.chdir('C:\\Users\\Surface\\Documents\\PREN2\\Navigation\\DebugGui\\static\\images\\')
    imgs = [open(os.getcwd() + '\\'+ str(f) + '.jpg', 'rb').read() for f in ['1', '2', '3']]

    @staticmethod
    def frames():
        while True:
            time.sleep(1)
            yield Camera.imgs[int(time.time()) % 3]

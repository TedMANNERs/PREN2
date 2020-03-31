import abc

class BaseCamera(metaclass=abc.ABCMeta):
    def getFrame(self):
        """Return the current camera frame."""
        raise RuntimeError('Must be implemented by subclasses.')

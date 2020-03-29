import abc

class Subscriber(metaclass=abc.ABCMeta):
    def __init__(self):
        self._publisher = None

    @abc.abstractmethod
    def onCommandReceived(self, command):
        pass
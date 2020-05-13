import time

class TimerError(Exception):
    """Custom exception used for errors in the Timer class"""

class Timer:
    def __init__(self):
        self._startTime = None
        self.elapsed_time = 0.0

    def start(self):
        if self._startTime is not None:
            raise TimerError(f"Timer is already running. Use .stop() to stop it")

        self._startTime = time.perf_counter()

    def stop(self):
        if self._startTime is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        self.elapsed_time = self.getElapsedTime()
        self._startTime = None

    def reset(self):
        self._startTime = time.perf_counter()

    def getElapsedTime(self):
        return time.perf_counter() - self._startTime
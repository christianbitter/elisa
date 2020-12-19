import time


class FPS:
    """A frame per second counter"""

    def __init__(self):
        """Setup a new frames per second counter"""
        super(FPS, self).__init__()
        self._time_start_ns = 0.0
        self._time_stop_ns = 0.0
        self._time_delta_ns = 0.0
        self._time_dt_ns = 0.0
        self._fps = 0
        self._no_frames = 0

    def tick(self):
        """Start the performance counting/collection process"""
        self._time_start_ns = time.perf_counter_ns()

    def tock(self):
        """Stop the performance counting/ collection process"""
        self._time_stop_ns = time.perf_counter_ns()
        self._time_delta_ns = self._time_stop_ns - self._time_start_ns
        self._time_dt_ns += self._time_delta_ns
        self._time_dt_s = self._time_dt_ns / 1000000000
        self._no_frames += 1
        self._fps = self._no_frames / self._time_dt_s

    @property
    def fps(self) -> float:
        """Returns the number of frames per second achieved

        Returns:
            float: fps
        """
        return self._fps

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "FPS: {}".format(self._fps)

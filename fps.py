import time

class FPS():
    """"""

    def __init__(self, ):
        """Constructor for FPS"""
        super(FPS, self).__init__()
        self._time = time.perf_counter_ns()
        self._oldtime = 0
        self._delta_acc = 0
        self._no_frames = 0
        self._fps     = 0

    def collect(self):
        _t = time.perf_counter_ns()
        dt = _t - self._oldtime
        self._no_frames += 1
        self._delta_acc = self._delta_acc + dt
        self._delta     = dt
        self._time      = _t
        self._oldtime   = self._time

        d_s = self._delta_acc / 1000000
        self._fps = self._no_frames / d_s


    @property
    def delta_ms(self):
        return self._delta * 0.001

    @property
    def fps(self):
        return self._fps

    @property
    def millis(self):
        return self._time * 0.001

    def __repr__(self):
        return "Millisec.: {}/ {} FPS".format(self.millis, self.fps)
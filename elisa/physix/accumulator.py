"""M1: frame-time accumulator for a fixed simulation step."""

from __future__ import annotations

from collections.abc import Callable

DEFAULT_MAX_FRAME_TIME = 0.25


class FixedStepAccumulator:
    """Turn irregular real frame times into a whole number of fixed steps.

    Args:
        step: Callable that advances the simulation by one fixed step.
        dt: Fixed simulation timestep in seconds.
        max_frame_time: Largest real frame time accepted for a single call;
            a longer stall is clamped so catch-up cannot spiral.
    """

    def __init__(
        self,
        step: Callable[[], None],
        dt: float = 1.0 / 60.0,
        max_frame_time: float = DEFAULT_MAX_FRAME_TIME,
    ) -> None:
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        if max_frame_time <= 0.0:
            raise ValueError("max_frame_time must be positive")
        self._step = step
        self._dt = float(dt)
        self._max_frame_time = float(max_frame_time)
        self._accumulator = 0.0

    @property
    def dt(self) -> float:
        return self._dt

    @property
    def max_frame_time(self) -> float:
        return self._max_frame_time

    @property
    def remainder(self) -> float:
        """Simulation time accumulated but not yet stepped."""
        return self._accumulator

    def advance(self, frame_time: float) -> int:
        """Feed one real frame time and return the number of steps run.

        (M1):
            1. reject or clamp a negative or oversized ``frame_time`` so a
               stall cannot exceed ``max_frame_time``;
            2. add the accepted time to the accumulator;
            3. while the accumulator holds at least ``dt``, call ``step()``
               once and subtract ``dt`` (never call step with a fractional
               dt);
            4. keep the remainder for the next frame and return the step
               count.
        """
        frame_time = min(max(frame_time, 0.0), self._max_frame_time)

        self._accumulator = self._accumulator + frame_time
        step_count = 0

        while self._accumulator >= self._dt:
            self._step()
            self._accumulator -= self._dt
            step_count += 1

        return step_count

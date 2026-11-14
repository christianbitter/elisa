"""Shared tuning constants for the physics milestones.

These are the values the roadmap says are calibrated per fixed step.  They live
here rather than in a milestone folder because more than one milestone uses
them and the learner's project should not carry duplicates.
"""

FIXED_DT = 1.0 / 60.0
MAX_FRAME_TIME = 0.25
GRAVITY_Y = -9.81

SLOP = 0.005
CORRECTION_FRACTION = 0.8
RESTITUTION_THRESHOLD = 1.0
SOLVER_ITERATIONS = 8

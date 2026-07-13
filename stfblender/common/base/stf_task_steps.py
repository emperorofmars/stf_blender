from enum import IntEnum

__all__ = ["STF_TaskSteps"]

class STF_TaskSteps(IntEnum):
	DEFAULT = 100
	BEFORE_ANIMATION = 10000
	ANIMATION = 10010
	AFTER_ANIMATION = 10020
	FINALE = 10000000

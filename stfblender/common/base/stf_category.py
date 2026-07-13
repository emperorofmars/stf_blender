from enum import StrEnum

__all__ = ["STF_Category"]

class STF_Category(StrEnum):
	DATA = "data"
	NODE = "node"
	INSTANCE = "instance"
	COMPONENT = "component"

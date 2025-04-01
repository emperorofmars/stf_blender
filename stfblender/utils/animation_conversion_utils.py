

from typing import Callable


# Translation
def translate_translation_property_to_stf(index: int) -> str:
	match(index):
			case 0: return "x"
			case 1: return "z"
			case 2: return "y"
	return None

def get_translation_to_stf_translation_func(index: int) -> Callable[[any], any]:
	def __func(value: float) -> float:
		match(index):
			case 0: return value
			case 1: return -value
			case 2: return value
	return __func


# Rotation
def translate_rotation_property_to_stf(index: int) -> str:
	match(index):
			case 0: return "x"
			case 1: return "z"
			case 2: return "y"
			case 3: return "w"
	return None

def get_rotation_to_stf_translation_func(index: int) -> Callable[[any], any]:
	def __func(value: float) -> float:
		match(index):
			case 0: return value
			case 1: return value
			case 2: return -value
			case 3: return value
	return __func


# Scale
def translate_scale_property_to_stf(index: int) -> str:
	match(index):
			case 0: return "x"
			case 1: return "z"
			case 2: return "y"
	return None

def get_scale_to_stf_translation_func(index: int) -> Callable[[any], any]:
	def __func(value: float) -> float: return value
	return __func




# Translation
def translate_translation_property_to_blender(index: int) -> str:
	match(index):
			case "x": return 0
			case "z": return 1
			case "y": return 2
	return None

def get_translation_to_blender_translation_func(index: int) -> Callable[[any], any]:
	def __func(value: float) -> float:
		match(index):
			case 0: return value
			case 1: return -value
			case 2: return value
	return __func

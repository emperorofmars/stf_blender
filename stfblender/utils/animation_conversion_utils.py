from typing import Callable

"""
Export
"""

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

def translate_bone_translation_property_to_stf(index: int) -> str:
	match(index):
			case 0: return "x"
			case 1: return "y"
			case 2: return "z"
	return None


# Rotation
def translate_rotation_property_to_stf(index: int) -> str:
	match(index):
			case 0: return "w"
			case 1: return "x"
			case 2: return "z"
			case 3: return "y"
	return None

def get_rotation_to_stf_translation_func(index: int) -> Callable[[any], any]:
	def __func(value: float) -> float:
		match(index):
			case 0: return value
			case 1: return value
			case 2: return -value
			case 3: return value
	return __func

def translate_bone_rotation_property_to_stf(index: int) -> str:
	match(index):
			case 0: return "w"
			case 1: return "x"
			case 2: return "y"
			case 3: return "z"
	return None


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

def translate_bone_scale_property_to_stf(index: int) -> str:
	match(index):
			case 0: return "x"
			case 1: return "z"
			case 2: return "y"
	return None


"""
Import
"""

# Translation
def translate_translation_property_to_blender(property: str) -> int:
	match(property):
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

def translate_translation_property_to_blender_bone(property: str) -> int:
	match(property):
			case "x": return 0
			case "y": return 1
			case "z": return 2
	return None

# Rotation
def translate_rotation_property_to_blender(property: str) -> int:
	match(property):
			case "w": return 0
			case "x": return 1
			case "z": return 2
			case "y": return 3
	return None

def get_rotation_to_blender_translation_func(index: int) -> Callable[[any], any]:
	def __func(value: float) -> float:
		match(index):
			case 0: return value
			case 1: return value
			case 2: return -value
			case 3: return value
	return __func

def translate_rotation_property_to_blender_bone(property: str) -> int:
	match(property):
			case "w": return 0
			case "x": return 1
			case "y": return 2
			case "z": return 3
	return None


# Scale
def translate_scale_property_to_blender(property: str) -> int:
	match(property):
			case "x": return 0
			case "z": return 1
			case "y": return 2
	return None

def get_scale_to_blender_translation_func(index: int) -> Callable[[any], any]:
	def __func(value: float) -> float: return value
	return __func

def translate_scale_property_to_blender_bone(property: str) -> int:
	match(property):
			case "x": return 0
			case "y": return 1
			case "z": return 2
	return None

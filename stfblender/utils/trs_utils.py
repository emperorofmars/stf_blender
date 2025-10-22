import mathutils

# Graciously referenced from: https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/blender/exp/nodes.py#L537


def close_enough(value: float, target: float = 0, threshold: float = 0.00001) -> float:
	if(abs(value - target) < threshold):
		return target
	else:
		return value


""" Export """

def blender_translation_to_stf(blender_vec: mathutils.Vector | list[float]) -> list[float]:
	# x,y,z -> x,z,-y
	return [close_enough(blender_vec[0]), close_enough(blender_vec[2]), close_enough(-blender_vec[1])]

def blender_rotation_to_stf(blender_quat: mathutils.Quaternion | list[float]) -> list[float]:
	# w,x,y,z -> x,z,-y,w
	return [close_enough(blender_quat[1]), close_enough(blender_quat[3]), close_enough(-blender_quat[2]), close_enough(blender_quat[0], 1)]

def blender_rotation_euler_to_stf(blender_vec: mathutils.Vector | list[float]):
	# x,y,z -> x,z,-y
	return [close_enough(blender_vec[0]), close_enough(-blender_vec[2]), close_enough(-blender_vec[1])]

def blender_scale_to_stf(blender_vec: mathutils.Vector | list[float]) -> list[float]:
	# x,y,z -> x,z,y
	return [close_enough(blender_vec[0], 1), close_enough(blender_vec[2], 1), close_enough(blender_vec[1], 1)]

def blender_to_trs(t: mathutils.Vector | list[float], r: mathutils.Quaternion | list[float], s: mathutils.Vector | list[float]) -> list[list[float]]:
	return [
		blender_translation_to_stf(t),
		blender_rotation_to_stf(r),
		blender_scale_to_stf(s)
	]

def blender_uv_to_stf(blender_vec: mathutils.Vector | list[float]) -> list[float]:
	# x,y -> x,1-y
	return [blender_vec[0], 1 - blender_vec[1]]


""" Import """

def stf_translation_to_blender(vec: list[float]) -> mathutils.Vector:
	# x,z,-y -> x,y,z
	return mathutils.Vector((vec[0], -vec[2], vec[1]))

def stf_rotation_to_blender(quat: list[float]) -> mathutils.Quaternion:
	# x,z,-y,w -> w,x,y,z
	return mathutils.Quaternion((quat[3], quat[0], -quat[2], quat[1]))

def stf_rotation_euler_to_blender(vec: list[float]) -> mathutils.Vector:
	# x,z,-y -> x,y,z
	return mathutils.Vector((vec[0], -vec[2], -vec[1]))

def stf_scale_to_blender(vec: list[float]) -> mathutils.Vector:
	# x,z,y -> x,y,z
	return mathutils.Vector((vec[0], vec[2], vec[1]))

def stf_to_blender(trs: list[list[float]]) -> tuple[mathutils.Vector, mathutils.Quaternion, mathutils.Vector]:
	return (stf_translation_to_blender(trs[0]), stf_rotation_to_blender(trs[1]), stf_scale_to_blender(trs[2]))

def stf_to_blender_matrix(trs: list[list[float]]) -> mathutils.Matrix:
	return mathutils.Matrix.LocRotScale(stf_translation_to_blender(trs[0]), stf_rotation_to_blender(trs[1]), stf_scale_to_blender(trs[2]))

def stf_uv_to_blender(stf_uv: list[float]) -> list[float]:
	return mathutils.Vector((stf_uv[0], 1 - stf_uv[1]))


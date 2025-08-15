import bpy
import mathutils

# Graciously referenced from: https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/blender/exp/nodes.py#L537

def blender_translation_to_stf(blender_vec: mathutils.Vector) -> list[float]:
	# x,y,z -> x,z,-y
	return [blender_vec[0], blender_vec[2], -blender_vec[1]]

def blender_rotation_to_stf(blender_quat: mathutils.Quaternion) -> list[float]:
	# w,x,y,z -> x,z,-y,w
	return [blender_quat[1], blender_quat[3], -blender_quat[2], blender_quat[0]]

def blender_scale_to_stf(blender_vec: list[float]) -> list[float]:
	# x,y,z -> x,z,y
	return [blender_vec[0], blender_vec[2], blender_vec[1]]

def blender_to_trs(t: mathutils.Vector, r: mathutils.Quaternion, s: mathutils.Vector) -> list[list[float]]:
	return [
		blender_translation_to_stf(t),
		blender_rotation_to_stf(r),
		blender_scale_to_stf(s)
	]

def blender_uv_to_stf(blender_vec: list[float]) -> list[float]:
	# x,y -> x,1-y
	return [blender_vec[0], 1 - blender_vec[1]]


def blender_object_to_trs(blender_object: bpy.types.Object) -> list[list[float]]:
	if(blender_object.parent):
		match(blender_object.parent_type):
			case "OBJECT":
				t, r, s = (blender_object.parent.matrix_world.inverted_safe() @ blender_object.matrix_world).decompose()
			case "BONE":
				t, r, s = (blender_object.parent.matrix_world.inverted_safe() @ blender_object.matrix_world).decompose()
	else:
		t, r, s = blender_object.matrix_world.decompose()
	return blender_to_trs(t, r, s)


def stf_translation_to_blender(vec: list[float]) -> mathutils.Vector:
	# x,z,-y -> x,y,z
	return mathutils.Vector((vec[0], -vec[2], vec[1]))

def stf_rotation_to_blender(quat: list[float]) -> mathutils.Quaternion:
	# x,z,-y,w -> w,x,y,z
	return mathutils.Quaternion((quat[3], quat[0], -quat[2], quat[1]))

def stf_scale_to_blender(vec: list[float]) -> mathutils.Vector:
	# x,z,y -> x,y,z
	return mathutils.Vector((vec[0], vec[2], vec[1]))

def stf_to_blender(trs: list[list[float]]) -> tuple[mathutils.Vector, mathutils.Quaternion, mathutils.Vector]:
	return (stf_translation_to_blender(trs[0]), stf_rotation_to_blender(trs[1]), stf_scale_to_blender(trs[2]))

def stf_to_blender_matrix(trs: list[list[float]]) -> mathutils.Matrix:
	return mathutils.Matrix.LocRotScale(stf_translation_to_blender(trs[0]), stf_rotation_to_blender(trs[1]), stf_scale_to_blender(trs[2]))

def trs_to_blender_object(trs: list[list[float]], blender_object: bpy.types.Object):
	blender_object.rotation_mode = "QUATERNION"
	matrix_local = stf_to_blender_matrix(trs)
	if(blender_object.parent):
		match(blender_object.parent_type):
			case "OBJECT":
				blender_object.matrix_world = blender_object.parent.matrix_world @ matrix_local
			case "BONE":
				blender_object.matrix_world = blender_object.parent.matrix_world @ matrix_local
	else:
		blender_object.matrix_world = matrix_local

def stf_uv_to_blender(stf_uv: list[float]) -> list[float]:
	return mathutils.Vector((stf_uv[0], 1 - stf_uv[1]))

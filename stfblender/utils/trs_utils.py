import bpy
import mathutils

# Graciously referenced from: https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/blender/exp/nodes.py#L537

def blender_translation_to_stf(blender_vec: mathutils.Vector) -> list[float]:
	# x,y,z -> x,z,-y
	return [blender_vec.x, blender_vec.z, -blender_vec.y]

def blender_rotation_to_stf(blender_quat: mathutils.Quaternion) -> list[float]:
	# w,x,y,z -> x,z,-y,w
	return [blender_quat.x, blender_quat.z, -blender_quat.y, blender_quat.w]

def blender_scale_to_stf(blender_vec: mathutils.Vector) -> list[float]:
	# x,y,z -> x,z,y
	return [blender_vec.x, blender_vec.z, blender_vec.y]

def to_trs(t: mathutils.Vector, r: mathutils.Quaternion, s: mathutils.Vector) -> list[list[float]]:
	return [
		blender_translation_to_stf(t),
		blender_rotation_to_stf(r),
		blender_scale_to_stf(s)
	]

def blender_object_to_trs(blender_object: bpy.types.Object) -> list[list[float]]:
	return to_trs(blender_object.location, blender_object.rotation_quaternion, blender_object.scale)


def stf_translation_to_blender(vec: list[float]) -> mathutils.Vector:
	# x,z,-y -> x,y,z
	return mathutils.Vector((vec[0], -vec[2], vec[1]))

def stf_rotation_to_blender(quat: list[float]) -> mathutils.Vector:
	# x,z,-y,w -> w,x,y,z
	return mathutils.Quaternion((quat[3], quat[0], -quat[2], quat[1]))

def stf_scale_to_blender(vec: list[float]) -> mathutils.Vector:
	# x,z,y -> x,y,z
	return mathutils.Vector((vec[0], vec[2], vec[1]))

def from_trs(trs: list[list[float]]) -> tuple[mathutils.Vector, mathutils.Quaternion, mathutils.Vector]:
	return (stf_translation_to_blender(trs[0]), stf_rotation_to_blender(trs[1]), stf_scale_to_blender(trs[2]))

def trs_to_blender_object(trs: list[list[float]], blender_object: bpy.types.Object):
	blender_object.location = stf_translation_to_blender(trs[0])
	blender_object.rotation_mode = "QUATERNION"
	blender_object.rotation_quaternion = stf_rotation_to_blender(trs[1])
	blender_object.scale = stf_scale_to_blender(trs[2])

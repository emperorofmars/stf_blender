import uuid
import bpy

from ....utils.component_utils import add_component
from ..ava_avatar import STF_Module_AVA_Avatar, AVA_Avatar


def detect_mesh_and_armature(collection: bpy.types.Collection) -> tuple[bpy.types.Mesh, bpy.types.Armature]:
	main_mesh = None
	main_armature = None
	for object in collection.all_objects[:]:
		if(type(object.data) == bpy.types.Mesh and ("body" in object.name.lower() or "face" in object.name.lower())):
			if(not main_mesh or len(object.name) < len(main_mesh.name)):
				main_mesh = object
	for object in collection.all_objects[:]:
		if(type(object.data) == bpy.types.Armature and ("armature" in object.name.lower() or "skeleton" in object.name.lower())):
			if(not main_armature or len(object.name) < len(main_armature.name)):
				main_armature = object
	if(main_mesh and main_armature):
		return main_mesh, main_armature
	else:
		return None


def clear_components(target: bpy.types.ID, component_property: str):
	for preexisting in getattr(target, component_property):
		for ref_index, ref in enumerate(target.stf_info.stf_components):
			if(ref.stf_id == preexisting.stf_id):
				target.stf_info.stf_components.remove(ref_index)
				break
	getattr(target, component_property).clear()


def ava_autosetup(target: bpy.types.Collection):
	detect_ret = detect_mesh_and_armature(target)
	if(not detect_ret):
		return
	main_mesh, main_armature = detect_ret

	target.stf_use_collection_as_prefab = True

	# Clear existing components
	clear_components(target, STF_Module_AVA_Avatar.blender_property_name)

	# Apply
	_, avatar = add_component(target, STF_Module_AVA_Avatar.blender_property_name, str(uuid.uuid4()), STF_Module_AVA_Avatar.stf_type)
	avatar: AVA_Avatar = avatar # autocomplete
	avatar.name = target.name
	avatar.primary_mesh_instance = main_mesh
	avatar.primary_armature_instance = main_armature

	# todo detect visemes, humanoid armature mappings, eye rotation, ...


import bpy

from ..base.stf_registry import get_stf_modules


def clean_id_things(id_thingy: any):
	valid_component_ids = []
	if(hasattr(id_thingy, "stf_info")):
		for ref in id_thingy.stf_info.stf_components:
			valid_component_ids.append(ref.stf_id)
	if(hasattr(id_thingy, "stf_instance_armature")):
		for ref in id_thingy.stf_instance_armature.stf_components:
			valid_component_ids.append(ref.stf_id)
	if(hasattr(id_thingy, "stf_instance_armature_component_standins")):
		for ref in id_thingy.stf_instance_armature_component_standins.stf_components:
			valid_component_ids.append(ref.stf_id)

	check_properties = []
	for stf_module in get_stf_modules():
		if(hasattr(stf_module, "blender_property_name")):
			check_properties.append(getattr(stf_module, "blender_property_name"))

	cleaned_components = 0
	for prop in check_properties:
		if(hasattr(id_thingy, prop)):
			components = getattr(id_thingy, prop)
			i = 0
			while i < len(components):
				if(components[i].stf_id not in valid_component_ids):
					components.remove(i)
					cleaned_components += 1
				i += 1
	if(cleaned_components > 0):
		print(id_thingy, " : ", cleaned_components)


def cleanup_unreferenced_components():
	for blender_thingy in bpy.data.collections:
		clean_id_things(blender_thingy)
	for blender_thingy in bpy.data.objects:
		clean_id_things(blender_thingy)
	for blender_thingy in bpy.data.armatures:
		clean_id_things(blender_thingy)
		for bone in blender_thingy.bones:
			clean_id_things(bone)
	for blender_thingy in bpy.data.materials:
		clean_id_things(blender_thingy)
	for blender_thingy in bpy.data.images:
		clean_id_things(blender_thingy)
	for blender_thingy in bpy.data.actions:
		clean_id_things(blender_thingy)
	for blender_thingy in bpy.data.meshes:
		clean_id_things(blender_thingy)


class CleanupOp(bpy.types.Operator):
	bl_idname = "stf.cleanup_unreferenced_components"
	bl_label = "Cleanup Unreferenced Components"

	def execute(self, context):
		cleanup_unreferenced_components()
		return {"FINISHED"}



import bpy

from ..base.stf_registry import get_stf_modules


def clean_id_thingy(id_thingy: any):
	valid_component_ids = []
	cleaned_component_refs = 0
	if(hasattr(id_thingy, "stf_info")):
		for ref in id_thingy.stf_info.stf_components:
			if(hasattr(id_thingy, ref.blender_property_name)):
				valid_component_ids.append(ref.stf_id)
		i = 0
		while i < len(id_thingy.stf_info.stf_components):
			if(id_thingy.stf_info.stf_components[i].stf_id not in valid_component_ids):
				id_thingy.stf_info.stf_components.remove(i)
				cleaned_component_refs += 1
			i += 1

	if(hasattr(id_thingy, "stf_instance_armature")):
		for ref in id_thingy.stf_instance_armature.stf_components:
			if(hasattr(id_thingy, ref.blender_property_name)):
				valid_component_ids.append(ref.stf_id)
		i = 0
		while i < len(id_thingy.stf_instance_armature.stf_components):
			if(id_thingy.stf_instance_armature.stf_components[i].stf_id not in valid_component_ids):
				id_thingy.stf_instance_armature.stf_components.remove(i)
				cleaned_component_refs += 1
			i += 1

	if(hasattr(id_thingy, "stf_instance_armature_component_standins")):
		for ref in id_thingy.stf_instance_armature_component_standins.stf_components:
			if(hasattr(id_thingy, ref.blender_property_name)):
				valid_component_ids.append(ref.stf_id)
		i = 0
		while i < len(id_thingy.stf_instance_armature_component_standins.stf_components):
			if(id_thingy.stf_instance_armature_component_standins.stf_components[i].stf_id not in valid_component_ids):
				id_thingy.stf_instance_armature_component_standins.stf_components.remove(i)
				cleaned_component_refs += 1
			i += 1

	if(hasattr(id_thingy, "stf_data_refs")):
		for ref in id_thingy.stf_data_refs:
			if(hasattr(id_thingy, ref.blender_property_name)):
				valid_component_ids.append(ref.stf_id)
		i = 0
		while i < len(id_thingy.stf_data_refs):
			if(id_thingy.stf_data_refs[i].stf_id not in valid_component_ids):
				id_thingy.stf_data_refs.remove(i)
				cleaned_component_refs += 1
			i += 1

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
	if(cleaned_components > 0 or cleaned_component_refs > 0):
		print(id_thingy, " : ", cleaned_components, " - ", cleaned_component_refs)


def cleanup_unreferenced_components():
	for blender_thingy in bpy.data.collections:
		clean_id_thingy(blender_thingy)
	for blender_thingy in bpy.data.objects:
		clean_id_thingy(blender_thingy)
	for blender_thingy in bpy.data.armatures:
		clean_id_thingy(blender_thingy)
		for bone in blender_thingy.bones:
			clean_id_thingy(bone)
	for blender_thingy in bpy.data.materials:
		clean_id_thingy(blender_thingy)
	for blender_thingy in bpy.data.images:
		clean_id_thingy(blender_thingy)
	for blender_thingy in bpy.data.actions:
		clean_id_thingy(blender_thingy)
	for blender_thingy in bpy.data.meshes:
		clean_id_thingy(blender_thingy)


class CleanupOp(bpy.types.Operator):
	"""Remove components and data-resources no longer referenced anywhere"""
	bl_idname = "stf.cleanup_unreferenced_components"
	bl_label = "Cleanup Unreferenced Components"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		cleanup_unreferenced_components()
		return {"FINISHED"}


class QuaternionsEverywhere(bpy.types.Operator):
	"""Warning: this will break existing non-quaternion animations!"""
	bl_idname = "stf.set_everything_to_quaternion_rotation"
	bl_label = "Set everything to use Quaternions (At your own risk!)"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		for blender_object in bpy.data.objects[:]:
			blender_object.rotation_mode = "QUATERNION"
			if(type(blender_object.data) == bpy.types.Armature):
				for bone in blender_object.pose.bones[:]:
					bone.rotation_mode = "QUATERNION"
		return {"FINISHED"}


class UnfuckMatrixParentInverse(bpy.types.Operator):
	"""Warning: this will pretty much fuck up all your animations!"""
	bl_idname = "stf.unfuck_matrix_parent_inverse"
	bl_label = "Unfuck matrix_parent_inverse (Don't)"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		for blender_object in bpy.data.objects[:]:
			if(blender_object.parent):
				tmp = blender_object.matrix_world.copy()
				blender_object.matrix_parent_inverse = blender_object.parent.matrix_world.inverted_safe()
				blender_object.matrix_world = tmp
		return {"FINISHED"}


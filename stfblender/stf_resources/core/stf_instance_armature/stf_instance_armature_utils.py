import bpy

from ....common import STF_ExportContext, STF_ImportContext
from ....common.resource.component import InstanceModComponentRef, STF_Handler_Component, STF_Component_Ref
from ....common.utils.animation_conversion_utils import *

from ....common.base.stf_registry import find_component_handler, get_component_handlers
from ....common.resource.component.component_utils import add_component


def update_armature_instance_component_standins(context: bpy.types.Context, blender_object: bpy.types.Object, stf_modules: list[STF_Handler_Component] = None):
	blender_armature: bpy.types.Armature = blender_object.data
	handled_ids = []
	if(not stf_modules):
		stf_modules = get_component_handlers()

	for bone in blender_armature.bones:
		for component_ref in bone.stf_info.stf_components:
			if(hasattr(bone, component_ref.blender_property_name)):
				for component in getattr(bone, component_ref.blender_property_name):
					if(component.stf_id == component_ref.stf_id):
						break
				else:
					continue
			if(stf_module := find_component_handler(stf_modules, component_ref.stf_type)):
				if(hasattr(stf_module, "set_component_instance_standin_func")):
					for standin_component_ref in blender_object.stf_instance_armature_component_standins.stf_components:
						if(standin_component_ref.stf_id == component_ref.stf_id):
							for standin_component in getattr(blender_object, component_ref.blender_property_name):
								if(standin_component.stf_id == standin_component_ref.stf_id):
									break
							break
					else:
						standin_component_ref, standin_component = add_component(blender_object, component_ref.blender_property_name, component_ref.stf_id, component_ref.stf_type, blender_object.stf_instance_armature_component_standins.stf_components)
					standin_component_ref.bone = bone.name
					if(not standin_component_ref.override):
						set_func = getattr(stf_module, "set_component_instance_standin_func")
						set_func(context, component_ref, blender_object, component, standin_component)
					handled_ids.append(component_ref.stf_id)

	standin_ref_index = 0
	while(standin_ref_index < len(blender_object.stf_instance_armature_component_standins.stf_components)):
		#for standin_ref_index in range(len(blender_object.stf_instance_armature_component_standins.stf_components)):
		standin_ref = blender_object.stf_instance_armature_component_standins.stf_components[standin_ref_index]
		if(standin_ref.stf_id not in handled_ids):
			if(hasattr(bone, component_ref.blender_property_name) and hasattr(blender_object, standin_ref.blender_property_name)):
				for standin_component_index, standin_component in enumerate(getattr(blender_object, standin_ref.blender_property_name)):
					if(standin_component.stf_id == standin_ref.stf_id):
						getattr(blender_object, standin_ref.blender_property_name).remove(standin_component_index)
						standin_component_index -= 1
						blender_object.stf_instance_armature_component_standins.stf_components.remove(standin_ref_index)
						standin_ref_index -= 1
						break
		standin_ref_index += 1


def serialize_standin(context: STF_ExportContext, blender_object: bpy.types.Object, component_standin_ref: InstanceModComponentRef) -> dict:
	for standin_component in getattr(blender_object, component_standin_ref.blender_property_name):
		if(standin_component.stf_id == component_standin_ref.stf_id):
			break
	else:
		return None

	stf_modules = get_component_handlers()
	if(stf_module := find_component_handler(stf_modules, component_standin_ref.stf_type)):
		if(hasattr(stf_module, "serialize_component_instance_standin_func")):
			return stf_module.serialize_component_instance_standin_func(context, component_standin_ref, standin_component, blender_object)
	return None


def parse_standin(context: STF_ImportContext, blender_object: bpy.types.Object, component_id: str, json_resource: dict):
	for standin_ref in blender_object.stf_instance_armature_component_standins.stf_components:
		if(standin_ref.stf_id == component_id):
			break
	else:
		return
	for standin_component in getattr(blender_object, standin_ref.blender_property_name):
		if(standin_component.stf_id == standin_ref.stf_id):
			break
	else:
		return

	stf_modules = get_component_handlers()
	if(stf_module := find_component_handler(stf_modules, standin_ref.stf_type)):
		if(hasattr(stf_module, "serialize_component_instance_standin_func")):
			standin_ref.override = True
			return stf_module.parse_component_instance_standin_func(context, json_resource, standin_ref, standin_component, blender_object)


class UpdateArmatureInstanceComponentStandins(bpy.types.Operator):
	bl_idname = "stf.update_armature_instance_standins"
	bl_label = "Update Standins"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context: bpy.types.Context):
		update_armature_instance_component_standins(context, context.object, get_component_handlers())
		return {"FINISHED"}



def process_components(armature_instance: bpy.types.Object, stf_resources: list[STF_Handler_Component] = None):
	if(not stf_resources):
		stf_resources = get_component_handlers()

	components_to_process = {}

	# todo handle exclusion groups

	for bone in armature_instance.data.bones:
		for component_ref in bone.stf_info.stf_components:
			component_ref: STF_Component_Ref = component_ref
			for stf_module in stf_resources:
				if(stf_module.stf_type == component_ref.stf_type and hasattr(stf_module, "process_func") and getattr(stf_module, "process_func")):
					for component in getattr(bone, component_ref.blender_property_name):
						if(component.stf_id == component_ref.stf_id):
							components_to_process[component.stf_id] = ([component, bone, stf_module])
							break

	for component_ref in armature_instance.stf_instance_armature_component_standins.stf_components:
		if(component_ref.override and component_ref.stf_id in components_to_process):
			for component in getattr(armature_instance, components_to_process[component_ref.stf_id][2].blender_property_name):
				if(component.stf_id == component_ref.stf_id):
					components_to_process[component.stf_id][0] = component
					break

	for component_ref in armature_instance.stf_instance_armature.stf_components:
		bone: bpy.types.Bone = armature_instance.data.bones[component_ref.bone]
		for component_ref in bone.stf_info.stf_components:
			component_ref: STF_Component_Ref = component_ref
			for stf_module in stf_resources:
				if(stf_module.stf_type == component_ref.stf_type and hasattr(stf_module, "process_func") and getattr(stf_module, "process_func")):
					for component in getattr(bone, component_ref.blender_property_name):
						if(component.stf_id == component_ref.stf_id):
							components_to_process[component.stf_id] = ([component, bone, stf_module])
							break

	for component_id in components_to_process:
		component, bone, stf_module = components_to_process[component_id]
		component: STF_ComponentResourceBase = component
		stf_module.process_func(component, bone, armature_instance)


class ProcessComponentsOntoArmatureInstance(bpy.types.Operator):
	bl_idname = "stf.armature_instance_process_components"
	bl_label = "Process Components"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context: bpy.types.Context): return context.object is not None and type(context.object.data) == bpy.types.Armature

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event, message="This will overwrite constraints and other values!")

	def execute(self, context: bpy.types.Context):
		process_components(context.object, get_component_handlers())
		return {"FINISHED"}


import bpy

from .stf_instance_armature import InstanceModComponentRef
from ....exporter.stf_export_context import STF_ExportContext
from ....utils.animation_conversion_utils import *
from ....utils.component_utils import add_component, find_component_module, get_component_modules


class UpdateArmatureInstanceComponentStandins(bpy.types.Operator):
	bl_idname = "stf.update_armature_instance_standins"
	bl_label = "Update Standins"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		blender_object: bpy.types.Object = context.object
		blender_armature: bpy.types.Armature = context.object.data
		stf_modules = get_component_modules()

		handled_ids = []

		for bone in blender_armature.bones:
			for component_ref in bone.stf_components:
				if(hasattr(bone, component_ref.blender_property_name)):
					for component in getattr(bone, component_ref.blender_property_name):
						if(component.stf_id == component_ref.stf_id):
							break
					else:
						continue
				if(stf_module := find_component_module(stf_modules, component_ref.stf_type)):
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

		for standin_ref_index, standin_ref in enumerate(blender_object.stf_instance_armature_component_standins.stf_components):
			if(standin_ref.stf_id not in handled_ids):
				if(hasattr(bone, component_ref.blender_property_name)):
					for standin_component_index, standin_component in enumerate(getattr(blender_object, standin_ref.blender_property_name)):
						if(standin_component.stf_id == standin_ref.stf_id):
							getattr(blender_object, standin_ref.blender_property_name).remove(standin_component_index)
							standin_component_index -= 1
							blender_object.stf_instance_armature_component_standins.stf_components.remove(standin_ref_index)
							standin_ref_index -= 1
							break

		return {"FINISHED"}

def serialize_standin(context: STF_ExportContext, blender_object: bpy.types.Object, component_standin_ref: InstanceModComponentRef) -> dict: # todo
	return {  }

def parse_standin(): # todo
	pass

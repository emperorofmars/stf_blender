import bpy

from ....core.stf_module import STF_Module
from ....utils.id_utils import ensure_stf_id
from ....utils.animation_conversion_utils import *
from ....utils.armature_bone import ArmatureBone
from ....utils.component_utils import STF_Component_Ref, find_component_module, get_component_modules


class UpdateArmatureInstanceComponentStandins(bpy.types.Operator):
	bl_idname = "stf.update_armature_instance_standins"
	bl_label = "Update Standins"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		blender_object: bpy.types.Object = context.object
		blender_armature: bpy.types.Armature = context.object.data
		stf_modules = get_component_modules()

		for bone in blender_armature.bones:
			for component_ref in bone.stf_components:
				if(hasattr(bone, component_ref.blender_property_name)):
					for component in getattr(bone, component_ref.blender_property_name):
						if(component.stf_id == component_ref.stf_id):
							break
					else:
						continue
				if(stf_module := find_component_module(stf_modules, component_ref.stf_type)):
					if(hasattr(stf_module, "set_component_instance_standin")):
						# todo create standin component
						set_func = getattr(stf_module, "set_component_instance_standin")
						set_func(context, component_ref, blender_object, component)

		return {"FINISHED"}

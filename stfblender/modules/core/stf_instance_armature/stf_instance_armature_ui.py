import bpy

from .stf_instance_armature import InstanceModComponentRef
from .stf_instance_armature_utils import UpdateArmatureInstanceComponentStandins
from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STF_Component_Ref, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui_utils import draw_components_ui, draw_instance_standin_components_ui, set_stf_component_filter


class STFSetArmatureInstanceIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for ArmatureInstance"""
	bl_idname = "stf.set_armature_instance_stf_id"
	@classmethod
	def poll(cls, context): return context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Armature
	def get_property(self, context): return context.object.stf_instance

class STFAddArmatureInstanceComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to ArmatureInstance"""
	bl_idname = "stf.add_armature_instance_component"
	@classmethod
	def poll(cls, context): return context.object.stf_instance_armature is not None and context.object.data and type(context.object.data) is bpy.types.Armature
	def get_property(self, context): return context.object
	def get_components_ref_property(self, context) -> STF_Component_Ref: return context.object.stf_instance_armature.stf_components

class STFRemoveArmatureInstanceComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	bl_idname = "stf.remove_armature_instance_component"
	def get_property(self, context): return context.object
	def get_components_ref_property(self, context) -> STF_Component_Ref: return context.object.stf_instance_armature.stf_components

class STFEditArmatureInstanceComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	bl_idname = "stf.edit_armature_instance_component_id"
	def get_property(self, context): return context.object
	def get_components_ref_property(self, context) -> STF_Component_Ref: return context.object.stf_instance_armature.stf_components


def _get_target_object_func(component_holder: bpy.types.Object, component_ref: InstanceModComponentRef) -> any:
	armature: bpy.types.Armature = component_holder.data
	for bone in armature.bones:
		if(bone.stf_id == component_ref.bone):
			return bone
	return None

def _inject_ui(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: InstanceModComponentRef, context_object: any, component: any) -> bool:
	layout.prop_search(component_ref, "bone", component_ref.id_data.data, "bones", text="Target Bone")
	if(not component_ref.bone):
		layout.label(text="Please select a target Bone")
		return False
	layout.separator(type="LINE", factor=1)
	return True

def _inject_standin_ui(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: InstanceModComponentRef, context_object: any, component: any) -> bool:
	layout.label(text="Target Bone: " + component_ref.bone)
	layout.prop(component_ref, "override")
	layout.separator(type="LINE", factor=1)
	return True


class STFArmatureInstancePanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_armature_instance_editor"
	bl_label = "STF Editor: stf.instance.armature"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return (context.object.stf_instance_armature is not None and context.object.data and type(context.object.data) is bpy.types.Armature)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Bone)

		# Set ID
		draw_stf_id_ui(self.layout, context, context.object.stf_instance, STFSetArmatureInstanceIDOperator.bl_idname, True)

		self.layout.separator(factor=2, type="LINE")

		# Components specific to this instance
		draw_components_ui(self.layout, context, context.object, STFAddArmatureInstanceComponentOperator.bl_idname, STFRemoveArmatureInstanceComponentOperator.bl_idname, STFEditArmatureInstanceComponentIdOperator.bl_idname, context.object.stf_instance_armature, _get_target_object_func, _inject_ui)

		self.layout.separator(factor=4, type="LINE")

		# todo standins for components on bones
		self.layout.prop(context.object.stf_instance_armature_component_standins, "use_bone_component_overrides")
		if(context.object.stf_instance_armature_component_standins.use_bone_component_overrides):
			self.layout.label(text="Override and animate values of components on bones.")
			self.layout.operator(UpdateArmatureInstanceComponentStandins.bl_idname)
			self.layout.separator(factor=1, type="SPACE")
			
			if(len(context.object.stf_instance_armature_component_standins.stf_components) > 0):
				draw_instance_standin_components_ui(self.layout, context, context.object, STFEditArmatureInstanceComponentIdOperator.bl_idname, context.object.stf_instance_armature_component_standins, _get_target_object_func, _inject_standin_ui)

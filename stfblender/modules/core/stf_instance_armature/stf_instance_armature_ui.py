import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STF_Component_Ref, STFAddComponentOperatorBase, STFEditComponentIdOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui_utils import draw_components_ui, set_stf_component_filter
from ..stf_node.stf_node import InstanceModComponentRef


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
	def poll(cls, context): return context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Armature
	def get_property(self, context): return context.object
	def get_components_ref_property(self, context) -> STF_Component_Ref: return context.object.stf_instance.stf_components

class STFRemoveArmatureInstanceComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	bl_idname = "stf.remove_armature_instance_component"
	def get_property(self, context): return context.object
	def get_components_ref_property(self, context) -> STF_Component_Ref: return context.object.stf_instance.stf_components

class STFEditArmatureInstanceComponentIdOperator(bpy.types.Operator, STFEditComponentIdOperatorBase):
	bl_idname = "stf.edit_armature_instance_component_id"
	def get_property(self, context): return context.object
	def get_components_ref_property(self, context) -> STF_Component_Ref: return context.object.stf_instance.stf_components


def _get_target_object_func(component_holder: bpy.types.Object, component_ref: InstanceModComponentRef) -> any:
	armature: bpy.types.Armature = component_holder.data
	for bone in armature.bones:
		if(bone.stf_id == component_ref.node_id):
			return bone
	return None

def _inject_ui(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: InstanceModComponentRef, context_object: any, component: any):
	layout.label(text=str(context_object))
	layout.prop(component_ref, "node_id", text="Target Bone Id")
	layout.separator(type="LINE", factor=1)


class STFArmatureInstancePanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_armature_instance_editor"
	bl_label = "STF ArmatureInstance Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "STF"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return (context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Armature)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Bone)

		self.layout.label(text="stf.instance.armature")

		# Set ID
		draw_stf_id_ui(self.layout, context, context.object.stf_instance, STFSetArmatureInstanceIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		draw_components_ui(self.layout, context, context.object, STFAddArmatureInstanceComponentOperator.bl_idname, STFRemoveArmatureInstanceComponentOperator.bl_idname, STFEditArmatureInstanceComponentIdOperator.bl_idname, context.object.stf_instance, _get_target_object_func, _inject_ui)

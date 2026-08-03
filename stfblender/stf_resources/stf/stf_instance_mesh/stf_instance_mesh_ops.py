import bpy

from .....stfblender_common import STFSetIDOperatorBase
from .stf_instance_mesh_data import STF_Instance_Mesh


class STFSetMeshInstanceIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for mesh instance"""
	bl_idname = "stf.set_mesh_instance_stf_id"
	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		return hasattr(context, "object") and context.object is not None and context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh  # pyright: ignore[reportReturnType]
	def get_property(self, context: bpy.types.Context): return context.object.stf_instance


class OverrideBlendshape(bpy.types.Operator):
	"""Override a shape key for this mesh instance"""
	bl_idname = "stf.override_mesh_instance_blendshape"
	bl_label = "Override Shape Key"
	bl_options = {"REGISTER", "UNDO"}

	key_name: bpy.props.StringProperty(name="Shape key name")

	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		return hasattr(context, "object") and context.object is not None and context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh # pyright: ignore[reportReturnType]

	def execute(self, context: bpy.types.Context) -> set:
		if(self.key_name in context.object.stf_instance_mesh.blendshape_values or self.key_name not in context.object.data.shape_keys.key_blocks):
			return {"CANCELLED"}

		override = context.object.stf_instance_mesh.blendshape_values.add()
		override.name = self.key_name
		override.value = context.object.data.shape_keys.key_blocks[self.key_name].value
		return {"FINISHED"}

class RemoveBlendshapeOverride(bpy.types.Operator):
	"""Remove a shape key override on this mesh instance"""
	bl_idname = "stf.remove_override_mesh_instance_blendshape"
	bl_label = "Remove Shape Key Override"
	bl_options = {"REGISTER", "UNDO"}

	key_name: bpy.props.StringProperty(name="Shape key name")

	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		return hasattr(context, "object") and context.object is not None and context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh # pyright: ignore[reportReturnType]

	def execute(self, context: bpy.types.Context) -> set:
		if(self.key_name not in context.object.stf_instance_mesh.blendshape_values or self.key_name not in context.object.data.shape_keys.key_blocks):
			return {"CANCELLED"}

		context.object.stf_instance_mesh.blendshape_values.remove(context.object.stf_instance_mesh.blendshape_values.find(self.key_name))
		return {"FINISHED"}


class STFDrawMeshInstanceBlendshapeList(bpy.types.UIList):
	"""Override blendshapes on this mesh instance"""
	bl_idname = "COLLECTION_UL_stf_instance_mesh_blendshapes"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data: bpy.types.Key, item: bpy.types.ShapeKey, icon, active_data: STF_Instance_Mesh, active_propname: str, index: int): # pyright: ignore[reportIncompatibleMethodOverride]
		if(index == 0):
			layout.label(text=("Basis" if item.name == "Basis" else "Basis: " + item.name))
			return

		if(item.name in active_data.blendshape_values):
			layout.operator(RemoveBlendshapeOverride.bl_idname, text="", icon="REMOVE").key_name = item.name
		else:
			layout.operator(OverrideBlendshape.bl_idname, text="", icon="ADD").key_name = item.name

		layout.label(text=item.name)

		if(item.name in active_data.blendshape_values):
			layout.prop(active_data.blendshape_values[item.name], "value")
		else:
			disabled_row = layout.row()
			disabled_row.enabled = False
			disabled_row.prop(item, "value")


class RemoveUnmodifiedBlendshapeOverrides(bpy.types.Operator):
	"""Remove all unmodified shape key instance overrides"""
	bl_idname = "stf.remove_unmodified_overrides_mesh_instance_blendshape"
	bl_label = "Remove Unmodified Shape Key Overrides"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		return hasattr(context, "object") and context.object is not None and context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh # pyright: ignore[reportReturnType]

	def execute(self, context: bpy.types.Context) -> set:
		index = 0
		while(index < len(context.object.stf_instance_mesh.blendshape_values)):
			override = context.object.stf_instance_mesh.blendshape_values[index]
			if(
				override.name not in context.object.data.shape_keys.key_blocks or (
					override.value < context.object.data.shape_keys.key_blocks[override.name].value + 0.0001 and
					override.value > context.object.data.shape_keys.key_blocks[override.name].value - 0.0001
				)
			):
				context.object.stf_instance_mesh.blendshape_values.remove(index)
				continue
			index += 1
		return {"FINISHED"}

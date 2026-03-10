import bpy

from ....common.helpers import draw_multiline_text
from ....common.utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from .stf_instance_mesh import STF_Instance_Mesh_Blendshape_Value
from .stf_instance_mesh_util import instance_blendshapes_requires_update, set_instance_blendshapes


class SetInstanceBlendshapes(bpy.types.Operator):
	"""Override the Blendshape values of the Mesh"""
	bl_idname = "stf.set_mesh_instance_blendshapes"
	bl_label = "Set Blendshapes per Instance"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context): return hasattr(context, "object") and context.object is not None and context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		set_instance_blendshapes(context.object)
		return {"FINISHED"}


class STFSetMeshInstanceIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for MeshInstance"""
	bl_idname = "stf.set_mesh_instance_stf_id"
	@classmethod
	def poll(cls, context): return hasattr(context, "object") and context.object is not None and context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh
	def get_property(self, context): return context.object.stf_instance


class STFDrawMeshInstanceBlendshapeList(bpy.types.UIList):
	"""Override blendshapes on this meshinstance"""
	bl_idname = "COLLECTION_UL_stf_instance_mesh_blendshapes"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: STF_Instance_Mesh_Blendshape_Value, icon, active_data, active_propname, index):
		if(item.name == "Basis"):
			layout.label(text="Basis")
			return
		row_outer = layout.row()
		if(item.id_data.data.shape_keys and item.id_data.data.shape_keys.key_blocks and item.name in item.id_data.data.shape_keys.key_blocks):
			if(item.id_data.stf_instance_mesh.override_blendshape_values):
				row_outer.prop(item, "override", text="")
			row_outer.label(text=item.name)
			row = row_outer.row()
			if(not item.override or not item.id_data.stf_instance_mesh.override_blendshape_values):
				row.enabled = False
				if(item.id_data.data.shape_keys and item.id_data.data.shape_keys.key_blocks and item.name in item.id_data.data.shape_keys.key_blocks):
					row.prop(item.id_data.data.shape_keys.key_blocks[item.name], "value", text="Value")
			else:
				row.prop(item, "value", text="Value")
		else:
			row_outer.alert = True
			row_outer.enabled = False
			row_outer.label(text="Invalid Value ( " + item.name + " )")


	def filter_items(self, context: bpy.types.Context, data, propname: str):
		items: list[STF_Instance_Mesh_Blendshape_Value] = getattr(data, propname)

		_sort = [(idx, item) for idx, item in enumerate(items)]
		def _sort_func(item: tuple[int, STF_Instance_Mesh_Blendshape_Value]):
			return item[1].index_on_mesh
		sortorder = bpy.types.UI_UL_list.sort_items_helper(_sort, _sort_func, False)

		return [self.bitflag_filter_item] * len(items), sortorder


class STFMeshInstancePanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_mesh_instance_editor"
	bl_label = "STF Editor: stf.instance.mesh"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "object"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "object") and context.object is not None and context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh

	def draw(self, context: bpy.types.Context):
		layout = self.layout
		if(context.object.find_armature()):
			t, r, s = context.object.matrix_local.decompose()
			if(t.length > 0.0001 or abs(r.x) > 0.0001 or abs(r.y) > 0.0001 or abs(r.z) > 0.0001 or abs((r.w - 1)) > 0.0001 or abs(s.x - 1) > 0.0001 or abs(s.y - 1) > 0.0001 or abs(s.z - 1) > 0.0001):
				text_row = draw_multiline_text(layout, "Warning, this mesh is not aligned with its Armature!\nThis will lead to differing behavior outside of Blender.\nApplying all Transforms for the Mesh and Armature will likely fix this.", width=80, icon="ERROR", alert=True)
				layout.separator(factor=2, type="LINE")

		# Set ID
		draw_stf_id_ui(layout, context, context.object.stf_instance, context.object.stf_instance, STFSetMeshInstanceIDOperator.bl_idname, True)

		layout.separator(factor=2, type="LINE")

		# Blendshape Values per Instance
		if(context.object.data.shape_keys and len(context.object.data.shape_keys.key_blocks) > 0):
			layout.prop(context.object.stf_instance_mesh, "override_blendshape_values", text="Use Instance Shape Keys")
			#if(context.object.stf_instance_mesh.override_blendshape_values):
			row = layout.row()
			if(instance_blendshapes_requires_update(context.object)):
				row.alert = True
			row.operator(SetInstanceBlendshapes.bl_idname, text="Update Shape Keys", icon="LOOP_FORWARDS")
			layout.template_list(STFDrawMeshInstanceBlendshapeList.bl_idname, "", context.object.stf_instance_mesh, "blendshape_values", context.object.stf_instance_mesh, "active_blendshape")


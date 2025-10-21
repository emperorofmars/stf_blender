import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from .stf_instance_mesh_util import set_instance_blendshapes


class SetInstanceBlendshapes(bpy.types.Operator):
	"""Override the Blendshape values of the Mesh"""
	bl_idname = "stf.set_mesh_instance_blendshapes"
	bl_label = "Set Blendshapes per Instance"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context): return context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh

	def execute(self, context):
		set_instance_blendshapes(context.object)
		return {"FINISHED"}


class STFSetMeshInstanceIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for MeshInstance"""
	bl_idname = "stf.set_mesh_instance_stf_id"
	@classmethod
	def poll(cls, context): return context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh
	def get_property(self, context): return context.object.stf_instance


class STFDrawMeshInstanceBlendshapeList(bpy.types.UIList):
	"""Override blendshapes on this meshinstance"""
	bl_idname = "COLLECTION_UL_stf_instance_mesh_blendshapes"

	def draw_item(self, context, layout: bpy.types.UILayout, data, item, icon, active_data, active_propname, index):
		row = layout.row()
		row.prop(item, "override", text=item.name)
		row.prop(item, "value", text="Value")


class STFMeshInstancePanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_mesh_instance_editor"
	bl_label = "STF Editor: stf.instance.mesh"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return (context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh)

	def draw(self, context):
		if(context.object.find_armature()):
			t, r, s = context.object.matrix_local.decompose()
			if(t.length > 0.0001 or abs(r.x) > 0.0001 or abs(r.y) > 0.0001 or abs(r.z) > 0.0001 or abs((r.w - 1)) > 0.0001 or abs(s.x - 1) > 0.0001 or abs(s.y - 1) > 0.0001 or abs(s.z - 1) > 0.0001):
				self.layout.label(text="Warning, this mesh-instance is not aligned with its Armature! This will lead to differing output.", icon="ERROR")

		# Set ID
		draw_stf_id_ui(self.layout, context, context.object.stf_instance, context.object.stf_instance, STFSetMeshInstanceIDOperator.bl_idname, True)

		self.layout.separator(factor=2, type="LINE")

		# Blendshape Values per Instance
		self.layout.prop(context.object.stf_instance_mesh, "override_blendshape_values", text="Use Instance Shape Keys")
		if(context.object.stf_instance_mesh.override_blendshape_values):
			self.layout.operator(SetInstanceBlendshapes.bl_idname, text="Update Shape Keys", icon="LOOP_FORWARDS")

			self.layout.template_list(STFDrawMeshInstanceBlendshapeList.bl_idname, "", context.object.stf_instance_mesh, "blendshape_values", context.object.stf_instance_mesh, "active_blendshape")


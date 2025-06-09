import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from .stf_instance_mesh_util import set_instance_blendshapes


class SetInstanceBlendshapes(bpy.types.Operator):
	bl_idname = "stf.set_mesh_instance_blendshapes"
	bl_label = "Set Blendshapes per Instance"
	bl_category = "STF"
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

class STFMeshInstancePanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_mesh_instance_editor"
	bl_label = "STF MeshInstance Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "STF"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return (context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh)

	def draw(self, context):
		self.layout.label(text="stf.instance.mesh")

		# Set ID
		draw_stf_id_ui(self.layout, context, context.object.stf_instance, STFSetMeshInstanceIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		self.layout.operator(SetInstanceBlendshapes.bl_idname)

		# Blendshape Values per Instance
		box = self.layout.box()
		for index, instance_blendshape in enumerate(context.object.stf_instance_mesh.blendshape_values):
			row = box.row()
			row.prop(instance_blendshape, "override", text=instance_blendshape.name)
			row.prop(instance_blendshape, "value", text="Value")


		# TODO Materials per Instance


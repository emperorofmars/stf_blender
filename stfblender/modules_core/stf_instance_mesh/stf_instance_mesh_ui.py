import bpy

from ...utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui


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

		# TODO Blendshape Values per Instance

		# TODO Materials per Instance


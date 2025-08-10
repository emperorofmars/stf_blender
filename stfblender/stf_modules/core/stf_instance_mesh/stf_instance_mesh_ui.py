import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from .stf_instance_mesh_util import set_instance_blendshapes, set_instance_materials


class SetInstanceMaterials(bpy.types.Operator):
	"""Override the Materials of the Mesh"""
	bl_idname = "stf.set_mesh_instance_materials"
	bl_label = "Set Materials per Instance"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context): return context.object.stf_instance is not None and context.object.data and type(context.object.data) is bpy.types.Mesh

	def execute(self, context):
		set_instance_materials(context.object)
		return {"FINISHED"}

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
		# Set ID
		draw_stf_id_ui(self.layout, context, context.object.stf_instance, context.object.stf_instance, STFSetMeshInstanceIDOperator.bl_idname, True)

		self.layout.separator(factor=2, type="LINE")

		# Materials per Instance
		self.layout.prop(context.object.stf_instance_mesh, "override_materials")
		if(context.object.stf_instance_mesh.override_materials):
			self.layout.operator(SetInstanceMaterials.bl_idname)
			if(len(context.object.stf_instance_mesh.materials) > 1):
				box = self.layout.box()
				for material in context.object.stf_instance_mesh.materials:
					row = box.row()
					row.prop(material, "override")
					row.prop(material, "material")

		self.layout.separator(factor=2, type="LINE")

		# Blendshape Values per Instance
		self.layout.prop(context.object.stf_instance_mesh, "override_blendshape_values")
		if(context.object.stf_instance_mesh.override_blendshape_values):
			self.layout.operator(SetInstanceBlendshapes.bl_idname)

			if(len(context.object.stf_instance_mesh.blendshape_values) > 1):
				box = self.layout.box()
				for instance_blendshape in context.object.stf_instance_mesh.blendshape_values[1:]:
					row = box.row()
					row.prop(instance_blendshape, "override", text=instance_blendshape.name)
					row.prop(instance_blendshape, "value", text="Value")


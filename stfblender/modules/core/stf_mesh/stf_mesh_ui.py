import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui_utils import draw_components_ui, set_stf_component_filter


class STFSetMeshIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Mesh"""
	bl_idname = "stf.set_mesh_stf_id"
	@classmethod
	def poll(cls, context): return context.mesh is not None
	def get_property(self, context): return context.mesh

class STFAddMeshComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Mesh"""
	bl_idname = "stf.add_mesh_component"
	@classmethod
	def poll(cls, context): return context.mesh is not None
	def get_property(self, context): return context.mesh

class STFRemoveMeshComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	bl_idname = "stf.remove_mesh_component"
	def get_property(self, context): return context.mesh

class STFEditMeshComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	bl_idname = "stf.edit_mesh_component_id"
	def get_property(self, context): return context.mesh


class STFMeshSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_mesh_editor"
	bl_label = "STF Editor: stf.mesh"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "STF"
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		return (context.mesh is not None)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Mesh)

		if(context.object.find_armature()):
			t, r, s = context.object.matrix_local.decompose()
			if(t.length > 0.0001 or abs(r.x) > 0.0001 or abs(r.y) > 0.0001 or abs(r.z) > 0.0001 or abs((r.w - 1)) > 0.0001 or abs(s.x - 1) > 0.0001 or abs(s.y - 1) > 0.0001 or abs(s.z - 1) > 0.0001):
				self.layout.label(text="Warning, origin not aligned with Armature! This will lead to differing output.")

		# Set ID
		draw_stf_id_ui(self.layout, context, context.mesh, STFSetMeshIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		draw_components_ui(self.layout, context, context.mesh, STFAddMeshComponentOperator.bl_idname, STFRemoveMeshComponentOperator.bl_idname, STFEditMeshComponentIdOperator.bl_idname)

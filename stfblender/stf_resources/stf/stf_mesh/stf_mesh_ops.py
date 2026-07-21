import bpy

from .....stfblender_common.resource import STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase


class STFSetMeshIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Mesh"""
	bl_idname = "stf.set_mesh_stf_id"
	@classmethod
	def poll(cls, context): return hasattr(context, "mesh") and context.mesh is not None
	def get_property(self, context): return context.mesh.stf_info

class STFAddMeshComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Mesh"""
	bl_idname = "stf.add_mesh_component"
	@classmethod
	def poll(cls, context): return hasattr(context, "mesh") and context.mesh is not None
	def get_property(self, context): return context.mesh

class STFRemoveMeshComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Mesh"""
	bl_idname = "stf.remove_mesh_component"
	def get_property(self, context): return context.mesh

class STFEditMeshComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_mesh_component_id"
	def get_property(self, context): return context.mesh

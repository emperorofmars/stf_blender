import bpy
from ..common.helpers.collection_helpers import OP_Edit_Component_Collection


class Edit_Component_Collection(bpy.types.Operator):
	bl_idname = OP_Edit_Component_Collection
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	blender_id_type: bpy.props.StringProperty() # type: ignore
	blender_property_name: bpy.props.StringProperty() # type: ignore
	component_id: bpy.props.StringProperty() # type: ignore

	op: bpy.props.StringProperty() # type: ignore
	component_property: bpy.props.StringProperty() # type: ignore
	index: bpy.props.IntProperty() # type: ignore

	def invoke(self, context: bpy.types.Context, event) -> set:
		if(self.op == "remove"):
			return context.window_manager.invoke_confirm(self, event)
		else:
			return self.execute(context)

	def execute(self, context: bpy.types.Context) -> set:
		blender_id = getattr(context, self.blender_id_type) if not self.scene_collection else context.scene.collection
		if(blender_id):
			for component in getattr(blender_id, self.blender_property_name):
				if(component.stf_id == self.component_id):
					if(self.op == "add"):
						getattr(component, self.component_property).add()
						return {"FINISHED"}
					elif(self.op == "remove"):
						getattr(component, self.component_property).remove(self.index)
						return {"FINISHED"}

		self.report({"ERROR"}, "Couldn't edit component collection")
		return {"CANCELLED"}

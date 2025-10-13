import bpy


class Edit_Component_Collection(bpy.types.Operator):
	bl_idname = "stf.edit_component_collection"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	blender_id_type: bpy.props.StringProperty() # type: ignore
	blender_property_name: bpy.props.StringProperty() # type: ignore
	component_id: bpy.props.StringProperty() # type: ignore

	op: bpy.props.StringProperty() # type: ignore
	component_property: bpy.props.StringProperty() # type: ignore
	index: bpy.props.IntProperty() # type: ignore

	def invoke(self, context, event):
		if(self.op == "remove"):
			return context.window_manager.invoke_confirm(self, event)
		else:
			return self.execute(context)

	def execute(self, context):
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


def create_add_button(layout: bpy.types.UILayout, blender_id_type: str | bool, blender_property_name: str, component_id: str, component_property: str, text: str = "Add", icon: str = "ADD") -> bpy.types.OperatorProperties:
	ret = layout.operator(Edit_Component_Collection.bl_idname, text=text, icon=icon)
	if(type(blender_id_type) == str):
		ret.blender_id_type = blender_id_type
		ret.scene_collection = False
	else:
		ret.blender_id_type = ""
		ret.scene_collection = True
	ret.blender_property_name = blender_property_name
	ret.component_id = component_id
	ret.component_property = component_property
	ret.op = "add"
	return

def create_remove_button(layout: bpy.types.UILayout, blender_id_type: str | bool, blender_property_name: str, component_id: str, component_property: str, index: int, text: str = "", icon: str = "X") -> bpy.types.OperatorProperties:
	ret = layout.operator(Edit_Component_Collection.bl_idname, text=text, icon=icon)
	if(type(blender_id_type) == str):
		ret.blender_id_type = blender_id_type
		ret.scene_collection = False
	else:
		ret.blender_id_type = ""
		ret.scene_collection = True
	ret.blender_property_name = blender_property_name
	ret.component_id = component_id
	ret.component_property = component_property
	ret.index = index
	ret.op = "remove"
	return


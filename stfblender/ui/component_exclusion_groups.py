import bpy


__all__ = ["STF_ExclusionGroups", "STF_RegisterExclusionGroup", "STF_RemoveExclusionGroup", "STF_ManageExclusionGroups"]


class STF_ExclusionGroups(bpy.types.PropertyGroup):
	group_name: bpy.props.StringProperty(name="Group Name", options=set()) # type: ignore

class STF_RegisterExclusionGroup(bpy.types.Operator):
	"""Register new Exclusion Group to make it selectable globally"""
	bl_idname = "stf.register_exclusion_group_operator"
	bl_label = "Register new Exclusion Group"
	bl_options = {"REGISTER", "UNDO"}

	group_name: bpy.props.StringProperty(name="Group Name") # type: ignore

	@classmethod
	def poll(cls, context): return context.collection is not None

	def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set:
		if(self.group_name):
			return self.execute(context)
		else:
			return context.window_manager.invoke_props_dialog(self)

	def execute(self, context: bpy.types.Context) -> set:
		if(self.group_name and self.group_name not in context.collection.stf_exclusion_groups):
			group = context.collection.stf_exclusion_groups.add()
			group.name = self.group_name
			group.group_name = self.group_name
		return {"FINISHED"}

class STF_RemoveExclusionGroup(bpy.types.Operator):
	"""Remove Exclusion-Group"""
	bl_idname = "stf.remove_exclusion_group_operator"
	bl_label = "Remove"
	bl_options = {"REGISTER", "UNDO"}

	group_name: bpy.props.StringProperty(name="Group Name") # type: ignore

	@classmethod
	def poll(cls, context): return context.collection is not None

	def execute(self, context: bpy.types.Context) -> set:
		for index, g in enumerate(context.collection.stf_exclusion_groups):
			if(g.name == self.group_name):
				context.collection.stf_exclusion_groups.remove(index)
		return {"FINISHED"}

class STF_ManageExclusionGroups(bpy.types.Operator):
	"""Manage Registered Exclusion-Groups"""
	bl_idname = "stf.manage_exclusion_groups_operator"
	bl_label = "Manage Exclusion-Groups"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	initial_groups: bpy.props.CollectionProperty(type=STF_ExclusionGroups, name="Exclusion Groups", options=set()) # type: ignore

	@classmethod
	def poll(cls, context): return context.collection is not None

	def invoke(self, context: bpy.types.Context, event):
		for g in context.collection.stf_exclusion_groups:
			new_g = self.initial_groups.add()
			new_g.name = g.name
		return context.window_manager.invoke_props_dialog(self, confirm_text="Done")

	def execute(self, context: bpy.types.Context) -> set:
		return {"FINISHED"}

	def cancel(self, context: bpy.types.Context):
		context.collection.stf_exclusion_groups.clear()
		for g in self.initial_groups:
			new_g = context.collection.stf_exclusion_groups.add()
			new_g.name = g.name
			new_g.group_name = g.name

	def draw(self, context: bpy.types.Context):
		layout: bpy.types.UILayout = self.layout # pyright: ignore[reportAssignmentType]
		for g in context.collection.stf_exclusion_groups:
			row = layout.row(align=True)
			row.label(text=g.name)
			row.operator(STF_RemoveExclusionGroup.bl_idname, icon="X", text="").group_name = g.name
		layout.separator(factor=2, type="LINE")
		layout.operator(STF_RegisterExclusionGroup.bl_idname, text="Add New Group", icon="PLUS")


def register():
	bpy.types.Collection.stf_exclusion_groups = bpy.props.CollectionProperty(type=STF_ExclusionGroups, name="Exclusion Groups", options=set())

def unregister():
	if(hasattr(bpy.types.Collection, "stf_exclusion_groups")):
		del bpy.types.Collection.stf_exclusion_groups

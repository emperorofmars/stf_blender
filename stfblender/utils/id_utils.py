import bpy
import uuid


class STFSetIDOperatorBase:
	"""Set STF-ID"""
	bl_label = "Set STF-ID"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		self.get_property(context).stf_id = str(uuid.uuid4())
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass


class STFSetDataIDOperatorBase:
	"""Set STF-ID on a Blender ID property"""
	bl_idname = "stf.set_object_stf_data_id"
	bl_label = "Set STF-ID"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context):
		return context.object is not None

	def execute(self, context):
		context.object.stf_data_id = str(uuid.uuid4())
		return {"FINISHED"}


def draw_stf_id_ui(layout: bpy.types.UILayout, context: bpy.types.Context, object: any, set_id_op: str):
	if(object.stf_id):
		layout.prop(object, "stf_id")
	else:
		layout.operator(set_id_op)


def draw_stf_object_data_id_ui(layout: bpy.types.UILayout, context: bpy.types.Context, object: any, set_id_op: str):
	if(object.stf_data_id):
		layout.prop(object, "stf_data_id")
	else:
		layout.operator(STFSetDataIDOperatorBase.bl_idname)


def ensure_stf_id(object: any):
	if(not object.stf_id):
		object.stf_id = str(uuid.uuid4())


def ensure_stf_object_data_id(object: bpy.types.Object):
	if(not object.stf_data_id):
		object.stf_data_id = str(uuid.uuid4())

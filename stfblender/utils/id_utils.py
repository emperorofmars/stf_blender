import bpy
import uuid

def draw_stf_id_ui(layout: bpy.types.UILayout, context: bpy.types.Context, object: any, set_id_op: str):
	if(object.stf_id):
		layout.prop(object, "stf_id")
	else:
		layout.operator(set_id_op)

def ensure_stf_id(object: any):
	if(not object.stf_id):
		object.stf_id = str(uuid.uuid4())

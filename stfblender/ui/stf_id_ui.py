import bpy
from typing import Any

from ..common.helpers.misc import OP_CopyToClipboard


__all__ = ["draw_stf_id_ui"]


def draw_stf_id_ui(layout: bpy.types.UILayout, context: bpy.types.Context, blender_object: Any, stf_prop_holder: Any, set_id_op: str, is_instance: bool = False):
	layout = layout.box()
	flow = layout.split(factor=0.15)
	flow.label(text="ID:", icon="TAG")
	if(stf_prop_holder.stf_id):
		row = flow.row(align=True)
		row_l = row.row(align=True)
		if(context.scene.stf_edit_resource_id):
			row_l.prop(stf_prop_holder, "stf_id", text="")
		else:
			row_l.label(text=stf_prop_holder.stf_id)
		row_r = row.row(align=False)
		row_r.alignment = "RIGHT"
		row_r.operator(OP_CopyToClipboard, text="", icon="DUPLICATE").text = stf_prop_holder.stf_id
		row_r.prop(context.scene, "stf_edit_resource_id", text="", icon="MODIFIER")
	else:
		flow.operator(set_id_op)

	flow = layout.split(factor=0.15)
	flow.label(text="Name:", icon="FILE_TEXT")
	row = flow.row()
	if(not hasattr(stf_prop_holder, "stf_name_source_of_truth") or stf_prop_holder.stf_name_source_of_truth):
		row.prop(stf_prop_holder, "stf_name", text="")
	else:
		sub = row.row()
		sub.enabled = False
		sub.prop(blender_object, "name", text="")
	if(not is_instance):
		row_r = row.row()
		row_r.alignment = "RIGHT"
		row_r.prop(stf_prop_holder, "stf_name_source_of_truth", text="Override Name")


def register():
	bpy.types.Scene.stf_edit_resource_id = bpy.props.BoolProperty(name="Edit ID", description="Toggle the editing of the ID", default=False)

def unregister():
	if hasattr(bpy.types.Scene, "stf_edit_resource_id"):
		del bpy.types.Scene.stf_edit_resource_id

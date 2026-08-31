import bpy
from typing import Any

from ...stfblender_common import STF_Category, STF_Handler_BlenderNative, STF_Handler_ComponentHolder
from ...stfblender_common.resource.stf_registry import find_eligible_export_handlers
from ..register_stf_data import STF_Info, STF_Instance
from .stf_id_ui import draw_stf_id_ui
from .component_ui import draw_components_ui


def draw_blender_native_resource_selector(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		blender_resource: Any,
		stf_info: STF_Info | STF_Instance
) -> STF_Handler_BlenderNative | STF_Handler_ComponentHolder | None:
	handlers = find_eligible_export_handlers(blender_resource)

	handler = None

	row = layout.row(align=True)

	if(context.scene.stf_edit_resource_usage):
		row.prop(stf_info, "determine_type", text="")
	else:
		row.alignment = "LEFT"

	if(stf_info.determine_type == "auto"):
		spacing = "    " if context.scene.stf_edit_resource_usage else ""
		prio = -1
		for candidate in handlers:
			if(candidate[1] >= prio):
				handler = candidate[0]
				prio = candidate[1]
		if(handler):
			row.label(text=f"{spacing}{handler.stf_type}")
		else:
			row.label(text=f"{spacing}Could not determine STF handler!", icon="ERROR")
	elif(stf_info.determine_type == "manual"):
		if(context.scene.stf_edit_resource_usage):
			row.prop(stf_info, "use_as", text="")
		else:
			row.label(text=f"{stf_info.use_as}    (manually overridden!)")
		for candidate in handlers:
			if(candidate[0].stf_type == stf_info.use_as):
				handler = candidate[0]
				break
	elif(not context.scene.stf_edit_resource_usage):
		row.label(text=stf_info.determine_type.capitalize())

	row_r = row.row()
	row_r.alignment = "RIGHT"
	row_r.prop(context.scene, "stf_edit_resource_usage", text="", icon="MODIFIER")

	return handler # pyright: ignore[reportReturnType]


def draw_blender_native_panel(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		blender_resource: Any,
		stf_handler: STF_Handler_BlenderNative | STF_Handler_ComponentHolder
) -> None:
	if(not hasattr(stf_handler, "get_stf_prop_holder") or not hasattr(stf_handler, "operator_set_stf_id")):
		layout.label(text="No `get_stf_prop_holder` or `operator_set_stf_id`: " + str(stf_handler))
		return
	if(stf_handler.stf_type == None):
		layout.label(text="Fallback!", icon="WARNING_LARGE")

	draw_stf_id_ui(layout, context, stf_handler.get_resource_object(blender_resource), stf_handler.get_stf_prop_holder(blender_resource), stf_handler.operator_set_stf_id, stf_handler.stf_category == STF_Category.INSTANCE)

	if(hasattr(stf_handler, "draw")):
		col_sep = layout.column()
		if(stf_handler.draw(layout.column(), context, blender_resource) != False):
			col_sep.separator(factor=2, type="LINE")

	# Components
	if(stf_handler.stf_category in [STF_Category.DATA, STF_Category.NODE]
		and hasattr(stf_handler, "get_components")
		and hasattr(stf_handler, "get_components_holder")
		and hasattr(stf_handler, "operator_component_add")
		and hasattr(stf_handler, "operator_component_remove")
		and hasattr(stf_handler, "operator_component_edit")
	):
		components = stf_handler.get_components(blender_resource)
		layout.separator(factor=2, type="LINE")
		header, body = layout.panel("stf.node_components", default_closed = False)
		header.label(text="STF Components (" + (str(len(components)) if components else "0") + ")", icon="GROUP")
		if(body): draw_components_ui(body, context, stf_handler.get_stf_prop_holder(blender_resource), stf_handler.get_components_holder(blender_resource), stf_handler.operator_component_add, stf_handler.operator_component_remove, stf_handler.operator_component_edit)


def register():
	bpy.types.Scene.stf_edit_resource_usage = bpy.props.BoolProperty(name="Edit Usage", description="Edit which STF type represents this Blender resource", default=False, options={"SKIP_SAVE"})

def unregister():
	if hasattr(bpy.types.Scene, "stf_edit_resource_usage"):
		del bpy.types.Scene.stf_edit_resource_usage

import bpy
from typing import Any

from ...stfblender_common.base import STF_Category
from ...stfblender_common.resource import STF_Handler_BlenderNative, STF_Handler_ComponentHolder
from .stf_id_ui import draw_stf_id_ui
from .component_ui import draw_components_ui


def draw_blender_native_panel(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		blender_resource: Any,
		stf_handler: STF_Handler_BlenderNative | STF_Handler_ComponentHolder
) -> None:
	if(not hasattr(stf_handler, "get_stf_prop_holder") or not hasattr(stf_handler, "operator_set_stf_id")):
		layout.label(text="No get_stf_prop_holder or operator_set_stf_id: " + str(stf_handler))
		return

	layout.box().label(text=stf_handler.stf_type)
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
		layout.separator(factor=2, type="LINE")
		header, body = layout.panel("stf.node_components", default_closed = False)
		header.label(text="STF Components (" + str(len(stf_handler.get_components(blender_resource))) + ")", icon="GROUP")
		if(body): draw_components_ui(body, context, stf_handler.get_stf_prop_holder(blender_resource), stf_handler.get_components_holder(blender_resource), stf_handler.operator_component_add, stf_handler.operator_component_remove, stf_handler.operator_component_edit)


import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, STFReport, add_component, export_component_base, import_component_base


_stf_type = "stfexp.node.ethereal"
_blender_property_name = "stfexp_node_ethereal"


class STFEXP_Node_Ethereal(STF_ComponentResourceBase):
	pass


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Node_Ethereal):
	pass


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
	component_ref, component = add_component(context_resource, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_resource)

	return component


def _stf_export(context: STF_ExportContext, blender_resource: STFEXP_Node_Ethereal, context_resource: Any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, blender_resource, _blender_property_name, context_resource)

	return ret, blender_resource.stf_id


class Handler_STFEXP_Node_Ethereal(STF_Handler_Component):
	"""An `stf.node` with this component on it will be removed once an import into a game-engine concludes"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [STFEXP_Node_Ethereal]
	import_resource = _stf_import
	export_resource = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Object]
	draw = _draw_component

	like_types = ["ethereal"]

	pretty_name_template = "Ethereal"


register_stf_handlers = [
	Handler_STFEXP_Node_Ethereal
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Node_Ethereal))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)

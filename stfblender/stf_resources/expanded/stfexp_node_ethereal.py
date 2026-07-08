import bpy
from typing import Any

from ...common import PSTF_ExportContext, PSTF_ImportContext, STF_Category
from ...common.resource.component import STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref
from ....stf_blender_common.operators.base_operators_component import add_component, export_component_base, import_component_base


_stf_type = "stfexp.node.ethereal"
_blender_property_name = "stfexp_node_ethereal"


class STFEXP_Node_Ethereal(STF_ComponentResourceBase):
	pass


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STFEXP_Node_Ethereal):
	pass


def _stf_import(context: PSTF_ImportContext, json_resource: dict, id: str, context_object: Any) -> Any:
	component_ref, component = add_component(context_object, _blender_property_name, id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)

	return component


def _stf_export(context: PSTF_ExportContext, component: STFEXP_Node_Ethereal, context_object: Any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)

	return ret, component.stf_id


class Handler_STFEXP_Node_Ethereal(STF_Handler_Component):
	"""An `stf.node` with this component on it will be removed once an import into a game-engine concludes"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	understood_application_types = [STFEXP_Node_Ethereal]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Object]
	draw_component_func = _draw_component

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

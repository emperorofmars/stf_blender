import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STFReport, add_component, export_component_base, import_component_base


class STFEXP_Node_Ethereal(STF_ComponentResourceBase):
	pass


class Handler_STFEXP_Node_Ethereal(STF_Handler_Component):
	"""An `stf.node` with this component on it will be removed once an import into a game-engine concludes"""
	stf_type = "stfexp.node.ethereal"
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [STFEXP_Node_Ethereal]
	like_types = ["ethereal"]
	blender_property_name = "stfexp_node_ethereal"
	single = True
	filter = [bpy.types.Object]
	pretty_name_template = "Ethereal"

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)
		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: STFEXP_Node_Ethereal, context_resource: Any) -> tuple[dict, str]:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)
		return ret, component.stf_id


def register():
	setattr(bpy.types.Object, Handler_STFEXP_Node_Ethereal.blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Node_Ethereal))

def unregister():
	if hasattr(bpy.types.Object, Handler_STFEXP_Node_Ethereal.blender_property_name):
		delattr(bpy.types.Object, Handler_STFEXP_Node_Ethereal.blender_property_name)

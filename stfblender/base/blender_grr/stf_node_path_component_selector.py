import bpy

from .utils import draw_component_info
from .stf_node_path_selector import *
from ...importer.stf_import_context import STF_ImportContext
from ...exporter.stf_export_context import STF_ExportContext
from ...utils.reference_helper import get_resource_id, import_resource, register_exported_resource
from ..stf_module_component import STF_Component_Ref


class NodePathComponentSelector(bpy.types.PropertyGroup):
	target: bpy.props.PointerProperty(type=NodePathSelector, name="Object") # type: ignore
	target_component: bpy.props.StringProperty(name="Component") # type: ignore


def draw_node_path_component_selector(layout: bpy.types.UILayout, nps: NodePathComponentSelector):
	draw_node_path_selector(layout, nps.target)
	if(target := resolve_node_path_selector(nps.target)):
		layout.prop_search(nps, "target_component", target.stf_info, "stf_components", icon="ERROR" if not nps.target_component or nps.target_component not in target.stf_info.stf_components else "NONE")
		if(nps.target_component):
			draw_component_info(layout, target, target.stf_info, nps.target_component)


def resolve_node_path_component_selector(nps: NodePathComponentSelector) -> bpy.types.Object | bpy.types.Bone | None:
	if(component_holder := resolve_node_path_selector(nps)):
		if(nps.target_component in component_holder.stf_info.stf_components):
			component_ref: STF_Component_Ref = component_holder.stf_info.stf_components[nps.target_component]
			for component in getattr(component_holder, component_ref.blender_property_name):
				if(component.stf_id == component_ref.stf_id):
					return component
	return None


def validate_node_path_component_selector(nps: NodePathComponentSelector) -> bool:
	return resolve_node_path_component_selector(nps) != None


def node_path_component_selector_to_stf(context: STF_ExportContext, nps: NodePathComponentSelector, json_resource: dict) -> list:
	if(nps.target_component):
		if(ret := node_path_selector_to_stf(context, nps.target, json_resource)):
			return ret + ["components", register_exported_resource(json_resource, nps.target_component)]
	return None


def node_path_component_selector_from_stf(context: STF_ImportContext, json_resource: dict, node_path: list, nps: NodePathComponentSelector):
	if("components" in node_path):
		idx = node_path.index("components")
		if(len(node_path) > idx + 1):
			node_path_selector_from_stf(context, json_resource, node_path[0 : idx], nps.target)
			nps.target_component = get_resource_id( json_resource, node_path[idx + 1])

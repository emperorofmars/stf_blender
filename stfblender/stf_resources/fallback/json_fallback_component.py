import bpy
import json
from typing import Any

from ...common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STF_Category
from ...common.resource.component import STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref
from ...common.resource.component.component_utils import add_component, export_component_base, import_component_base, preserve_component_reference
from ...common.blender_grr import BlenderGRR, construct_blender_grr, resolve_blender_grr
from .json_fallback_buffer import STF_FallbackBuffer, decode_buffer, encode_buffer
from .json_fallback_ui import draw_fallback


_blender_property_name = "stf_json_fallback_component"


class JsonFallbackComponent(STF_ComponentResourceBase):
	json: bpy.props.StringProperty(name="Raw Json", default="{\"type\": \"\"}", options=set()) # type: ignore
	referenced_resources: bpy.props.CollectionProperty(type=BlenderGRR, name="Referenced Resources", options=set()) # type: ignore
	active_referenced_resource: bpy.props.IntProperty() # type: ignore
	buffers: bpy.props.CollectionProperty(type=STF_FallbackBuffer, name="Buffers", options=set()) # type: ignore
	active_buffer: bpy.props.IntProperty() # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: JsonFallbackComponent):
	draw_fallback(layout, component_ref, component)


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: Any) -> Any:
	component_ref, component = add_component(context_object, _blender_property_name, id, json_resource["type"])
	component: JsonFallbackComponent = component
	import_component_base(context, component, json_resource, _blender_property_name, context_object)

	component.json = json.dumps(json_resource)

	_get_component = preserve_component_reference(component, _blender_property_name, context_object)

	def _handle():
		component = _get_component()
		for resource_id in json_resource.get("referenced_resources", []):
			resource_grr = component.referenced_resources.add()
			if(referenced_resource := context._import_resource(resource_id)):
				construct_blender_grr(referenced_resource, resource_grr)
	context.add_task(STF_TaskSteps.FINALE, _handle)

	for buffer_id in json_resource.get("referenced_buffers", []):
		encode_buffer(context, buffer_id, component)

	return component


def _stf_export(context: STF_ExportContext, component: JsonFallbackComponent, context_object: Any) -> tuple[dict, str]:
	try:
		json_component = json.loads(component.json)
		if("type" not in json_component or not json_component["type"]):
			return None
		ret = export_component_base(context, json_component["type"], component, _blender_property_name, context_object)
		ret = ret | json_component

		ret["referenced_resources"] = []
		ret["referenced_buffers"] = []

		def _handle():
			for referenced_resource in component.referenced_resources:
				if(blender_resource := resolve_blender_grr(referenced_resource)):
					print("Exporting From Fallback")
					context.serialize_resource(ret, blender_resource)

		context.add_task(STF_TaskSteps.FINALE, _handle)

		for buffer in component.buffers:
			decode_buffer(context, ret, buffer)

		return ret, component.stf_id
	except:
		return None


class Handler_JsonFallbackComponent(STF_Handler_Component):
	"""This type is not supported.
	You have to edit the raw json string, resource references and base64 encoded binary buffers"""
	stf_type = None
	stf_category = STF_Category.COMPONENT
	understood_application_types = [JsonFallbackComponent]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	draw_component_func = _draw_component

	like_types = []


register_stf_handlers = [
	Handler_JsonFallbackComponent
]


def register():
	# register wherever components could be possibly added
	setattr(bpy.types.Action, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Armature, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Brush, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Camera, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Curve, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.TextCurve, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Curves, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.GreasePencil, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Key, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Lattice, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Library, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Light, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.LightProbe, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Mask, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Material, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Mesh, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.MetaBall, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.MovieClip, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.NodeTree, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.PaintCurve, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Palette, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.PointCloud, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Scene, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Screen, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Sound, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Speaker, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Text, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Texture, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Volume, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.WindowManager, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.WorkSpace, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.World, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))


def unregister():
	if hasattr(bpy.types.Action, _blender_property_name): delattr(bpy.types.Action, _blender_property_name)
	if hasattr(bpy.types.Armature, _blender_property_name): delattr(bpy.types.Armature, _blender_property_name)
	if hasattr(bpy.types.Brush, _blender_property_name): delattr(bpy.types.Brush, _blender_property_name)
	if hasattr(bpy.types.Camera, _blender_property_name): delattr(bpy.types.Camera, _blender_property_name)
	if hasattr(bpy.types.Collection, _blender_property_name): delattr(bpy.types.Collection, _blender_property_name)
	if hasattr(bpy.types.Curve, _blender_property_name): delattr(bpy.types.Curve, _blender_property_name)
	if hasattr(bpy.types.TextCurve, _blender_property_name): delattr(bpy.types.TextCurve, _blender_property_name)
	if hasattr(bpy.types.Curves, _blender_property_name): delattr(bpy.types.Curves, _blender_property_name)
	if hasattr(bpy.types.GreasePencil, _blender_property_name): delattr(bpy.types.GreasePencil, _blender_property_name)
	if hasattr(bpy.types.Key, _blender_property_name): delattr(bpy.types.Key, _blender_property_name)
	if hasattr(bpy.types.Lattice, _blender_property_name): delattr(bpy.types.Lattice, _blender_property_name)
	if hasattr(bpy.types.Library, _blender_property_name): delattr(bpy.types.Library, _blender_property_name)
	if hasattr(bpy.types.Light, _blender_property_name): delattr(bpy.types.Light, _blender_property_name)
	if hasattr(bpy.types.LightProbe, _blender_property_name): delattr(bpy.types.LightProbe, _blender_property_name)
	if hasattr(bpy.types.Mask, _blender_property_name): delattr(bpy.types.Mask, _blender_property_name)
	if hasattr(bpy.types.Material, _blender_property_name): delattr(bpy.types.Material, _blender_property_name)
	if hasattr(bpy.types.Mesh, _blender_property_name): delattr(bpy.types.Mesh, _blender_property_name)
	if hasattr(bpy.types.MetaBall, _blender_property_name): delattr(bpy.types.MetaBall, _blender_property_name)
	if hasattr(bpy.types.MovieClip, _blender_property_name): delattr(bpy.types.MovieClip, _blender_property_name)
	if hasattr(bpy.types.NodeTree, _blender_property_name): delattr(bpy.types.NodeTree, _blender_property_name)
	if hasattr(bpy.types.Object, _blender_property_name): delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.PaintCurve, _blender_property_name): delattr(bpy.types.PaintCurve, _blender_property_name)
	if hasattr(bpy.types.Palette, _blender_property_name): delattr(bpy.types.Palette, _blender_property_name)
	if hasattr(bpy.types.PointCloud, _blender_property_name): delattr(bpy.types.PointCloud, _blender_property_name)
	if hasattr(bpy.types.Scene, _blender_property_name): delattr(bpy.types.Scene, _blender_property_name)
	if hasattr(bpy.types.Sound, _blender_property_name): delattr(bpy.types.Sound, _blender_property_name)
	if hasattr(bpy.types.Speaker, _blender_property_name): delattr(bpy.types.Speaker, _blender_property_name)
	if hasattr(bpy.types.Text, _blender_property_name): delattr(bpy.types.Text, _blender_property_name)
	if hasattr(bpy.types.Texture, _blender_property_name): delattr(bpy.types.Texture, _blender_property_name)
	if hasattr(bpy.types.Volume, _blender_property_name): delattr(bpy.types.Volume, _blender_property_name)
	if hasattr(bpy.types.WindowManager, _blender_property_name): delattr(bpy.types.WindowManager, _blender_property_name)
	if hasattr(bpy.types.WorkSpace, _blender_property_name): delattr(bpy.types.WorkSpace, _blender_property_name)
	if hasattr(bpy.types.World, _blender_property_name): delattr(bpy.types.World, _blender_property_name)

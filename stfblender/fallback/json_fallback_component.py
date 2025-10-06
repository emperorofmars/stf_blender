import bpy
import json

from ..base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ..exporter.stf_export_context import STF_ExportContext
from ..importer.stf_import_context import STF_ImportContext
from ..utils.component_utils import add_component
from .json_fallback_properties import _fallback_component_blender_property_name


_blender_property_name = _fallback_component_blender_property_name


class JsonFallbackComponent(STF_BlenderComponentBase):
	stf_type: bpy.props.StringProperty(name="STF Type", options=set()) # type: ignore
	json: bpy.props.StringProperty(name="Raw Json", default="{\"type\": \"\"}", options=set()) # type: ignore
	#referenced_resources:
	#buffers:


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: JsonFallbackComponent):
	col = layout.column(align=True)
	col.label(text="Json Data:", icon="PASTEDOWN")

	json_error = False
	try:
		json.loads(component.json)
	except:
		json_error = True
	col.alert = json_error
	col.prop(component, "json", text="", icon="ERROR" if json_error else "NONE")

	#layout.prop(component, "referenced_resources")
	#layout.prop(component, "buffers")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, id, json_resource["type"])

	component.stf_type = json_resource["type"]
	component.json = json.dumps(json_resource)

	#component.referenced_resources = json_resource.get("referenced_resources")
	#component.referenced_buffers = json_resource.get("buffers")

	return component


def _stf_export(context: STF_ExportContext, component: JsonFallbackComponent, context_object: any) -> tuple[dict, str]:
	return json.loads(component.json), component.stf_id, context


class STF_Module_JsonFallbackComponent(STF_BlenderComponentModule):
	"""This type is not supported.
	You have to edit the raw json string, resource references and base64 encoded binary buffers"""
	stf_type = None
	stf_kind = "component"
	understood_application_types = [JsonFallbackComponent]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = None
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_JsonFallbackComponent
]


def register():
	# register wherever components could be possibly added
	setattr(bpy.types.Action, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Armature, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Brush, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Camera, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Curve, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.Curves, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.GreasePencil, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
	setattr(bpy.types.GreasePencilv3, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent))
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
	if hasattr(bpy.types.Curves, _blender_property_name): delattr(bpy.types.Curves, _blender_property_name)
	if hasattr(bpy.types.GreasePencil, _blender_property_name): delattr(bpy.types.GreasePencil, _blender_property_name)
	if hasattr(bpy.types.GreasePencilv3, _blender_property_name): delattr(bpy.types.GreasePencilv3, _blender_property_name)
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

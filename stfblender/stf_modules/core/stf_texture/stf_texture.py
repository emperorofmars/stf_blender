import bpy

from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base
from ....utils.id_utils import ensure_stf_id


_stf_type = "stf.texture"
_blender_property_name = "stf_texture"


class STF_Texture(STF_BlenderComponentBase):
	"""Define information on how an image is to be uploaded to the GPU"""
	width: bpy.props.IntProperty(name="Width", subtype="PIXEL", default=1024, min=1, options=set()) # type: ignore
	height: bpy.props.IntProperty(name="Height", subtype="PIXEL", default=1024, min=1, options=set()) # type: ignore
	downscale_priority: bpy.props.IntProperty(name="Downscale Priority", default=0, min=-1, options=set()) # type: ignore
	quality: bpy.props.FloatProperty(name="Quality", subtype="FACTOR", default=1, min=0, max=1, options=set()) # type: ignore
	mipmaps: bpy.props.BoolProperty(name="Mipmaps", default=True, options=set()) # type: ignore
	# TODO much more


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_Texture):
	col = layout.column(align=True)
	col.use_property_split = True
	col.prop(component, "width")
	col.prop(component, "height")
	col.prop(component, "downscale_priority")
	col.prop(component, "quality")
	col.prop(component, "mipmaps")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)

	component.width = json_resource.get("width", 1024)
	component.height = json_resource.get("height", 1024)
	component.downscale_priority = json_resource.get("downscale_priority", 0)
	component.quality = json_resource.get("quality", 1)
	component.mipmaps = json_resource.get("mipmaps", True)

	return component


def _stf_export(context: STF_ExportContext, component: STF_Texture, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	ret["width"] = component.width
	ret["height"] = component.height
	ret["downscale_priority"] = component.downscale_priority
	ret["quality"] = component.quality
	ret["mipmaps"] = component.mipmaps
	return ret, component.stf_id


class STF_Module_STF_Texture(STF_BlenderComponentModule):
	"""Information how an Image is to be processed into a GPU texture"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [STF_Texture]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Image]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_STF_Texture
]


def register():
	setattr(bpy.types.Image, _blender_property_name, bpy.props.CollectionProperty(type=STF_Texture, options=set()))

def unregister():
	if hasattr(bpy.types.Image, _blender_property_name):
		delattr(bpy.types.Image, _blender_property_name)

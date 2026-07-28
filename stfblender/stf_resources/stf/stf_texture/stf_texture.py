import bpy
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STFReport, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, add_component, export_component_base, import_component_base


class STF_Texture(STF_ComponentResourceBase):
	"""Define information on how an image is to be uploaded to the GPU"""
	width: bpy.props.IntProperty(name="Width", subtype="PIXEL", default=1024, min=1, options=set())
	height: bpy.props.IntProperty(name="Height", subtype="PIXEL", default=1024, min=1, options=set())
	downscale_priority: bpy.props.IntProperty(name="Downscale Priority", default=0, min=-1, options=set())
	quality: bpy.props.FloatProperty(name="Quality", subtype="FACTOR", default=1, min=0, max=1, options=set())
	mipmaps: bpy.props.BoolProperty(name="Mipmaps", default=True, options=set())
	# TODO more gpu texture relevant properties


class Handler_STF_Texture(STF_Handler_Component):
	"""Information how an Image is to be processed into a GPU texture"""
	stf_type = "stf.texture"
	stf_category = STF_Category.COMPONENT
	like_types = ["texture"]
	understood_blender_types = [STF_Texture]
	blender_property_name = "stf_texture"
	single = True
	filter = [bpy.types.Image]
	pretty_name_template = "Texture Settings"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STF_Texture):
		col = layout.column(align=True)
		col.use_property_split = True
		col.prop(component, "width")
		col.prop(component, "height")
		col.prop(component, "downscale_priority")
		col.prop(component, "quality")
		col.prop(component, "mipmaps")

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		component.width = json_resource.get("width", 1024)
		component.height = json_resource.get("height", 1024)
		component.downscale_priority = json_resource.get("downscale_priority", 0)
		component.quality = json_resource.get("quality", 1)
		component.mipmaps = json_resource.get("mipmaps", True)

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: STF_Texture, context_resource: Any) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)
		ret["width"] = component.width
		ret["height"] = component.height
		ret["downscale_priority"] = component.downscale_priority
		ret["quality"] = component.quality
		ret["mipmaps"] = component.mipmaps
		return ret, component.stf_id


def register():
	setattr(bpy.types.Image, Handler_STF_Texture.blender_property_name, bpy.props.CollectionProperty(type=STF_Texture, options=set()))

def unregister():
	if hasattr(bpy.types.Image, Handler_STF_Texture.blender_property_name):
		delattr(bpy.types.Image, Handler_STF_Texture.blender_property_name)

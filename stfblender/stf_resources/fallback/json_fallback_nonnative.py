import bpy
import json
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STF_Category, STF_Handler_NonNative, STF_NonNativeResourceBase, STF_NonNativeResource_Ref, STFReport, add_nonnative_resource, export_nonnative_resource_base, get_components_from_nonnative_resource, import_nonnative_resource_base
from ....stfblender_common.blender_grr import BlenderGRR
from .json_fallback_buffer import STF_FallbackBuffer, decode_buffer, encode_buffer
from .json_fallback_ui import draw_fallback


class JsonFallbackNonNative(STF_NonNativeResourceBase):
	json: bpy.props.StringProperty(name="Raw Json")
	referenced_resources: bpy.props.CollectionProperty(type=BlenderGRR, name="Referenced Resources", options=set())
	active_referenced_resource: bpy.props.IntProperty()
	buffers: bpy.props.CollectionProperty(type=STF_FallbackBuffer, name="Buffers", options=set())
	active_buffer: bpy.props.IntProperty()


class Handler_JsonFallbackNonNative(STF_Handler_NonNative):
	"""This type is not supported.
	You have to edit the raw json string, resource references and base64 encoded binary buffers"""
	stf_type = None # pyright: ignore[reportAssignmentType]
	stf_category = STF_Category.DATA
	understood_blender_types = [JsonFallbackNonNative]
	blender_property_name = "stf_json_fallback_data"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, resource_ref: STF_NonNativeResource_Ref, context_resource: bpy.types.Collection | None, resource: JsonFallbackNonNative):
		draw_fallback(layout, resource_ref, resource)

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: bpy.types.Collection | None) -> Any | STFReport:
		resource_ref, resource = add_nonnative_resource(context_resource, cls.blender_property_name, stf_id, json_resource["type"]) # pyright: ignore[reportArgumentType]
		resource: JsonFallbackNonNative = resource
		import_nonnative_resource_base(resource, json_resource)

		resource.json = json.dumps(json_resource)

		def _handle():
			for resource in getattr(context_resource, cls.blender_property_name): # The `resource` object is very likely invalidated
				if(stf_id == resource.stf_id):
					break
			else:
				return
			for resource_id in json_resource.get("referenced_resources", []):
				resource_grr = resource.referenced_resources.add()
				if(referenced_resource := context._import_resource(resource_id)):
					resource_grr.construct(referenced_resource, resource_id)
		context.add_task(STF_TaskSteps.FINALE, _handle)

		for buffer_id in json_resource.get("referenced_buffers", []):
			encode_buffer(context, buffer_id, resource) # pyright: ignore[reportArgumentType]

		return resource

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: JsonFallbackNonNative, context_resource: Any) -> tuple[dict, str] | STFReport:
		try:
			json_resource = json.loads(blender_resource.json)
			if("type" not in json_resource or not json_resource["type"]):
				return None # pyright: ignore[reportReturnType]
			ret = export_nonnative_resource_base(context, json_resource["type"], blender_resource)
			ret = ret | json_resource

			ret["referenced_resources"] = []
			ret["referenced_buffers"] = []

			for referenced_resource in blender_resource.referenced_resources:
				referenced_resource: BlenderGRR = referenced_resource
				if(blender_resource := referenced_resource.resolve()):
					def _handle():
						context.serialize_resource(ret, blender_resource)
					context.add_task(STF_TaskSteps.FINALE, _handle)

			for buffer in blender_resource.buffers:
				decode_buffer(context, ret, buffer)

			return ret, blender_resource.stf_id
		except Exception:
			return None # pyright: ignore[reportReturnType]

	get_components = get_components_from_nonnative_resource


def register():
	setattr(bpy.types.Collection, Handler_JsonFallbackNonNative.blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackNonNative, options=set()))

def unregister():
	if hasattr(bpy.types.Collection, Handler_JsonFallbackNonNative.blender_property_name):
		delattr(bpy.types.Collection, Handler_JsonFallbackNonNative.blender_property_name)

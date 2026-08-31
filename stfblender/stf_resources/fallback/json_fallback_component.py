import bpy
import json
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, STFReport, add_component, export_component_base, import_component_base, preserve_component_reference
from ....stfblender_common.blender_grr import BlenderGRR, construct_blender_grr, resolve_blender_grr
from ...register_stf_data import blender_types
from .json_fallback_buffer import STF_FallbackBuffer, decode_buffer, encode_buffer
from .json_fallback_ui import draw_fallback


class JsonFallbackComponent(STF_ComponentResourceBase):
	json: bpy.props.StringProperty(name="Raw Json", default="{\"type\": \"\"}", options=set())
	referenced_resources: bpy.props.CollectionProperty(type=BlenderGRR, name="Referenced Resources", options=set())
	active_referenced_resource: bpy.props.IntProperty()
	buffers: bpy.props.CollectionProperty(type=STF_FallbackBuffer, name="Buffers", options=set())
	active_buffer: bpy.props.IntProperty()


class Handler_JsonFallbackComponent(STF_Handler_Component):
	"""This type is not supported.
	You have to edit the raw json string, resource references and base64 encoded binary buffers"""
	stf_type = None # pyright: ignore[reportAssignmentType]
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [JsonFallbackComponent]
	blender_property_name = "stf_json_fallback_component"
	single = False

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: JsonFallbackComponent):
		draw_fallback(layout, component_ref, component)

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, json_resource["type"]) # pyright: ignore[reportAssignmentType]
		component: JsonFallbackComponent = component
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		component.json = json.dumps(json_resource)

		_get_component = preserve_component_reference(component, cls.blender_property_name, context_resource)

		def _handle():
			component = _get_component()
			for resource_id in json_resource.get("referenced_resources", []):
				resource_grr = component.referenced_resources.add()
				if(referenced_resource := context._import_resource(resource_id)):
					construct_blender_grr(referenced_resource, resource_grr)
		context.add_task(STF_TaskSteps.FINALE, _handle)

		for buffer_id in json_resource.get("referenced_buffers", []):
			encode_buffer(context, buffer_id, component) # pyright: ignore[reportArgumentType]

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: JsonFallbackComponent, context_resource: Any) -> tuple[dict, str]:
		try:
			json_component = json.loads(blender_resource.json)
			if("type" not in json_component or not json_component["type"]):
				return None # pyright: ignore[reportReturnType]
			ret = export_component_base(context, json_component["type"], blender_resource, cls.blender_property_name, context_resource)
			ret = ret | json_component

			ret["referenced_resources"] = []
			ret["referenced_buffers"] = []

			component = blender_resource
			def _handle():
				for referenced_resource in component.referenced_resources:
					if(blender_resource := resolve_blender_grr(referenced_resource)):
						context.serialize_resource(ret, blender_resource)

			context.add_task(STF_TaskSteps.FINALE, _handle)

			for buffer in blender_resource.buffers:
				decode_buffer(context, ret, buffer)

			return ret, blender_resource.stf_id
		except Exception:
			return None # pyright: ignore[reportReturnType]


def register():
	# register wherever components could be possibly added
	for blender_type in blender_types:
		setattr(blender_type, Handler_JsonFallbackComponent.blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackComponent, name="STF Fallback Components", options=set()))

def unregister():
	for blender_type in blender_types:
		if hasattr(blender_type, Handler_JsonFallbackComponent.blender_property_name): delattr(blender_type, Handler_JsonFallbackComponent.blender_property_name)

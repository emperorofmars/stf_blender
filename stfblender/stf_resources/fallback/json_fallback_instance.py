import bpy
import json
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_BlenderNative, STFReport, STFSetIDOperatorBase, ensure_stf_id
from ....stfblender_common.blender_grr import BlenderGRR, construct_blender_grr, resolve_blender_grr
from .json_fallback_buffer import STF_FallbackBuffer, decode_buffer, encode_buffer
from .json_fallback_ui import draw_fallback


_blender_property_name = "stf_json_fallback_instance"


class STFSetFallbackInstanceIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Fallback-Instance"""
	bl_idname = "stf.set_fallback_instance_stf_id"
	@classmethod
	def poll(cls, context) -> bool: return hasattr(context, "object") and context.object is not None and context.object.stf_instance is not None
	def get_property(self, context): return context.object.stf_instance


class JsonFallbackInstance(STF_ComponentResourceBase):
	stf_type: bpy.props.StringProperty(options=set())
	stf_id: bpy.props.StringProperty(options=set())
	json: bpy.props.StringProperty(name="Raw Json", default="{\"type\": \"\"}", options=set())
	referenced_resources: bpy.props.CollectionProperty(type=BlenderGRR, name="Referenced Resources", options=set())
	active_referenced_resource: bpy.props.IntProperty()
	buffers: bpy.props.CollectionProperty(type=STF_FallbackBuffer, name="Buffers", options=set())
	active_buffer: bpy.props.IntProperty()
	blender_property_name: bpy.props.StringProperty(default=_blender_property_name, options={"READ_ONLY"})


class Handler_JsonFallbackInstance(STF_Handler_BlenderNative):
	"""This type is not supported.
	You have to edit the raw json string, resource references and base64 encoded binary buffers"""
	stf_type = None # pyright: ignore[reportAssignmentType]
	stf_category = STF_Category.INSTANCE
	understood_blender_types = [tuple]
	blender_property_name = _blender_property_name
	operator_set_stf_id = STFSetFallbackInstanceIDOperator.bl_idname
	get_stf_prop_holder = lambda blender_resource: blender_resource[0].stf_instance

	@classmethod
	def can_handle_blender_resource(cls, blender_resource: Any) -> int:
		if(type(blender_resource) is tuple and type(blender_resource[0]) is bpy.types.Object and type(blender_resource[1]) is JsonFallbackInstance):
			return 1000
		else:
			return -1

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, blender_resource: Any) -> None | bool:
		blender_object: bpy.types.Object = blender_resource[0]
		fallback_instance: JsonFallbackInstance = blender_resource[1]
		json_instance = json.loads(fallback_instance.json)
		layout.label(text="Instance Fallback: " + str(json_instance.get("type")))
		draw_fallback(layout, fallback_instance, fallback_instance, True) # pyright: ignore[reportArgumentType]


	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		blender_object = bpy.data.objects.new(json_resource.get("name", "STF Fallback"), None)

		blender_object.stf_instance.use_fallback_resource = True
		blender_object.stf_instance.stf_id = stf_id
		if(json_resource.get("name")):
			blender_object.stf_instance.stf_name = json_resource["name"]

		fallback_instance: JsonFallbackInstance = getattr(blender_object, cls.blender_property_name)
		fallback_instance.stf_type = json_resource.get("type")
		fallback_instance.stf_id = stf_id
		fallback_instance.json = json.dumps(json_resource)

		def _handle():
			for resource_id in json_resource.get("referenced_resources", []):
				resource_grr = fallback_instance.referenced_resources.add()
				if(referenced_resource := context._import_resource(resource_id)):
					construct_blender_grr(referenced_resource, resource_grr)
		context.add_task(STF_TaskSteps.FINALE, _handle)

		for buffer_id in json_resource.get("referenced_buffers", []):
			encode_buffer(context, buffer_id, fallback_instance)

		return (blender_object, fallback_instance)


	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: tuple[bpy.types.Object, JsonFallbackInstance], context_resource: Any) -> tuple[dict, str] | STFReport:
		try:
			blender_object: bpy.types.Object = blender_resource[0]
			fallback_instance: JsonFallbackInstance = blender_resource[1]
			json_instance = json.loads(fallback_instance.json)

			if("type" not in json_instance or not json_instance["type"]):
				return None # pyright: ignore[reportReturnType]

			ensure_stf_id(context, blender_object.stf_instance)
			ret = {
				"type": fallback_instance.stf_type,
				"name": blender_object.stf_instance.stf_name,
			} | json_instance
			ret["referenced_resources"] = []
			ret["referenced_buffers"] = []

			def _handle():
				for referenced_resource in fallback_instance.referenced_resources:
					if(blender_resource := resolve_blender_grr(referenced_resource)):
						context.serialize_resource(ret, blender_resource)
			context.add_task(STF_TaskSteps.FINALE, _handle)

			for buffer in fallback_instance.buffers:
				decode_buffer(context, ret, buffer)

			return ret, fallback_instance.stf_id
		except Exception:
			return None # pyright: ignore[reportReturnType]


def register():
	setattr(bpy.types.Object, Handler_JsonFallbackInstance.blender_property_name, bpy.props.PointerProperty(type=JsonFallbackInstance))

def unregister():
	if hasattr(bpy.types.Object, Handler_JsonFallbackInstance.blender_property_name):
		delattr(bpy.types.Object, Handler_JsonFallbackInstance.blender_property_name)

import bpy
import base64

from ...common import STF_ExportContext, STF_ImportContext


class STF_FallbackBuffer(bpy.types.PropertyGroup):
	stf_id: bpy.props.StringProperty(name="ID", options=set()) # type: ignore
	buffer_base64: bpy.props.StringProperty(name="Base64 Buffer", options=set()) # type: ignore


def encode_buffer(context: STF_ImportContext, buffer_id: str, stf_fallback: bpy.types.CollectionProperty):
	blender_buffer = stf_fallback.buffers.add()
	blender_buffer.name = buffer_id
	blender_buffer.stf_id = buffer_id
	if(buffer := context._import_buffer(buffer_id)):
		blender_buffer.buffer_base64 = base64.standard_b64encode(buffer).decode("ascii") # I hate this


def decode_buffer(context: STF_ExportContext, json_parent: dict, stf_fallback: STF_FallbackBuffer) -> str:
	return context.serialize_buffer(json_parent, base64.standard_b64decode(stf_fallback.buffer_base64), stf_fallback.stf_id)

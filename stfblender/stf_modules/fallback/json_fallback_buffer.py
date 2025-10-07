import bpy
import base64

from ...importer.stf_import_context import STF_ImportContext
from ...exporter.stf_export_context import STF_ExportContext


class STF_FallbackBuffer(bpy.types.PropertyGroup):
	stf_id: bpy.props.StringProperty(name="ID", options=set()) # type: ignore
	buffer_base64: bpy.props.StringProperty(name="Base64 Buffer", options=set()) # type: ignore


def encode_buffer(context: STF_ImportContext, buffer_id: str, stf_fallback: bpy.types.CollectionProperty):
	blender_buffer = stf_fallback.buffers.add()
	if(buffer := context.import_buffer(buffer_id)):
		blender_buffer.name = buffer_id
		blender_buffer.stf_id = buffer_id
		blender_buffer.buffer_base64 = base64.standard_b64encode(buffer).decode("ascii") # I hate this


def decode_buffer(context: STF_ExportContext, stf_fallback: STF_FallbackBuffer) -> str:
	return context.serialize_buffer(base64.standard_b64decode(stf_fallback.buffer_base64), stf_fallback.stf_id)

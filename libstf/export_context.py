import io

class ExportContext:
	__resources: dict[any, dict] # Blender type -> exported STF Json object
	__buffer_definitions: dict[any, dict] # Blender type -> exported STF json buffer object
	__buffers: list[io.BytesIO] # Actual binary buffers

	def export(object: any) -> dict | None:

		return None

	def serialize_buffer(data: io.BytesIO) -> str:
		pass

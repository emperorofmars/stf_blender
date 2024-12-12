
import io
import json


class STF_Meta_AssetInfo:
	asset_name: str
	asset_author: str
	asset_version: str
	asset_license: str
	asset_license_url: str
	asset_documentation: str
	asset_documentation_url: str
	generator: str
	timestamp: str

class STF_Meta:
	version_major: int = 0
	version_minor: int = 0
	root: str
	profiles: list[str] = []
	meta: STF_Meta_AssetInfo = STF_Meta_AssetInfo()

class STF_Buffer_Included:
	type: str = "stf.buffer.included"
	index: int

class STF_Buffer_File:
	type: str = "stf.buffer.file"
	path: str

class STF_Buffer_JsonArray:
	type: str = "stf.buffer.json_array"
	data: list[io.BytesIO]

class STF_JsonDefinition:
	meta: STF_Meta = STF_Meta()
	resources: dict[str, dict] = dict()
	buffers: list[STF_Buffer_Included | STF_Buffer_File | STF_Buffer_JsonArray] = []


class STF_File:
	binary_version_major: int = 0
	binary_version_minor: int = 0
	#definition: STF_JsonDefinition = STF_JsonDefinition()
	definition: dict[str, dict] = {"meta": {"version_major": 0, "version_minor": 0}, "resources": {}, "buffers": []}
	buffers_included: list[io.BytesIO] = []

	@staticmethod
	def parse_from_buffer(buffer: io.BytesIO):
		ret = STF_File()
		# Read and check magic number
		magic_number = buffer.read(4)
		if(magic_number.decode("ascii") != "STF0"):
			raise ImportError("Invalid magic number, not an STF file! (" + str(magic_number) + ")")

		# Read and check STF binary version
		ret.binary_version_major = int.from_bytes(buffer.read(4), byteorder="little")
		ret.binary_version_minor = int.from_bytes(buffer.read(4), byteorder="little")

		# Read the number of buffers
		num_buffers_with_json = int.from_bytes(buffer.read(4), byteorder="little")
		num_buffers = num_buffers_with_json - 1
		if(num_buffers_with_json < 1):
			raise ImportError("Invalid number of buffers, at least one must be present!")

		# Read the length of the Json definition buffer
		json_buffer_len = int.from_bytes(buffer.read(8), byteorder="little")

		# Read the length of all other buffers
		buffer_lens = []
		for buffer_idx in range(0, num_buffers):
			buffer_lens.append(int.from_bytes(buffer.read(8), byteorder="little"))

			print(buffer_lens[len(buffer_lens) - 1])

		# Read the Json definition buffer
		ret.definition = json.loads(buffer.read(json_buffer_len).decode("utf-8"))

		# Read all other buffers
		for buffer_idx in range(0, num_buffers):
			ret.buffers_included.append(buffer.read(buffer_lens[buffer_idx]))

		return ret

	def serialize(self, buffer: io.BytesIO):
		# Serialize Magic number
		buffer.write("STF0".encode("ascii"))

		# Serialize STF binary version
		buffer.write(self.binary_version_major.to_bytes(length=4, byteorder="little"))
		buffer.write(self.binary_version_minor.to_bytes(length=4, byteorder="little"))

		# Serialize Number of buffers
		num_buffers = len(self.buffers_included)
		num_buffers_with_json = num_buffers + 1
		buffer.write(num_buffers_with_json.to_bytes(length=4, byteorder="little"))

		# Convert Json definition to buffer
		definition_buffer = json.dumps(self.definition).encode(encoding="utf-8")

		# Serialize length of Json definition buffer
		buffer_len = len(definition_buffer)
		buffer.write(buffer_len.to_bytes(length=8, byteorder="little"))

		# Serialize length of all other buffers
		for buffer_idx in range(0, num_buffers):
			buffer_len = len(self.buffers_included[buffer_idx])
			buffer.write(buffer_len.to_bytes(length=8, byteorder="little"))

		# Serialize Json definition buffer
		buffer.write(definition_buffer)

		# Serialize all other buffers
		for buffer_idx in range(0, num_buffers):
			buffer.write(self.buffers_included[buffer_idx])

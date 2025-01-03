import io
import json

from .stf_definition import STF_JsonDefinition


class STF_File:
	"""
		Holds all data of a binary STF file.
		Provides methods to parse and serialize it to and from a io-buffer, which can be a file.
	"""

	def __init__(self):
		self.binary_version_major: int = 0
		self.binary_version_minor: int = 0
		self.definition: STF_JsonDefinition = STF_JsonDefinition()
		self.buffers_included: list[io.BytesIO] = []

	@staticmethod
	def parse(buffer: io.BytesIO):
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
		ret.definition = STF_JsonDefinition.from_dict(json.loads(buffer.read(json_buffer_len).decode("utf-8")))

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
		definition_buffer = json.dumps(self.definition.to_dict()).encode(encoding="utf-8")

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

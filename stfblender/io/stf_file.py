# pyright: strict

import io
import json

from ..common.base.stf_json_definition import STF_JsonDefinition
from ..common.utils import buffer_utils

__all__ = ["STF_File"]

class STF_File:
	"""Holds all data of a binary STF file.
	Provides methods to parse and serialize it to and from a io-buffer, which can be a file"""

	def __init__(self):
		self.binary_version: int = 0
		self.padding_future_use: int = 0
		self.definition: STF_JsonDefinition = STF_JsonDefinition()
		self.buffers_included: list[bytes] = []
		self.filename: str = ""

	@staticmethod
	def parse(buffer: io.BufferedReader):
		ret = STF_File()
		ret.filename = buffer.name

		# Read and check magic number
		magic_number = buffer.read(4)
		if(magic_number.decode("ascii") != "STF0"):
			raise ImportError("Invalid magic number, not an STF file! (" + str(magic_number) + ")")

		# Read and check STF binary version
		ret.binary_version = buffer_utils.parse_uint(buffer, 4)
		ret.padding_future_use = buffer_utils.parse_uint(buffer, 4)

		# Read the number of buffers
		num_buffers_with_json = buffer_utils.parse_uint(buffer, 4)
		num_buffers = num_buffers_with_json - 1
		if(num_buffers_with_json < 1):
			raise ImportError("Invalid number of buffers, at least one must be present!")

		# Read the length of the Json definition buffer
		json_buffer_len = buffer_utils.parse_uint(buffer, 8)

		# Read the length of all other buffers
		buffer_lens: list[int] = []
		for buffer_idx in range(0, num_buffers):
			buffer_lens.append(buffer_utils.parse_uint(buffer, 8))

		# Read the Json definition buffer
		ret.definition = STF_JsonDefinition.from_dict(json.loads(buffer.read(json_buffer_len).decode("utf-8")))

		# Read all other buffers
		for buffer_idx in range(0, num_buffers):
			ret.buffers_included.append(buffer.read(buffer_lens[buffer_idx]))

		return ret

	def serialize(self, buffer: io.BufferedWriter):
		# Serialize Magic number
		buffer.write("STF0".encode("ascii"))

		# Serialize STF binary version
		buffer.write(buffer_utils.serialize_uint(self.binary_version, 4))
		buffer.write(buffer_utils.serialize_uint(self.padding_future_use, 4))

		# Serialize Number of buffers
		num_buffers = len(self.buffers_included)
		buffer.write(buffer_utils.serialize_uint(num_buffers + 1, 4)) # +1 for the Json definition buffer

		# Convert Json definition to buffer
		definition_buffer = json.dumps(self.definition.to_dict()).encode(encoding="utf-8")

		# Serialize length of Json definition buffer
		buffer.write(buffer_utils.serialize_uint(len(definition_buffer), 8))

		# Serialize length of all other buffers
		for buffer_idx in range(0, num_buffers):
			buffer.write(buffer_utils.serialize_uint(len(self.buffers_included[buffer_idx]), 8))

		# Serialize Json definition buffer
		buffer.write(definition_buffer)

		# Serialize all other buffers
		for buffer_idx in range(0, num_buffers):
			buffer.write(self.buffers_included[buffer_idx])

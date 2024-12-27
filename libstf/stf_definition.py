import io

class STF_Profile:
	name: str

class STF_Meta_AssetInfo:
	asset_name: str
	asset_author: str
	asset_version: str
	asset_license: str
	asset_license_url: str
	asset_documentation: str
	asset_documentation_url: str

	custom_values: dict[str, str] = {}

	@staticmethod
	def from_dict(dict: dict):
		ret = STF_Meta_AssetInfo()
		for key, value in dict.items():
			match key:
				case "asset_name": ret.asset_name = value
				case "asset_author": ret.asset_author = value
				case "asset_version": ret.asset_version = value
				case "asset_license": ret.asset_license = value
				case "asset_license_url": ret.asset_license_url = value
				case "asset_documentation": ret.asset_documentation = value
				case "asset_documentation_url": ret.asset_documentation_url = value
				case "generator": ret.generator = value
				case "timestamp": ret.timestamp = value
				case _: ret.custom_values.key = value

		return ret

	def to_dict(self):
		"""ret = {
			"asset_name": self.asset_name,
			"asset_author": self.asset_author,
			"asset_version": self.asset_version,
			"asset_license": self.asset_license,
			"asset_license_url": self.asset_license_url,
			"asset_documentation": self.asset_documentation,
			"asset_documentation_url": self.asset_documentation_url,
			"generator": self.generator,
			"timestamp": self.timestamp,
		}"""
		ret = vars(self)
		if("custom_values" in ret): del ret["custom_values"]
		for key, value in self.custom_values.items():
			ret[key] = value
		return ret


class STF_Meta:
	version_major: int = 0
	version_minor: int = 0
	generator: str
	timestamp: str
	root: str
	profiles: list[STF_Profile] = []
	asset_info: STF_Meta_AssetInfo = STF_Meta_AssetInfo()

	@staticmethod
	def from_dict(dict: dict):
		ret = STF_Meta()
		ret.version_major = dict["version_major"]
		ret.version_minor = dict["version_minor"]
		ret.root = dict["root"]
		ret.profiles = dict["profiles"]
		ret.asset_info = STF_Meta_AssetInfo.from_dict(dict["asset_info"])
		return ret

	def to_dict(self):
		return {
			"version_major": self.version_major,
			"version_minor": self.version_minor,
			"root": self.root,
			"profiles": self.profiles,
			"asset_info": self.asset_info.to_dict(),
		}


class STF_Buffer_Included:
	type: str = "stf.buffer.included"
	index: int

	@staticmethod
	def from_dict(dict: dict):
		ret = STF_Buffer_Included()
		ret.index = dict["index"]
		return ret

	def to_dict(self):
		return {
			"type": self.type,
			"index": self.index,
		}


class STF_Buffer_File:
	type: str = "stf.buffer.file"
	path: str

	@staticmethod
	def from_dict(dict: dict):
		ret = STF_Buffer_File()
		ret.path = dict["path"]
		return ret

	def to_dict(self):
		return {
			"type": self.type,
			"path": self.path,
		}


class STF_Buffer_JsonArray:
	type: str = "stf.buffer.json_array"
	data: list[io.BytesIO]

	@staticmethod
	def from_dict(dict: dict):
		ret = STF_Buffer_JsonArray()
		ret.data = dict["data"]
		return ret

	def to_dict(self):
		return {
			"type": self.type,
			"data": self.data,
		}


class STF_JsonDefinition:
	""" Represents the STF Json definition's top level object. """
	stf: STF_Meta = STF_Meta()
	resources: dict[str, dict] = dict()
	buffers: dict[str, STF_Buffer_Included | STF_Buffer_File | STF_Buffer_JsonArray] = dict()

	@staticmethod
	def from_dict(dict):
		ret = STF_JsonDefinition()
		ret.stf = STF_Meta.from_dict(dict["stf"])
		ret.resources = dict["resources"]
		for key, value in dict["buffers"]:
			match value.type:
				case "stf.buffer.included": ret.buffers[key] = STF_Buffer_Included.from_dict(value)
				case "stf.buffer.file": ret.buffers[key] = STF_Buffer_File.from_dict(value)
				case "stf.buffer.json_array": ret.buffers[key] = STF_Buffer_JsonArray.from_dict(value)
		return ret

	def to_dict(self):
		buffers = {}
		for key, value in self.buffers.items():
			buffers[key] = value.to_dict()
		return {
			"stf": self.stf.to_dict(),
			"resources": self.resources,
			"buffers": buffers,
		}

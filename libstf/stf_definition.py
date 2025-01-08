import io

class STF_Profile:
	def __init__(self):
		self.name: str

class STF_Meta_AssetInfo:
	def __init__(self):
		self.asset_name: str
		self.asset_author: str
		self.asset_version: str
		self.asset_license: str
		self.asset_license_url: str
		self.asset_documentation_url: str

		self.custom_properties: dict[str, str] = {}

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
				case "asset_documentation_url": ret.asset_documentation_url = value
				case _: ret.custom_properties.key = value

		return ret

	def to_dict(self):
		ret = {}
		for key, value in vars(self).items():
			match key:
				case "custom_properties":
					for key, value in self.custom_properties.items():
						ret[key] = value
				case _:
					ret[key] = value
		return ret


class STF_Meta:
	def __init__(self):
		import datetime

		self.version_major: int = 0
		self.version_minor: int = 0
		self.generator: str = "libstf_python"
		self.timestamp: str = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
		self.root: str
		self.profiles: list[STF_Profile] = []
		self.asset_info: STF_Meta_AssetInfo = STF_Meta_AssetInfo()

	@staticmethod
	def from_dict(dict: dict):
		ret = STF_Meta()
		ret.version_major = dict["version_major"]
		ret.version_minor = dict["version_minor"]
		ret.root = dict["root"]
		ret.profiles = dict["profiles"]
		ret.asset_info = STF_Meta_AssetInfo.from_dict(dict["asset_info"])
		ret.generator = dict["generator"]
		ret.timestamp = dict["timestamp"]
		return ret

	def to_dict(self):
		return {
			"version_major": self.version_major,
			"version_minor": self.version_minor,
			"root": self.root,
			"profiles": self.profiles,
			"asset_info": self.asset_info.to_dict(),
			"generator": self.generator,
			"timestamp": self.timestamp,
		}


class STF_Buffer_Included:
	def __init__(self):
		self.type: str = "stf.buffer.included"
		self.index: int

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
	def __init__(self):
		self.type: str = "stf.buffer.file"
		self.path: str

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
	def __init__(self):
		self.type: str = "stf.buffer.json_array"
		self.data: list[io.BytesIO]

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
	"""Represents the STF Json definition's top level object"""

	def __init__(self):
		self.stf: STF_Meta = STF_Meta()
		self.resources: dict[str, dict] = dict()
		self.buffers: dict[str, STF_Buffer_Included | STF_Buffer_File | STF_Buffer_JsonArray] = dict()

	@staticmethod
	def from_dict(dict):
		ret = STF_JsonDefinition()
		ret.stf = STF_Meta.from_dict(dict["stf"])
		ret.resources = dict["resources"]
		for key, value in dict["buffers"].items():
			match value["type"]:
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

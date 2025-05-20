import io

class STF_Profile:
	def __init__(self):
		self.name: str = None

class STF_Meta_AssetInfo:
	def __init__(self):
		self.asset_name: str = None
		self.version: str = None
		self.url: str = None
		self.author: str = None
		self.license: str = None
		self.license_url: str = None
		self.documentation_url: str = None

		self.custom_properties: dict[str, str] = {}

	@staticmethod
	def from_dict(dict: dict):
		ret = STF_Meta_AssetInfo()
		for key, value in dict.items():
			match key:
				case "asset_name": ret.asset_name = value
				case "version": ret.version = value
				case "url": ret.url = value
				case "author": ret.author = value
				case "license": ret.license = value
				case "license_url": ret.license_url = value
				case "documentation_url": ret.documentation_url = value
				case _: ret.custom_properties[key] = value

		return ret

	def to_dict(self):
		ret = {}
		for key, value in vars(self).items():
			if(value):
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
		self.generator_version = "0.0.0"
		self.timestamp: str = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
		self.root: str = None
		self.profiles: list[STF_Profile] = []
		self.asset_info: STF_Meta_AssetInfo = STF_Meta_AssetInfo()
		self.metric_multiplier: float = 1

	@staticmethod
	def from_dict(dict: dict):
		ret = STF_Meta()
		ret.version_major = dict["version_major"]
		ret.version_minor = dict["version_minor"]
		ret.root = dict["root"]
		ret.profiles = dict["profiles"]
		ret.asset_info = STF_Meta_AssetInfo.from_dict(dict["asset_info"])
		ret.generator = dict["generator"]
		ret.generator_version = dict["generator_version"]
		ret.timestamp = dict["timestamp"]
		ret.metric_multiplier = dict["metric_multiplier"]
		return ret

	def to_dict(self):
		return {
			"version_major": self.version_major,
			"version_minor": self.version_minor,
			"root": self.root,
			"profiles": self.profiles,
			"asset_info": self.asset_info.to_dict(),
			"generator": self.generator,
			"generator_version": self.generator_version,
			"timestamp": self.timestamp,
			"metric_multiplier": self.metric_multiplier,
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
		self.data: list[any]

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

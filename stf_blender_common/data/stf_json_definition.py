from typing import Any


class STF_Meta_AssetInfo:
	def __init__(self):
		self.asset_name: str | None = None
		self.version: str | None = None
		self.url: str | None = None
		self.author: str | None = None
		self.license: str | None = None
		self.license_url: str | None = None
		self.documentation_url: str | None = None

	@staticmethod
	def from_dict(dict: dict[str, str]):
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
		return ret

	def to_dict(self) -> dict[str, str]:
		ret = {}
		for key, value in vars(self).items():
			if(value):
				match key:
					case _:
						ret[key] = value
		return ret


class STF_Meta_AssetProperties:
	def __init__(self):
		self.custom_properties: dict[str, str] = {}

	@staticmethod
	def from_dict(dict: dict[str, str]):
		ret = STF_Meta_AssetProperties()
		for key, value in dict.items():
			ret.custom_properties[key] = value
		return ret

	def to_dict(self) -> dict[str, str]:
		ret = {}
		for key, value in vars(self).items():
			if(key and value):
				for key, value in self.custom_properties.items():
					ret[key] = value
		return ret


class STF_Meta:
	def __init__(self):
		import datetime

		self.version_major: int = 0
		self.version_minor: int = 1
		self.generator: str = "stf_blender"
		self.generator_version = "0.0.0"
		self.timestamp: str = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
		self.root: str
		self.asset_info: STF_Meta_AssetInfo = STF_Meta_AssetInfo()
		self.asset_properties: STF_Meta_AssetProperties = STF_Meta_AssetProperties()
		self.metric_multiplier: float = 1

	@staticmethod
	def from_dict(dict: dict[str, Any]):
		ret = STF_Meta()
		if("version" in dict):
			ret.version_major = dict["version"][0]
			ret.version_minor = dict["version"][1]
		else:
			ret.version_major = dict["version_major"]
			ret.version_minor = dict["version_minor"]
		ret.root = dict["root"]
		ret.asset_info = STF_Meta_AssetInfo.from_dict(dict.get("asset_info", {}))
		ret.asset_properties = STF_Meta_AssetProperties.from_dict(dict.get("asset_properties", {}))
		ret.generator = dict["generator"]
		ret.generator_version = dict["generator_version"]
		ret.timestamp = dict["timestamp"]
		ret.metric_multiplier = dict["metric_multiplier"]
		return ret

	def to_dict(self) -> dict[str, Any]:
		return {
			"version": [self.version_major, self.version_minor],
			"root": self.root,
			"asset_info": self.asset_info.to_dict(),
			"asset_properties": self.asset_properties.to_dict(),
			"generator": self.generator,
			"generator_version": self.generator_version,
			"timestamp": self.timestamp,
			"metric_multiplier": self.metric_multiplier,
		}


class STF_Buffer:
	def __init__(self):
		self.type: str = "stf.buffer.included"
		self.index: int

	@staticmethod
	def from_dict(dict: dict[str, Any]):
		ret = STF_Buffer()
		ret.index = dict["index"]
		return ret

	def to_dict(self) -> dict[str, Any]:
		return {
			"type": self.type,
			"index": self.index,
		}


class STF_JsonDefinition:
	"""Represents the STF Json definition's top level object"""

	def __init__(self):
		self.stf: STF_Meta = STF_Meta()
		self.resources: dict[str, dict] = dict()
		self.buffers: dict[str, STF_Buffer] = dict()

	@staticmethod
	def from_dict(dict: dict[str, Any]):
		ret = STF_JsonDefinition()
		ret.stf = STF_Meta.from_dict(dict["stf"])
		ret.resources = dict["resources"]
		for key, value in dict["buffers"].items():
			match value["type"]:
				case "stf.buffer.included": ret.buffers[key] = STF_Buffer.from_dict(value)
				case _: raise RuntimeError("Invalid buffer type: " + value["type"])
		return ret

	def to_dict(self) -> dict[str, Any]:
		buffers: dict[str, Any] = {}
		for key, value in self.buffers.items():
			buffers[key] = value.to_dict()
		return {
			"stf": self.stf.to_dict(),
			"resources": self.resources,
			"buffers": buffers,
		}

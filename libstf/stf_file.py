from .stf_resource import STF_Data_Resource, STF_SceneHierarchy_Resource


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
	version_major: int
	version_minor: int
	root: str
	profiles: list[str]
	meta: STF_Meta_AssetInfo

class STF_Buffer_Included:
	type: str = "stf.buffer.included"
	index: int

class STF_Buffer_File:
	type: str = "stf.buffer.file"
	path: str

class STF_Buffer_JsonArray:
	type: str = "stf.buffer.json_array"
	data: list[any]

class STF_JsonDefinition:
	meta: STF_Meta
	resources: dict[str, STF_SceneHierarchy_Resource | STF_Data_Resource]
	buffers: list[STF_Buffer_Included | STF_Buffer_File | STF_Buffer_JsonArray]


class STF_File:
	binary_version_major: int
	binary_version_minor: int
	definition: STF_JsonDefinition
	buffers_included: list[bytearray]
	buffers_file: dict[str, bytearray]

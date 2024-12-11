
from .stf_resource import STF_Data_Resource, STF_SceneHierarchy_Resource


class STF_Meta_AssetInfo:
	asset_name: str
	asset_author: str
	asset_version: str
	asset_license: str
	asset_license_url: str
	asset_documentation: str
	asset_documentation_url: str

class STF_Meta:
	version_major: int
	version_minor: int
	root: str
	profiles: list[str]
	meta: STF_Meta_AssetInfo

class STF_File:
	meta: STF_Meta
	resources: dict[str, STF_SceneHierarchy_Resource | STF_Data_Resource]
	buffers: list[bytearray]


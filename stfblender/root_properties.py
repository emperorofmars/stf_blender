import bpy

from ..libstf.stf_definition import STF_Meta_AssetInfo


class STF_KV(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(name="Property Name") # type: ignore
	value: bpy.props.StringProperty(name="Property value") # type: ignore


class STF_Meta(bpy.types.PropertyGroup):
	asset_name: bpy.props.StringProperty(name="Asset Name") # type: ignore
	asset_author: bpy.props.StringProperty(name="Author(s)") # type: ignore
	asset_version: bpy.props.StringProperty(name="Version") # type: ignore
	asset_license: bpy.props.StringProperty(name="License") # type: ignore
	asset_license_url: bpy.props.StringProperty(name="License URL") # type: ignore
	asset_documentation_url: bpy.props.StringProperty(name="Documentation URL") # type: ignore

	custom_properties: bpy.props.CollectionProperty(type=STF_KV, name="Type") # type: ignore

	def to_stf_meta_assetInfo(self) -> STF_Meta_AssetInfo:
		ret = STF_Meta_AssetInfo()
		if(self.asset_name): ret.asset_name = self.asset_name
		if(self.asset_author): ret.asset_author = self.asset_author
		if(self.asset_version): ret.asset_version = self.asset_version
		if(self.asset_license): ret.asset_license = self.asset_license
		if(self.asset_license_url): ret.asset_license_url = self.asset_license_url
		if(self.asset_documentation_url): ret.asset_documentation_url = self.asset_documentation_url
		ret.custom_properties = {}
		for custom_property in self.custom_properties:
			ret.custom_properties[custom_property.name] = custom_property.value
		return ret

	def from_stf_meta_assetInfo(self, meta: STF_Meta_AssetInfo):
		self.asset_name = meta.asset_name
		self.asset_author = meta.asset_author
		self.asset_version = meta.asset_version
		self.asset_license = meta.asset_license
		self.asset_license_url = meta.asset_license_url
		self.asset_documentation_url = meta.asset_documentation_url
		for key, value in meta.custom_properties:
			new_prop = self.custom_properties.add()
			new_prop.name = key
			new_prop.value = value


def draw_meta_editor(layout: bpy.types.UILayout, blender_scene_or_collection: bpy.types.Scene | bpy.types.Collection):
	layout.prop(blender_scene_or_collection.stf_meta, "asset_name")
	layout.prop(blender_scene_or_collection.stf_meta, "asset_author")
	layout.prop(blender_scene_or_collection.stf_meta, "asset_version")
	layout.prop(blender_scene_or_collection.stf_meta, "asset_license")
	layout.prop(blender_scene_or_collection.stf_meta, "asset_license_url")
	layout.prop(blender_scene_or_collection.stf_meta, "asset_documentation_url")
	layout.prop(blender_scene_or_collection.stf_meta, "custom_properties")


class STF_FileHandler(bpy.types.FileHandler):
	bl_idname = "IO_FH_stf"
	bl_label = "STF"
	bl_import_operator = "stf.import"
	bl_export_operator = "stf.export"
	bl_file_extensions = ".stf;.stf.json"


def register():
	bpy.types.Scene.stf_root_collection = bpy.props.PointerProperty(type=bpy.types.Collection, name="Root Collection") # type: ignore
	bpy.types.Collection.stf_meta = bpy.props.PointerProperty(type=STF_Meta, name="STF Meta") # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "stf_root_collection"):
		del bpy.types.Scene.stf_root_collection
	if hasattr(bpy.types.Collection, "stf_meta"):
		del bpy.types.Collection.stf_meta

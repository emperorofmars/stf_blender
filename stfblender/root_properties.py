import bpy

from ..libstf.stf_definition import STF_Meta_AssetInfo


class STF_KV(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(name="Name") # type: ignore
	value: bpy.props.StringProperty(name="Value") # type: ignore


class STF_Meta(bpy.types.PropertyGroup):
	asset_name: bpy.props.StringProperty(name="Asset Name") # type: ignore
	asset_version: bpy.props.StringProperty(name="Version") # type: ignore
	asset_url: bpy.props.StringProperty(name="Asset URL") # type: ignore
	asset_author: bpy.props.StringProperty(name="Author(s)") # type: ignore
	asset_license: bpy.props.StringProperty(name="License") # type: ignore
	asset_license_url: bpy.props.StringProperty(name="License URL") # type: ignore
	asset_documentation_url: bpy.props.StringProperty(name="Documentation URL") # type: ignore

	custom_properties: bpy.props.CollectionProperty(type=STF_KV, name="Type") # type: ignore

	def to_stf_meta_assetInfo(self) -> STF_Meta_AssetInfo:
		ret = STF_Meta_AssetInfo()
		if(self.asset_name): ret.asset_name = self.asset_name
		if(self.asset_version): ret.asset_version = self.asset_version
		if(self.asset_url): ret.asset_url = self.asset_url
		if(self.asset_author): ret.asset_author = self.asset_author
		if(self.asset_license): ret.asset_license = self.asset_license
		if(self.asset_license_url): ret.asset_license_url = self.asset_license_url
		if(self.asset_documentation_url): ret.asset_documentation_url = self.asset_documentation_url
		ret.custom_properties = {}
		for custom_property in self.custom_properties:
			ret.custom_properties[custom_property.name] = custom_property.value
		return ret

	def from_stf_meta_assetInfo(self, meta: STF_Meta_AssetInfo):
		if(meta.asset_name): self.asset_name = meta.asset_name
		if(meta.asset_version): self.asset_version = meta.asset_version
		if(meta.asset_url): self.asset_url = meta.asset_url
		if(meta.asset_author): self.asset_author = meta.asset_author
		if(meta.asset_license): self.asset_license = meta.asset_license
		if(meta.asset_license_url): self.asset_license_url = meta.asset_license_url
		if(meta.asset_documentation_url): self.asset_documentation_url = meta.asset_documentation_url
		for key, value in meta.custom_properties:
			if(key):
				new_prop = self.custom_properties.add()
				new_prop.name = key
				if(value):
					new_prop.value = value


class STFAddMetaPropertyCollection(bpy.types.Operator):
	bl_idname = "stf.add_meta_property_collection"
	bl_label = "Add Property"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context): return context.collection is not None

	def execute(self, context):
		context.collection.stf_meta.custom_properties.add()
		return {"FINISHED"}

class STFAddMetaPropertyScene(bpy.types.Operator):
	bl_idname = "stf.add_meta_property_scene"
	bl_label = "Add Property"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context): return context.scene is not None and context.scene.collection is not None

	def execute(self, context):
		context.scene.collection.stf_meta.custom_properties.add()
		return {"FINISHED"}


class STFRemoveMetaPropertyCollection(bpy.types.Operator):
	bl_idname = "stf.remove_meta_property_collection"
	bl_label = "Remove"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name="Index") # type: ignore

	@classmethod
	def poll(cls, context): return context.collection is not None

	def execute(self, context):
		context.collection.stf_meta.custom_properties.remove(self.index)
		return {"FINISHED"}


class STFRemoveMetaPropertyScene(bpy.types.Operator):
	bl_idname = "stf.remove_meta_property_scene"
	bl_label = "Remove"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name="Index") # type: ignore

	@classmethod
	def poll(cls, context): return context.scene is not None and context.scene.collection is not None

	def execute(self, context):
		context.scene.collection.stf_meta.custom_properties.remove(self.index)
		return {"FINISHED"}


def draw_meta_editor(layout: bpy.types.UILayout, collection: bpy.types.Collection, is_scene: bool):
	layout.prop(collection.stf_meta, "asset_name")
	layout.prop(collection.stf_meta, "asset_version")
	layout.prop(collection.stf_meta, "asset_url")
	layout.prop(collection.stf_meta, "asset_author")
	layout.prop(collection.stf_meta, "asset_license")
	layout.prop(collection.stf_meta, "asset_license_url")
	layout.prop(collection.stf_meta, "asset_documentation_url")

	for custom_property in collection.stf_meta.custom_properties:
		row = layout.split(factor=0.4)
		row.prop(custom_property, "name")
		row.prop(custom_property, "value")
		if(not is_scene):
			row.operator(STFRemoveMetaPropertyCollection.bl_idname)
		else:
			row.operator(STFRemoveMetaPropertyScene.bl_idname)

	if(not is_scene):
		layout.operator(STFAddMetaPropertyCollection.bl_idname)
	else:
		layout.operator(STFAddMetaPropertyScene.bl_idname)


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

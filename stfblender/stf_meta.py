import bpy

from .core.stf_definition import STF_Meta_AssetInfo


class STF_KV(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(name="Name") # type: ignore
	value: bpy.props.StringProperty(name="Value") # type: ignore


class STF_Meta(bpy.types.PropertyGroup):
	asset_name: bpy.props.StringProperty(name="Asset Name") # type: ignore
	version: bpy.props.StringProperty(name="Version") # type: ignore
	url: bpy.props.StringProperty(name="Asset URL") # type: ignore
	author: bpy.props.StringProperty(name="Author(s)") # type: ignore
	license: bpy.props.StringProperty(name="License") # type: ignore
	license_url: bpy.props.StringProperty(name="License URL") # type: ignore
	documentation_url: bpy.props.StringProperty(name="Documentation URL") # type: ignore

	custom_properties: bpy.props.CollectionProperty(type=STF_KV, name="Type") # type: ignore

	def to_stf_meta_assetInfo(self) -> STF_Meta_AssetInfo:
		ret = STF_Meta_AssetInfo()
		if(self.asset_name): ret.asset_name = self.asset_name
		if(self.version): ret.version = self.version
		if(self.url): ret.url = self.url
		if(self.author): ret.author = self.author
		if(self.license): ret.license = self.license
		if(self.license_url): ret.license_url = self.license_url
		if(self.documentation_url): ret.documentation_url = self.documentation_url
		ret.custom_properties = {}
		for custom_property in self.custom_properties:
			ret.custom_properties[custom_property.name] = custom_property.value
		return ret

	def from_stf_meta_assetInfo(self, meta: STF_Meta_AssetInfo):
		if(meta.asset_name): self.asset_name = meta.asset_name
		if(meta.version): self.version = meta.version
		if(meta.url): self.url = meta.url
		if(meta.author): self.author = meta.author
		if(meta.license): self.license = meta.license
		if(meta.license_url): self.license_url = meta.license_url
		if(meta.documentation_url): self.documentation_url = meta.documentation_url
		for key, value in meta.custom_properties.items():
			if(key):
				new_prop = self.custom_properties.add()
				new_prop.name = key
				if(value):
					new_prop.value = value


class STFAddMetaPropertyCollection(bpy.types.Operator):
	bl_idname = "stf.add_meta_property_collection"
	bl_label = "Add Property"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context): return context.collection is not None

	def execute(self, context):
		context.collection.stf_meta.custom_properties.add()
		return {"FINISHED"}

class STFAddMetaPropertyScene(bpy.types.Operator):
	bl_idname = "stf.add_meta_property_scene"
	bl_label = "Add Property"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context): return context.scene is not None and context.scene.collection is not None

	def execute(self, context):
		context.scene.collection.stf_meta.custom_properties.add()
		return {"FINISHED"}


class STFRemoveMetaPropertyCollection(bpy.types.Operator):
	bl_idname = "stf.remove_meta_property_collection"
	bl_label = "Remove"
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
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name="Index") # type: ignore

	@classmethod
	def poll(cls, context): return context.scene is not None and context.scene.collection is not None

	def execute(self, context):
		context.scene.collection.stf_meta.custom_properties.remove(self.index)
		return {"FINISHED"}


def draw_meta_editor(layout: bpy.types.UILayout, collection: bpy.types.Collection, is_scene: bool):
	layout.prop(collection.stf_meta, "asset_name")
	layout.prop(collection.stf_meta, "version")
	layout.prop(collection.stf_meta, "url")
	layout.prop(collection.stf_meta, "author")
	layout.prop(collection.stf_meta, "license")
	layout.prop(collection.stf_meta, "license_url")
	layout.prop(collection.stf_meta, "documentation_url")

	layout.separator(factor=1, type="LINE")
	layout.label(text="Custom Properties:")
	for custom_property in collection.stf_meta.custom_properties:
		row = layout.row()
		row.prop(custom_property, "name")
		row.separator(factor=5, type="SPACE")
		row.prop(custom_property, "value")
		row.separator(factor=2, type="SPACE")
		if(not is_scene):
			row.operator(STFRemoveMetaPropertyCollection.bl_idname, text="", icon="X")
		else:
			row.operator(STFRemoveMetaPropertyScene.bl_idname, text="", icon="X")

	if(not is_scene):
		layout.operator(STFAddMetaPropertyCollection.bl_idname, icon="ADD")
	else:
		layout.operator(STFAddMetaPropertyScene.bl_idname, icon="ADD")


def register():
	bpy.types.Scene.stf_root_collection = bpy.props.PointerProperty(type=bpy.types.Collection, name="Root Collection") # type: ignore
	bpy.types.Collection.stf_meta = bpy.props.PointerProperty(type=STF_Meta, name="STF Meta") # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "stf_root_collection"):
		del bpy.types.Scene.stf_root_collection
	if hasattr(bpy.types.Collection, "stf_meta"):
		del bpy.types.Collection.stf_meta

import bpy


def stf_docs():
	manual_map = (
		("bpy.ops.stf.export", "/guide/blender/import_export.html"),
		("bpy.ops.stf.import_files", "/guide/blender/import_export.html"),
		("bpy.types.stf_info.*", "/guide/blender/stf_concepts.html"),
		("bpy.ops.stf.add_collection_component", "/guide/blender/stf_concepts.html"),
		("bpy.ops.stf.remove_collection_component", "/guide/blender/stf_concepts.html"),
		("bpy.ops.stf.add_scene_collection_component", "/guide/blender/stf_concepts.html"),
		("bpy.ops.stf.remove_scene_collection_component", "/guide/blender/stf_concepts.html"),
		("bpy.types.ava_emotes.*", "/resources/ava/ava_expressions.html"),
		("bpy.ops.stf.add_ava_emote*", "/resources/ava/ava_expressions.html"),
	)
	return "https://docs.stfform.at", manual_map


def register():
	bpy.utils.register_manual_map(stf_docs)

def unregister():
	bpy.utils.unregister_manual_map(stf_docs)

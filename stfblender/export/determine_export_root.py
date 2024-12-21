import bpy

def traverse_tree(t):
	yield t
	for child in t.children:
		yield from traverse_tree(child)

def determine_export_root_collection(root_collection_name: str | None) -> bpy.types.Collection | None:
	ret = []

	collection = None

	for c in traverse_tree(bpy.context.scene.collection):
		if(c.name == root_collection_name):
			collection = c
			break

	return collection if collection else None

def determine_export_root_children(collection: bpy.types.Collection | None) -> list[bpy.types.Object]:
	ret = []

	for o in bpy.context.scene.objects:
		if(not o.parent and (not collection or collection in o.users_collection)):
			ret.append(o)

	print(ret)
	return ret


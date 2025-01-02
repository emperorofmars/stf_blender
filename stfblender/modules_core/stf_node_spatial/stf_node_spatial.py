import bpy

from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_export_context import STF_DataExportContext, STF_ExportContext
from ....libstf.stf_processor import STF_Processor
from ...utils.component_utils import STF_Component


_stf_type = "stf.node.spatial"


def stf_import(context: STF_ImportContext, json: dict, id: str) -> any:
	pass


class STF_BlenderNodeExportContext(STF_DataExportContext):
	def export_node(self, blender_object: bpy.types.Object) -> str:
		if(blender_object.stf_id and blender_object.stf_id in self.__resource["nodes"].keys()):
			return blender_object.stf_id
		else:
			# determine this from the registry
			(node, id) = stf_export(self, blender_object)
			self.__resource["nodes"][id] = node
			return id

def stf_export(context: STF_BlenderNodeExportContext, object: any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = object
	if(not blender_object.stf_id):
		import uuid
		blender_object.stf_id = str(uuid.uuid4())

	children = []
	for child in blender_object.children:
		children.append(context.export_node(child))

	# TODO: handle: blender_object.parent_type

	parent = None
	if(blender_object.parent):
		parent = context.export_node(parent)

	node = {
		"type": _stf_type,
		"name": blender_object.name,
		"trs": [
			blender_object.delta_location,
			blender_object.delta_rotation_quaternion,
			blender_object.delta_scale,
		],
		"parent": parent,
		"children": children,
		"components": [],
	}

	# TODO: handle node components

	return (node, blender_object.stf_id)


def register():
	bpy.types.Object.stf_id = bpy.props.StringProperty(name="Prefab ID") # type: ignore
	bpy.types.Object.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Object.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Object, "stf_id"):
		del bpy.types.Object.stf_id
	if hasattr(bpy.types.Object, "stf_components"):
		del bpy.types.Object.stf_components
	if hasattr(bpy.types.Object, "stf_active_component_index"):
		del bpy.types.Object.stf_active_component_index

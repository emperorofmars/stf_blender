import uuid
import bpy

from ...libstf.stf_import_context import STF_ImportContext
from ...libstf.stf_export_context import STF_ExportContext
from ...libstf.stf_processor import STF_Processor


_stf_type = "stf.prefab"


def _stf_import(context: STF_ImportContext, json: dict, id: str) -> any:
	pass

def _stf_export(context: STF_ExportContext, object: any) -> tuple[dict, str]:
	collection: bpy.types.Collection = object
	if(not collection.stf_id):
		collection.stf_id = str(uuid.uuid4())

	ret = {
		"type": _stf_type,
		"name": collection.name,
		"root": None,
		"nodes": None,
		"animations": None
	}
	return ret, collection.stf_id


class STF_Module_STF_Prefab(STF_Processor):
	stf_type = "stf.prefab"
	stf_kind = "data"
	understood_types = [bpy.types.Collection]
	import_func = _stf_import
	export_func = _stf_export


register_stf_processors = [
	STF_Module_STF_Prefab
]


def register():
	bpy.types.Collection.stf_id = bpy.props.StringProperty(name="ID") # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "stf_id"):
		del bpy.types.Collection.stf_id

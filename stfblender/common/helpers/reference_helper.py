from typing import Any

from ..stf_report import STFReportSeverity

from .. import STF_ImportContext, STF_ExportContext, STF_Category


def register_exported_resource(json_resource: dict, resource_id: str) -> int:
	if("referenced_resources" not in json_resource):
		json_resource["referenced_resources"] = [resource_id]
		return 0
	else:
		if(resource_id not in json_resource["referenced_resources"]):
			json_resource["referenced_resources"].append(resource_id)
			return len(json_resource["referenced_resources"]) - 1
		else:
			return json_resource["referenced_resources"].index(resource_id)

def register_exported_buffer(json_resource: dict, buffer_id: str) -> int:
	if("referenced_buffers" not in json_resource):
		json_resource["referenced_buffers"] = [buffer_id]
		return 0
	else:
		if(buffer_id not in json_resource["referenced_buffers"]):
			json_resource["referenced_buffers"].append(buffer_id)
			return len(json_resource["referenced_buffers"]) - 1
		else:
			return json_resource["referenced_buffers"].index(buffer_id)

def export_resource(context: STF_ExportContext, json_resource: dict, resource: Any, context_object: Any = None, stf_category: str | None = None, export_fail_severity: STFReportSeverity = STFReportSeverity.Error) -> int | None:
	if(resource_id := context.serialize_resource(resource, context_object, stf_category, export_fail_severity)):
		return register_exported_resource(json_resource, resource_id)
	else:
		return None

def export_buffer(context: STF_ExportContext, json_resource: dict, buffer: bytes, buffer_id: str | None = None) -> int | None:
	if(buffer_id := context.serialize_buffer(buffer, buffer_id)):
		return register_exported_buffer(json_resource, buffer_id)
	else:
		return None


def get_resource_id(json_resource: dict, resource_index: int) -> str:
	if(type(resource_index) is str): # todo remove this possibility sometime after stf v0.1.x
		return resource_index
	if(resource_index is None or "referenced_resources" not in json_resource or len(json_resource["referenced_resources"]) < resource_index):
		return None
	else:
		return json_resource["referenced_resources"][resource_index]

def get_buffer_id(json_resource: dict, buffer_index: int) -> str:
	if(type(buffer_index) is str): # todo remove this possibility sometime after stf v0.1.x
		return buffer_index
	if(buffer_index is None or "referenced_buffers" not in json_resource or len(json_resource["referenced_buffers"]) < buffer_index):
		return None
	else:
		return json_resource["referenced_buffers"][buffer_index]

def import_resource(context: STF_ImportContext, json_resource: dict, resource_index: int, context_object: Any = None, stf_category: str = STF_Category.DATA) -> Any:
	if(type(resource_index) is str): # todo remove this possibility sometime after stf v0.1.x
		return context.import_resource(resource_index, context_object, stf_category)
	if(resource_index is None or "referenced_resources" not in json_resource or len(json_resource["referenced_resources"]) < resource_index):
		return None
	else:
		return context.import_resource(json_resource["referenced_resources"][resource_index], context_object, stf_category)

def import_buffer(context: STF_ImportContext, json_resource: dict, buffer_index: int) -> bytes | None:
	if(type(buffer_index) is str): # todo remove this possibility sometime after stf v0.1.x
		return context.import_buffer(buffer_index)
	if(buffer_index is None or "referenced_buffers" not in json_resource or len(json_resource["referenced_buffers"]) < buffer_index):
		return None
	else:
		return context.import_buffer(json_resource["referenced_buffers"][buffer_index])

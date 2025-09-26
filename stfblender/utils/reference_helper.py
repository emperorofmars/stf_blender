from ..importer.stf_import_context import STF_ImportContext


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


def get_resource_id(json_resource: dict, resource_index: int) -> str:
	if("referenced_resources" not in json_resource or len(json_resource["referenced_resources"]) < resource_index):
		return None
	else:
		return json_resource["referenced_resources"][resource_index]

def get_buffer_id(json_resource: dict, buffer_index: int) -> str:
	if("referenced_buffers" not in json_resource or len(json_resource["referenced_buffers"]) < buffer_index):
		return None
	else:
		return json_resource["referenced_buffers"][buffer_index]

def import_resource(context: STF_ImportContext, json_resource: dict, resource_index: int, expected_kind: str = "data") -> any:
	if("referenced_resources" not in json_resource or len(json_resource["referenced_resources"]) < resource_index):
		return None
	else:
		return context.import_resource(json_resource["referenced_resources"][resource_index], expected_kind)

def import_buffer(context: STF_ImportContext, json_resource: dict, resource_index: int) -> any:
	if("referenced_buffers" not in json_resource or len(json_resource["referenced_buffers"]) < resource_index):
		return None
	else:
		return context.import_buffer(json_resource["referenced_buffers"][resource_index])

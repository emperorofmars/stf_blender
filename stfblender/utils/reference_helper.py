
def export_resource(json_resource: dict, resource_id: str) -> str:
	if("referenced_resources" not in json_resource):
		json_resource["referenced_resources"] = [resource_id]
	else:
		json_resource["referenced_resources"].append(resource_id)
	return resource_id

def export_buffer(json_resource: dict, buffer_id: str) -> str:
	if("referenced_buffers" not in json_resource):
		json_resource["referenced_buffers"] = [buffer_id]
	else:
		json_resource["referenced_buffers"].append(buffer_id)
	return buffer_id



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

def get_resource_id(json_resource: dict, resource_index: int) -> str:
	if(type(resource_index) is str): # todo remove this possibility sometime after stf v0.1.x
		return resource_index
	if(resource_index is None or "referenced_resources" not in json_resource or len(json_resource["referenced_resources"]) < resource_index):
		return None
	else:
		return json_resource["referenced_resources"][resource_index]

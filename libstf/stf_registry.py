
class STF_Profile:
	pass


class STF_TypeDefinition:
	def validate(type_instance: any, profiles: list[STF_Profile] = None) -> bool: False
	def to_json(type_instance: any, profiles: list[STF_Profile] = None) -> dict: None
	def from_Json(json: dict, profiles: list[STF_Profile] = None) -> any: None

class STF_Registry:
	registered_resource_types: dict[str, STF_TypeDefinition]
	registered_profiles: dict[str, STF_Profile]


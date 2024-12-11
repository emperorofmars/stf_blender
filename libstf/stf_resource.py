from .stf_registry import STF_Profile


class STF_Resource:
	type: str
	name: str
	degraded: bool
	def validate(type_instance: any, profiles: list[STF_Profile] = None) -> bool: False

class STF_Component_Resource(STF_Resource):
	overrides: list[str]

class STF_Node_Resource(STF_Resource):
	children: list[str]
	components: dict[STF_Component_Resource]

class STF_SceneHierarchy_Resource(STF_Resource):
	root: str
	nodes: dict[str, STF_Node_Resource]
	referenced_resources: list[str]

class STF_Data_Resource(STF_Resource):
	fallback: str
	components: list[STF_Component_Resource]
	referenced_buffers: list[str]

class STF_Modification(STF_Resource):
	fallback: str
	components: list[STF_Component_Resource]

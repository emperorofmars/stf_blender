
class STF_Profile:
	pass


class STF_ImportContext:
	profiles: list[STF_Profile]
	def add_import_warning(self, warning: str): pass
	def add_import_error(self, error: str): pass


class STF_ImportContext_Top(STF_ImportContext):
	profiles: list[STF_Profile]
	def get_resource_by_index(self, index: int) -> dict: pass
	def get_buffer_by_index(self, index: int) -> bytearray: pass


class STF_ImportContext_Data(STF_ImportContext):
	profiles: list[STF_Profile]
	def get_resource_by_index(self, index: int) -> dict: pass
	def get_buffer_by_index(self, index: int) -> bytearray: pass


class STF_ImportContext_Prefab(STF_ImportContext):
	profiles: list[STF_Profile]
	def get_resource_by_index(self, index: int) -> dict: pass
	def get_hierarchy_node(self, node_id: str) -> dict: pass


class STF_TypeProcessor:
	type: str
	import_context: STF_ImportContext

	#validate: function[STF_ImportContext_Top, dict]
	#process: function[STF_ImportContext_Top, dict]


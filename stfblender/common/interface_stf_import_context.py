import bpy
from typing import Any, Callable

from . import STF_Category
from .stf_task_steps import STF_TaskSteps
from .stf_report import STFReport
from .property_path_part import BlenderPropertyPathPart


class STF_ImportContext:
	"""Interface Context for resource import. It will be passed to each STF_Handlers's import func."""

	def get_json_resource(self, stf_id: str) -> dict | None:
		pass

	def get_imported_resource(self, stf_id: str):
		pass

	def register_imported_resource(self, stf_id: str, application_object: Any):
		pass

	def import_resource(self, json_parent: dict, resource_index: int, context_object: Any = None, stf_category: str = STF_Category.DATA) -> Any:
		"""Import a STF resource to a Blender 'thing'. The resources ID will be retrieved from the json_parent's 'referenced_resources' array, based on the 'resource_index' argument. Returns the imported Blender 'thing'."""
		pass

	def _import_resource(self, stf_id: str, context_object: Any = None, stf_category: str = STF_Category.DATA) -> Any | None:
		"""Import a STF resource to a Blender 'thing'. Returns the imported Blender 'thing'."""
		pass

	def import_buffer(self, json_parent: dict, buffer_index: int) -> bytes | None:
		"""Import a STF buffer to 'bytes'. The buffer ID will be retrieved from the json_parent's 'referenced_buffers' array, based on the 'buffer_index' argument. Returns the imported 'bytes'."""
		pass

	def _import_buffer(self, stf_id: str) -> bytes | None:
		"""Import a STF buffer to 'bytes'. Returns the imported 'bytes'."""
		pass

	def resolve_stf_property_path(self, stf_path: list[str], application_object: Any = None) -> BlenderPropertyPathPart | None:
		pass

	def add_task(self, step: int | STF_TaskSteps, task: Callable):
		"""Will be executed after all other resources have been exported."""
		pass

	def add_cleanup_task(self, task: Callable):
		pass

	def register_trash_object(self, trash: bpy.types.Object):
		pass

	def get_root_id(self) -> str:
		pass

	def set_root_collection(self, root_collection: bpy.types.Collection):
		pass

	def get_root_collection(self) -> bpy.types.Collection:
		pass

	def get_setting(self, key: str, default: Any = None) -> Any:
		pass

	def get_filename(self) -> str:
		pass

	def report(self, report: STFReport):
		pass

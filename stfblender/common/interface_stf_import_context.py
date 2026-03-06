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

	def import_resource(self, stf_id: str, context_object: Any = None, stf_category: str = STF_Category.DATA) -> Any:
		pass

	def import_buffer(self, stf_id: str) -> bytes | None:
		pass

	def resolve_stf_property_path(self, stf_path: list[str], application_object: Any = None) -> BlenderPropertyPathPart:
		pass

	def add_task(self, step: int | STF_TaskSteps, task: Callable):
		"""Will be executed after all other resources have been exported"""
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

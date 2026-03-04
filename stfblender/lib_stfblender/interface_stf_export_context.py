import bpy
from typing import Any, Callable

from .stf_task_steps import STF_TaskSteps
from .stf_json_definition import STF_Meta_AssetInfo
from .stf_report import STFReportSeverity, STFReport
from .property_path_part import STFPropertyPathPart


class STF_ExportContext:
	"""Interface Context for resource export. It will be passed to each STF_Module's export func."""

	def get_resource_id(self, application_object: Any) -> str | None:
		pass

	def register_id(self, application_object: Any, stf_id: str):
		pass

	def serialize_resource(self, application_object: Any, context_object: Any = None, module_kind = None, export_fail_severity: STFReportSeverity = STFReportSeverity.Error) -> str | None:
		pass

	def serialize_buffer(self, data: bytes, buffer_id: str = None) -> str:
		pass

	def resolve_application_property_path(self, application_object: Any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
		pass

	def add_task(self, step: int | STF_TaskSteps, task: Callable):
		"""Will be executed after all other resources have been exported"""
		pass

	def add_cleanup_task(self, task: Callable):
		pass

	def register_trash_object(self, trash: bpy.types.Object):
		pass

	def get_root(self) -> bpy.types.Collection:
		pass

	def report(self, report: STFReport):
		pass

	def id_exists(self, stf_id: str) -> bool:
		pass

	def get_setting(self, key: str, default: Any = None) -> Any:
		pass

	def get_root_id(self) -> str | None:
		pass

	def get_asset_info(self) -> STF_Meta_AssetInfo:
		pass

import bpy
from typing import Any, Callable, Protocol
from abc import abstractmethod

from .stf_task_steps import STF_TaskSteps
from .base.stf_json_definition import STF_Meta_AssetInfo
from .stf_report import STFReportSeverity, STFReport
from .property_path_part import STFPropertyPathPart


class STF_ExportContext(Protocol):
	"""Interface Context for resource export. It will be passed to each STF_Handler's export func."""

	@abstractmethod
	def get_resource_id(self, application_object: Any) -> str | None:
		pass

	@abstractmethod
	def register_id(self, application_object: Any, stf_id: str):
		pass

	@abstractmethod
	def serialize_resource(self, json_parent: dict, application_object: Any, context_object: Any = None, stf_category: str | None = None, export_fail_severity: STFReportSeverity = STFReportSeverity.Error) -> int | None:
		"""
		Export a Blender 'thing' to a STF resource. The exported resources ID will be written into the json_parent's `referenced_resources` array.
		Returns the index of the ID in the `referenced_resources` array.
		"""

	@abstractmethod
	def _serialize_resource(self, application_object: Any, context_object: Any = None, stf_category: str | None = None, export_fail_severity: STFReportSeverity = STFReportSeverity.Error) -> str | None:
		"""Export a Blender 'thing' to a STF resource. Returns the exported resources ID."""

	@abstractmethod
	def serialize_buffer(self, json_parent: dict, data: bytes, buffer_id: str | None = None) -> int:
		"""Export `bytes` to a STF buffer. The exported buffers ID will be written into the json_parent's `referenced_buffers` array. Returns the index of the ID in the `referenced_buffers` array."""

	@abstractmethod
	def _serialize_buffer(self, data: bytes, buffer_id: str | None = None) -> str:
		"""Export `bytes` to a STF buffer. Returns the exported buffers ID."""

	@abstractmethod
	def resolve_application_property_path(self, application_object: Any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart | None:
		pass

	@abstractmethod
	def add_task(self, step: int | STF_TaskSteps, task: Callable):
		"""Will be executed after all other resources have been exported."""

	@abstractmethod
	def add_cleanup_task(self, task: Callable):
		"""Add a task which will be executed after the exported concluded."""

	@abstractmethod
	def register_trash_object(self, trash: bpy.types.Object):
		"""Register a Blender Object for deletion after the export concluded"""

	@abstractmethod
	def get_root(self) -> bpy.types.Collection:
		pass

	@abstractmethod
	def report(self, report: STFReport):
		pass

	@abstractmethod
	def id_exists(self, stf_id: str) -> bool:
		pass

	@abstractmethod
	def get_setting(self, key: str, default: Any = None) -> Any:
		pass

	@abstractmethod
	def get_root_id(self) -> str | None:
		pass

	@abstractmethod
	def get_asset_info(self) -> STF_Meta_AssetInfo:
		pass

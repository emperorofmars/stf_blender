import bpy
import logging
from typing import Any

from .import_settings import STF_ImportSettings

from ..common import STFReportSeverity, STFReport, STF_Category
from ..common.resource import STF_HandlerBase
from ..common.base.stf_file import STF_File
from ..common.resource.blender_native.stf_handler_blender_native import STF_Handler_BlenderNative
from ..common.base.stf_json_definition import STF_Meta_AssetInfo
from ..common.base.stf_state_base import STF_State_Base


_logger = logging.getLogger(__name__)


class STF_ImportState(STF_State_Base):
	"""
	Hold all the data from a file for an import run.
	Gets passed to the STF_ImportContext.
	"""

	def __init__(self, file: STF_File, handlers: dict[str, STF_HandlerBase], fallback_handlers: dict[str, STF_HandlerBase] = {}, trash_objects: list[bpy.types.Object] = [], fail_on_severity: STFReportSeverity = STFReportSeverity.FatalError, settings: STF_ImportSettings = {}):
		super().__init__(fail_on_severity)

		self._file: STF_File = file

		self._modules: dict[str, STF_HandlerBase] = handlers
		self._fallback_modules: dict[str, STF_HandlerBase] = fallback_handlers

		self._imported_resources: dict[str, Any] = {} # ID | list of IDs -> imported object
		self._asset_info: STF_Meta_AssetInfo

		self._trash_objects: list[bpy.types.Object] = trash_objects

		self._settings: STF_ImportSettings = settings


	def determine_handler(self, json_resource: dict[str, Any], stf_category: str = STF_Category.DATA) -> STF_HandlerBase | None:
		return self._modules.get(json_resource["type"], self._fallback_modules.get(stf_category))

	def register_imported_resource(self, stf_id: str, application_object: Any):
		self._imported_resources[stf_id] = application_object

	def get_imported_resource(self, stf_id: str):
		return self._imported_resources.get(stf_id, None)

	def import_buffer(self, stf_id: str) -> bytes | None:
		if(buffer := self._file.definition.buffers.get(stf_id)):
			match(buffer.type):
				case "stf.buffer.included":
					return self._file.buffers_included[buffer.index]
				case _:
					_logger.fatal("Invalid buffer type: " + buffer.type, stack_info=True)
					self.report(STFReport("Invalid buffer type: " + buffer.type, severity=STFReportSeverity.FatalError))
		return None


	def determine_property_resolution_handler(self, stf_id: str) -> STF_HandlerBase | None:
		if(json_resource := self.get_json_resource(stf_id)):
			handler = self.determine_handler(json_resource)
			if(hasattr(handler, "resolve_stf_property_to_blender_func")):
				return handler
		return None


	def get_json_resource(self, stf_id: str) -> dict[str, Any]:
		return self._file.definition.resources.get(stf_id)

	def get_root_id(self) -> str:
		return self._file.definition.stf.root

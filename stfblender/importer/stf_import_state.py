import bpy
import logging

from .import_settings import STF_ImportSettings

from ..base.stf_report import STFReportSeverity, STFReport
from ..base.stf_file import STF_File
from ..base.stf_module import STF_Module
from ..base.stf_definition import STF_Meta_AssetInfo
from ..base.stf_state_base import STF_State_Base


_logger = logging.getLogger(__name__)


class STF_ImportState(STF_State_Base):
	"""
	Hold all the data from a file for an import run.
	Gets passed to the STF_ImportContext.
	"""

	def __init__(self, file: STF_File, modules: dict[str, STF_Module], fallback_modules: dict[str, STF_Module] = {}, trash_objects: list[bpy.types.Object] = [], fail_on_severity: STFReportSeverity = STFReportSeverity.FatalError, settings: STF_ImportSettings = {}):
		super().__init__(fail_on_severity)

		self._file = file

		self._modules: dict[str, STF_Module] = modules
		self._fallback_modules: dict[str, STF_Module] = fallback_modules

		self._imported_resources: dict[str, any] = {} # ID | list of IDs -> imported object
		self._asset_info: STF_Meta_AssetInfo

		self._trash_objects: list[bpy.types.Object] = trash_objects

		self._settings = settings


	def determine_module(self, json_resource: dict, stf_kind: str = None) -> STF_Module:
		return self._modules.get(json_resource["type"], self._fallback_modules.get(stf_kind))

	def register_imported_resource(self, stf_id: str, application_object: any):
		self._imported_resources[stf_id] = application_object

	def get_imported_resource(self, stf_id: str):
		return self._imported_resources.get(stf_id, None)

	def import_buffer(self, stf_id: str) -> bytes:
		buffer = self._file.definition.buffers.get(stf_id)
		match(buffer.type):
			case "stf.buffer.included":
				return self._file.buffers_included[buffer.index]
			case _:
				_logger.fatal("Invalid buffer type: " + buffer.type, stack_info=True)
				self.report(STFReport("Invalid buffer type: " + buffer.type, severity=STFReportSeverity.FatalError))
		return None


	def determine_property_resolution_module(self, stf_id: str) -> STF_Module:
		if(json_resource := self.get_json_resource(stf_id)):
			module = self.determine_module(json_resource)
			if(hasattr(module, "resolve_stf_property_to_blender_func")):
				return module
		return None


	def get_json_resource(self, stf_id: str) -> dict:
		return self._file.definition.resources.get(stf_id)

	def get_root_id(self) -> str:
		return self._file.definition.stf.root


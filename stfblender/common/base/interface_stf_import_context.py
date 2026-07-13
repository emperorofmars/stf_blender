import bpy
from typing import Any, Callable, Protocol
from abc import abstractmethod

from .stf_category import STF_Category
from .stf_task_steps import STF_TaskSteps
from .stf_report import STFReport
from .property_path_part import BlenderPropertyPathPart


class STF_ImportContext(Protocol):
	"""Interface Context for resource import. It will be passed to each STF_Handlers's import func"""

	@abstractmethod
	def get_json_resource(self, stf_id: str) -> dict | None:
		"""Get an STF JSON resource by ID"""

	@abstractmethod
	def get_imported_resource(self, stf_id: str) -> Any | None:
		"""If an STF resource has already been imported, it can be retrieved"""

	@abstractmethod
	def register_imported_resource(self, stf_id: str, application_object: Any) -> None:
		"""
		Once a resource has been successfully imported, the handler has to registered it here.

		:param str stf_id: ID of the imported STF resource
		:param Any application_object: The imported Blender object
		"""

	@abstractmethod
	def import_resource(self, json_parent: dict, resource_index: int, context_object: Any = None, stf_category: str = STF_Category.DATA) -> Any | None:
		"""
		Import a STF resource to a Blender 'thing'. The resources ID will be retrieved from the json_parent's `referenced_resources` array, based on the `resource_index` argument. Returns the imported Blender 'thing'.

		:param dict json_parent: The JSON resource-dict of the resource from which the resource-id will be retrieved
		:param int resource_index: Index of the resource-id in the `referenced_resources` array on the `json_parent`
		:param Any context_object: Blender object that will be passed to the to be imported resources handler. E.g. the Collection for a `stf.node` or the Armature for a `stf.bone`.
		:param str | STF_Category stf_category: The resources category, by default `STF_Category.DATA`.
		:return Any | None: The imported Blender object or `None` in case of failure
		"""

	def _import_resource(self, stf_id: str, context_object: Any = None, stf_category: str = STF_Category.DATA) -> Any | None:
		"""
		Under normal circumstances use the method without the underscore.

		Import a STF resource to a Blender 'thing'. Returns the imported Blender 'thing'.
		"""

	@abstractmethod
	def import_buffer(self, json_parent: dict, buffer_index: int) -> bytes | None:
		"""
		Import a STF buffer to `bytes`.
		The buffer ID will be retrieved from the json_parent's `referenced_buffers` array, based on the `buffer_index` argument.

		:param dict json_parent: The JSON resource-dict of the resource from which the buffers-id will be retrieved
		:param int buffer_index: Index of the buffer-id in the `referenced_buffers` array on the `json_parent`
		:return bytes: Returns the imported `bytes`
		"""

	@abstractmethod
	def _import_buffer(self, stf_id: str) -> bytes | None:
		"""
		Under normal circumstances use the method without the underscore.

		Import a STF buffer to `bytes`. Returns the imported `bytes`.
		"""

	@abstractmethod
	def resolve_stf_property_path(self, stf_path: list[str], blender_object: Any = None) -> BlenderPropertyPathPart | None:
		"""
		Convert a STF animation property-path into Blender.

		:param list[str] stf_path: The STF animation property path.
		:param Any blender_object: Resolve the path relative to this Blender object.
		"""

	@abstractmethod
	def add_task(self, step: int | STF_TaskSteps, task: Callable):
		"""Will be executed after all other resources have been imported."""

	@abstractmethod
	def add_cleanup_task(self, task: Callable):
		"""Will be executed once the import has concluded. Use it for complex cleanup operations."""

	@abstractmethod
	def register_trash_object(self, trash: bpy.types.Object):
		"""Will be executed once the import has concluded. Use it to delete trash objects that were temporarily needed."""

	@abstractmethod
	def get_root_id(self) -> str:
		pass

	@abstractmethod
	def set_root_collection(self, root_collection: bpy.types.Collection):
		pass

	@abstractmethod
	def get_root_collection(self) -> bpy.types.Collection:
		pass

	@abstractmethod
	def get_setting(self, key: str, default: Any = None) -> Any:
		pass

	@abstractmethod
	def get_filename(self) -> str:
		pass

	@abstractmethod
	def report(self, report: STFReport):
		pass

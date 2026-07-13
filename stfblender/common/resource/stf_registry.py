"""
Retrieve STF-handlers from Blender addons
"""

import bpy
from typing import Any

from .. import STF_Category
from .stf_handler_base import STF_HandlerBase
from .component import STF_Handler_Component, STF_ExportComponentHook
from .data import STF_Handler_Data

__all__ = ["get_stf_handlers", "get_import_handlers", "get_import_handlers_fallback", "get_export_handlers", "find_export_handler", "get_all_component_handlers", "get_blender_native_component_handlers", "get_data_component_handlers", "get_blender_non_native_data_handlers", "get_fallback_handler", "find_component_handler", "find_data_handler"]


def get_stf_handlers() -> list[STF_HandlerBase]:
	"""
	Scan all Blender addon modules for STF handlers.

	:returns list[STF_HandlerBase]: All handlers, may have redundant entries
	"""
	stf_handlers = []
	import sys
	for blender_addon in bpy.context.preferences.addons.keys(): # type: ignore
		try:
			python_module = sys.modules[blender_addon]
			if(stf_handler_list := getattr(python_module, "register_stf_handlers", None)):
				if(isinstance(stf_handler_list, list)):
					for stf_handler in stf_handler_list:
						if(stf_handler and hasattr(stf_handler, "stf_type")):
							stf_handlers.append(stf_handler)
		except Exception:
			continue
	return stf_handlers


def _is_priority_higher(a: STF_HandlerBase, b: STF_HandlerBase) -> bool:
	"""Check which handler is preferable"""
	if(not hasattr(a, "priority")):
		return True
	if(not hasattr(b, "priority")):
		return False
	return a.priority <= b.priority


def get_import_handlers() -> dict[str, STF_HandlerBase]:
	"""
	Scan all Blender addon modules for STF handlers usable for import.

	:returns dict[str, STF_HandlerBase]: For each supported STF resource type, the preferred handler for import
	"""
	stf_handlers = get_stf_handlers()
	ret_handlers = {}
	for stf_handler in stf_handlers:
		if(hasattr(stf_handler, "stf_type") and hasattr(stf_handler, "import_func")):
			if(not ret_handlers.get(stf_handler.stf_type) or _is_priority_higher(ret_handlers[stf_handler.stf_type], stf_handler)):
				ret_handlers[stf_handler.stf_type] = stf_handler
	return ret_handlers


def get_import_handlers_fallback() -> dict[str, STF_HandlerBase]:
	"""
	Get Fallback handlers per resource category (data, node, component).

	:returns dict[STF_Category, STF_HandlerBase]: For each supported STF resource category, the fallback handler import
	"""
	stf_handlers = get_stf_handlers()
	ret_handlers = {}
	for stf_handler in stf_handlers:
		if(hasattr(stf_handler, "stf_type") and not getattr(stf_handler, "stf_type") and hasattr(stf_handler, "import_func")):
			if(not ret_handlers.get(stf_handler.stf_category) or _is_priority_higher(ret_handlers[stf_handler.stf_category], stf_handler)):
				ret_handlers[stf_handler.stf_category] = stf_handler
	return ret_handlers


def get_export_handlers() -> tuple[dict[Any, list[STF_HandlerBase]], dict[Any, list[STF_ExportComponentHook]]]:
	"""
	Scan all Blender addon modules for STF handlers usable for export.

	:returns tuple[dict[Any, list[STF_HandlerBase]], dict[Any, list[STF_ExportComponentHook]]]:\
	First `dict` contains all handlers for Blender types (`bpy.types.Object`, `bpy.types.Material`, ...).
	Second `dict` contains all export-hooks for Blender types.
	"""
	stf_handlers = get_stf_handlers()

	ret_handlers = {}
	ret_hooks = {}

	for stf_handler in stf_handlers:
		if(hasattr(stf_handler, "understood_application_types") and hasattr(stf_handler, "export_func")):
			for understood_type in stf_handler.understood_application_types:
				if(not ret_handlers.get(understood_type)):
					ret_handlers[understood_type] = [stf_handler]
				else:
					ret_handlers[understood_type].append(stf_handler)

		if(hasattr(stf_handler, "hook_target_application_types") and hasattr(stf_handler, "hook_apply_func") and hasattr(stf_handler, "hook_can_handle_application_object_func")):
			stf_hook: STF_ExportComponentHook = stf_handler # type: ignore
			for understood_type in stf_hook.hook_target_application_types:
				if(not ret_hooks.get(understood_type)):
					ret_hooks[understood_type] = [stf_hook]
				else:
					ret_hooks[understood_type].append(stf_hook)

	return (ret_handlers, ret_hooks)


def find_export_handler(blender_resource: Any) -> STF_HandlerBase | None:
	"""
	Find a handler from the provided list of handlers for the type, or a fallback.

	:param Any blender_resource: the Blender-type to find a handler for
	:returns STF_HandlerBase | None: The resources handler with the highest priority if found
	"""
	stf_handlers = get_stf_handlers()
	ret: STF_HandlerBase | None = None
	ret_prio: int = -1
	for stf_handler in stf_handlers:
		if(hasattr(stf_handler, "understood_application_types") and hasattr(stf_handler, "export_func")):
			if(type(blender_resource) in stf_handler.understood_application_types):
				if(ret is None):
					ret = stf_handler
					ret_prio = stf_handler.can_handle_application_object_func(blender_resource) if hasattr(stf_handler, "can_handle_application_object_func") else stf_handler.priority
					continue
				handler_prio = stf_handler.can_handle_application_object_func(blender_resource) if hasattr(stf_handler, "can_handle_application_object_func") else stf_handler.priority
				if(handler_prio > ret_prio):
					ret = stf_handler
					ret_prio = handler_prio
	return ret


def get_all_component_handlers() -> list[STF_Handler_Component]:
	"""
	Scan all Blender addon modules for STF handlers for component-resources.

	:returns list[STF_Handler_Component]: All handlers for component-resources, may have redundant entries
	"""
	ret = []
	for stf_handler in get_stf_handlers():
		if(hasattr(stf_handler, "blender_property_name") and getattr(stf_handler, "stf_category") == "component"):
			ret.append(stf_handler)
	return ret


def get_blender_native_component_handlers(filter: Any = None) -> list[STF_Handler_Component]:
	"""
	Scan all Blender addon modules for STF handlers for component-resources, that can be added to Blender-native objects (`bpy.types.Object`, `bpy.types.Material`, ...).

	:param Any filter: Type for which to check the handlers `filter` list against.
	:returns list[STF_Handler_Component]: All handlers for component-resources, may have redundant entries
	"""
	ret = []
	for stf_handler in get_stf_handlers():
		if(hasattr(stf_handler, "stf_type") and getattr(stf_handler, "stf_type") and hasattr(stf_handler, "blender_property_name") and getattr(stf_handler, "stf_category") == "component"):
			if(hasattr(stf_handler, "filter_all_data_modules") and getattr(stf_handler, "filter_all_data_modules")):
				continue # Ignore, this component can only exist on non-Blender-native data resources
			elif(hasattr(stf_handler, "filter") and getattr(stf_handler, "filter") and filter):
				if(filter in getattr(stf_handler, "filter")):
					ret.append(stf_handler)
				else:
					continue
			else:
				ret.append(stf_handler)
	return ret


def get_data_component_handlers(filter = None) -> list[STF_Handler_Component]:
	"""
	Scan all Blender addon modules for STF handlers for component-resources, that can be added to Blender-NON-native STF-data resources (`stfexp.animation_blendtree`, `dev.vrm.blendshape_pose`, ...).

	:param Any filter: Type for which to check the handlers `filter` list against.
	:returns list[STF_Handler_Component]: All handlers for component-resources, may have redundant entries
	"""
	ret = []
	for stf_handler in get_stf_handlers():
		if(hasattr(stf_handler, "stf_type") and getattr(stf_handler, "stf_type") and hasattr(stf_handler, "blender_property_name") and getattr(stf_handler, "stf_category") == "component"):
			if(hasattr(stf_handler, "filter") and getattr(stf_handler, "filter") and filter):
				if(filter in getattr(stf_handler, "filter")):
					ret.append(stf_handler)
				else:
					continue
			elif(hasattr(stf_handler, "filter_all_data_modules")):
				if(getattr(stf_handler, "filter_all_data_modules")):
					ret.append(stf_handler)
				else:
					continue
			else:
				ret.append(stf_handler)
	return ret

def get_blender_non_native_data_handlers() -> list[STF_Handler_Data]:
	"""
	Scan all Blender addon modules for STF handlers for STF-data resources that are not native to Blender (`stfexp.animation_blendtree`, `dev.vrm.blendshape_pose`, ...).

	:returns list[STF_Handler_Data]: All handlers for data-resources, may have redundant entries
	"""
	ret = []
	for stf_handler in get_stf_handlers():
		if(hasattr(stf_handler, "stf_type") and getattr(stf_handler, "stf_type") and hasattr(stf_handler, "blender_property_name") and getattr(stf_handler, "stf_category") == "data"):
			ret.append(stf_handler)
	return ret


def get_fallback_handler(stf_category: STF_Category | str) -> STF_HandlerBase: # type: ignore
	"""
	Get a fallback handler for a resource category (data, node, component).

	:param STF_Category | str stf_category:
	:returns STF_HandlerBase: For each supported STF resource category, the fallback handler import
	"""
	for stf_handler in get_stf_handlers():
		if(hasattr(stf_handler, "stf_type") and stf_handler.stf_type is None and stf_handler.stf_category == stf_category):
			return stf_handler


def find_component_handler(stf_handlers: list[STF_Handler_Component], stf_type: str) -> STF_Handler_Component:  # type: ignore
	"""
	Find a component-handler from the provided list of handlers for the type, or a fallback.

	:param list[STF_Handler_Component] stf_handlers: List of component-resource handlers to search
	:param str stf_type: the resource-type to find a handler for
	:returns STF_Handler_Component: The resources handler or a fallback handler for component-resources
	"""
	for stf_handler in stf_handlers:
		if(stf_handler.stf_type == stf_type):
			return stf_handler
	if(stf_type == "fallback"):
		return get_fallback_handler(STF_Category.COMPONENT) # type: ignore

def find_data_handler(stf_handlers: list[STF_Handler_Data], stf_type: str) -> STF_Handler_Data:  # type: ignore
	"""
	Find a Blender-NON-native data-handler from the provided list of handlers for the type, or a fallback.

	:param list[STF_Handler_Data] stf_handlers: List of component-resource handlers to search
	:param str stf_type: the resource-type to find a handler for
	:returns STF_Handler_Data: The resources handler or a fallback handler for Blender-NON-native data-resources
	"""
	for stf_handler in stf_handlers:
		if(stf_handler.stf_type == stf_type):
			return stf_handler
	if(stf_type == "fallback"):
		return get_fallback_handler("data") # type: ignore

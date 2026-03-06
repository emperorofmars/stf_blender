import bpy

from typing import Any

from ...common.stf_category import STF_Category
from ..resource.stf_handler_base import STF_HandlerBase
from ..resource.component.stf_handler_component import STF_Handler_Component, STF_ExportComponentHook
from ..resource.data.stf_handler_data import STF_Handler_Data

"""
Util to retrieve all existing STF-handlers
"""

def get_stf_handlers() -> list[STF_HandlerBase]:
	stf_handlers = []
	import sys
	for blender_addon in bpy.context.preferences.addons.keys(): # type: ignore
		try:
			python_module = sys.modules[blender_addon]
			if(stf_handler_list := getattr(python_module, "register_stf_handlers", None)):
				if(isinstance(stf_handler_list, list)):
					for stf_handler in stf_handler_list:
						stf_handlers.append(stf_handler)
		except Exception:
			continue
	return stf_handlers


def is_priority_higher(a: STF_HandlerBase, b: STF_HandlerBase) -> bool:
	if(not hasattr(a, "priority")):
		return True
	if(not hasattr(b, "priority")):
		return False
	return a.priority <= b.priority


def get_import_handlers() -> dict[str, STF_HandlerBase]:
	stf_handlers = get_stf_handlers()
	ret_handlers = {}
	for stf_handler in stf_handlers:
		if(hasattr(stf_handler, "stf_type") and hasattr(stf_handler, "import_func")):
			if(not ret_handlers.get(stf_handler.stf_type) or is_priority_higher(ret_handlers[stf_handler.stf_type], stf_handler)):
				ret_handlers[stf_handler.stf_type] = stf_handler
	return ret_handlers


def get_import_handlers_fallback() -> dict[str, STF_HandlerBase]:
	stf_handlers = get_stf_handlers()
	ret_handlers = {}
	for stf_handler in stf_handlers:
		if(hasattr(stf_handler, "stf_type") and not getattr(stf_handler, "stf_type") and hasattr(stf_handler, "import_func")):
			if(not ret_handlers.get(stf_handler.stf_category) or is_priority_higher(ret_handlers[stf_handler.stf_category], stf_handler)):
				ret_handlers[stf_handler.stf_category] = stf_handler
	return ret_handlers


def get_export_handlers() -> tuple[dict[Any, list[STF_HandlerBase]], dict[Any, list[STF_ExportComponentHook]]]:
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


def get_all_component_handlers() -> list[STF_Handler_Component]:
	ret = []
	for stf_handler in get_stf_handlers():
		if(hasattr(stf_handler, "blender_property_name") and getattr(stf_handler, "stf_category") == "component"):
			ret.append(stf_handler)
	return ret


def get_component_handlers(filter = None) -> list[STF_Handler_Component]:
	ret = []
	for stf_handler in get_stf_handlers():
		if(hasattr(stf_handler, "stf_type") and getattr(stf_handler, "stf_type") and hasattr(stf_handler, "blender_property_name") and getattr(stf_handler, "stf_category") == "component"):
			if(hasattr(stf_handler, "filter_all_data_modules") and getattr(stf_handler, "filter_all_data_modules")):
				continue
			elif(hasattr(stf_handler, "filter") and getattr(stf_handler, "filter") and filter):
				if(filter in getattr(stf_handler, "filter")):
					ret.append(stf_handler)
				else:
					continue
			else:
				ret.append(stf_handler)
	return ret


def get_data_component_handlers(filter = None) -> list[STF_Handler_Component]:
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
	ret = []
	for stf_handler in get_stf_handlers():
		if(hasattr(stf_handler, "stf_type") and getattr(stf_handler, "stf_type") and hasattr(stf_handler, "blender_property_name") and getattr(stf_handler, "stf_category") == "data"):
			ret.append(stf_handler)
	return ret


def get_fallback_handler(stf_category: str) -> STF_HandlerBase: # type: ignore
	for stf_handler in get_stf_handlers():
		if(hasattr(stf_handler, "stf_type") and stf_handler.stf_type is None and stf_handler.stf_category == stf_category):
			return stf_handler


def find_component_handler(stf_handlers: list[STF_Handler_Component], stf_type: str) -> STF_Handler_Component:  # type: ignore
	for stf_handler in stf_handlers:
		if(stf_handler.stf_type == stf_type):
			return stf_handler
	if(stf_type == "fallback"):
		return get_fallback_handler(STF_Category.COMPONENT) # type: ignore

def find_data_handler(stf_handlers: list[STF_Handler_Data], stf_type: str) -> STF_Handler_Data:  # type: ignore
	for stf_handler in stf_handlers:
		if(stf_handler.stf_type == stf_type):
			return stf_handler
	if(stf_type == "fallback"):
		return get_fallback_handler("data") # type: ignore

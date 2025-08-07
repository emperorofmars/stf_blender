import bpy
from types import ModuleType

from .stf_module import STF_ExportComponentHook, STF_Module

"""
Util to retrieve all existing STF-modules
"""

def get_stf_modules_from_pymodule(python_module: ModuleType) -> list[str, STF_Module]:
	stf_modules = []
	if(stf_module_list := getattr(python_module, "register_stf_modules", None)):
		if(isinstance(stf_module_list, list)):
			for stf_module in stf_module_list:
				stf_modules.append(stf_module)
	return stf_modules

def get_stf_modules() -> list[STF_Module]:
	stf_modules = []
	import sys
	python_modules = [sys.modules[m] for m in bpy.context.preferences.addons.keys()]
	for python_module in python_modules:
		stf_modules = stf_modules + get_stf_modules_from_pymodule(python_module)
	return stf_modules


def is_priority_higher(a: STF_Module, b: STF_Module) -> bool:
	if(not hasattr(a, "priority")):
		return True
	if(not hasattr(b, "priority")):
		return False
	return a.priority <= b.priority


def get_import_modules() -> dict[str, STF_Module]:
	stf_modules = get_stf_modules()

	ret_modules = {}

	for stf_module in stf_modules:
		if(hasattr(stf_module, "stf_type") and hasattr(stf_module, "import_func")):
			if(not ret_modules.get(stf_module.stf_type) or is_priority_higher(ret_modules[stf_module.stf_type], stf_module)):
				ret_modules[stf_module.stf_type] = stf_module

	return ret_modules


def get_export_modules() -> tuple[dict[any, list[STF_Module]], dict[any, list[STF_ExportComponentHook]]]:
	stf_modules = get_stf_modules()

	ret_modules = {}
	ret_hooks = {}

	for stf_module in stf_modules:
		if(hasattr(stf_module, "understood_application_types") and hasattr(stf_module, "export_func")):
			for understood_type in stf_module.understood_application_types:
				if(not ret_modules.get(understood_type)):
					ret_modules[understood_type] = [stf_module]
				else:
					ret_modules[understood_type].append(stf_module)

		if(hasattr(stf_module, "hook_target_application_types") and hasattr(stf_module, "hook_apply_func") and hasattr(stf_module, "hook_can_handle_application_object_func")):
			for understood_type in stf_module.hook_target_application_types:
				if(not ret_hooks.get(understood_type)):
					ret_hooks[understood_type] = [stf_module]
				else:
					ret_hooks[understood_type].append(stf_module)

	return (ret_modules, ret_hooks)

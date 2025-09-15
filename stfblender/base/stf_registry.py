import bpy

from .stf_module import STF_Module
from .stf_module_component import STF_BlenderComponentModule, STF_ExportComponentHook
from .stf_module_data import STF_BlenderDataModule

"""
Util to retrieve all existing STF-modules
"""

def get_stf_modules() -> list[STF_Module]:
	stf_modules = []
	import sys
	for blender_addon in bpy.context.preferences.addons.keys():
		try:
			python_module = sys.modules[blender_addon]
			if(stf_module_list := getattr(python_module, "register_stf_modules", None)):
				if(isinstance(stf_module_list, list)):
					for stf_module in stf_module_list:
						stf_modules.append(stf_module)
		except Exception:
			continue
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


def get_component_modules(filter = None) -> list[STF_BlenderComponentModule]:
	ret = []
	for stf_module in get_stf_modules():
		if(hasattr(stf_module, "blender_property_name") and getattr(stf_module, "stf_kind") == "component"):
			if(hasattr(stf_module, "filter") and filter):
				if(filter in getattr(stf_module, "filter")):
					ret.append(stf_module)
				else:
					continue
			else:
				ret.append(stf_module)
	return ret

def get_blender_non_native_data_modules() -> list[STF_BlenderDataModule]:
	ret = []
	for stf_module in get_stf_modules():
		if(hasattr(stf_module, "blender_property_name") and getattr(stf_module, "stf_kind") == "data"):
			ret.append(stf_module)
	return ret

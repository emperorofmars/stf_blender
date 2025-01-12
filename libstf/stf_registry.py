import sys
from types import ModuleType
from .stf_module import STF_ExportComponentHook, STF_Module

"""
Utils to retrieve all existing STF processors.
"""

def get_search_modules(search_modules: list[ModuleType | str] | None = None) -> list[ModuleType]:
	ret = []
	if(search_modules):
		for search_module in search_modules:
			if(type(search_module) is ModuleType):
				ret.append(search_module)
			elif(type(search_module) is str):
				if(search_module in sys.modules):
					ret.append(sys.modules[search_module])
			else:
				raise TypeError()
	else:
		for _, module in sys.modules:
			ret.append(module)
	return ret


def get_stf_modules_from_pymodule(module: ModuleType) -> list[str, STF_Module]:
	ret = []
	if(stf_processor_list := getattr(module, "register_stf_modules", None)):
		if(isinstance(stf_processor_list, list)):
			for stf_processor in stf_processor_list:
				ret.append(stf_processor)
	return ret


def get_stf_modules(search_modules: list[ModuleType | str] | None = None) -> list[STF_Module]:
	ret = []
	modules = get_search_modules(search_modules)
	for module in modules:
		ret = ret + get_stf_modules_from_pymodule(module)
	return ret


def is_priority_higher(a: STF_Module, b: STF_Module) -> bool:
	if(not hasattr(a, "priority")):
		return True
	if(not hasattr(b, "priority")):
		return False
	return a.priority <= b.priority



def get_import_modules(search_modules: list[ModuleType | str] | None = None) -> dict[str, STF_Module]:
	stf_modules = get_stf_modules(search_modules)

	ret_modules = {}

	for stf_module in stf_modules:
		if(hasattr(stf_module, "stf_type") and hasattr(stf_module, "import_func")):
			if(not ret_modules.get(stf_module.stf_type) or is_priority_higher(ret_modules[stf_module.stf_type], stf_module)):
				ret_modules[stf_module.stf_type] = stf_module

	return ret_modules


def get_export_modules(search_modules: list[ModuleType | str] | None = None) -> tuple[dict[any, list[STF_Module]], dict[any, list[STF_ExportComponentHook]]]:
	stf_modules = get_stf_modules(search_modules)

	tmp_registered_modules = {}
	tmp_registered_hooks = {}

	ret_modules = {}
	ret_hooks = {}

	for stf_module in stf_modules:
		if(hasattr(stf_module, "understood_application_types") and hasattr(stf_module, "export_func")):
			"""if(not hasattr(stf_module, "hook_target_application_types")):
				for understood_type in stf_module.understood_application_types:
					if(not ret_modules.get(understood_type) or is_priority_higher(ret_modules[understood_type], stf_module)):
						ret_modules[understood_type] = stf_module"""
			if(not hasattr(stf_module, "hook_target_application_types")):
				for understood_type in stf_module.understood_application_types:
					if(not tmp_registered_modules.get(understood_type) or is_priority_higher(tmp_registered_modules[understood_type], stf_module)):
						tmp_registered_modules[understood_type] = stf_module

						if(not ret_modules.get(understood_type)):
							ret_modules[understood_type] = [stf_module]
						else:
							ret_modules[understood_type].append(stf_module)
			else:
				for understood_type in stf_module.understood_application_types:
					if(not tmp_registered_hooks.get(understood_type) or is_priority_higher(tmp_registered_hooks[understood_type], stf_module)):
						tmp_registered_hooks[understood_type] = stf_module

						if(not ret_hooks.get(understood_type)):
							ret_hooks[understood_type] = [stf_module]
						else:
							ret_hooks[understood_type].append(stf_module)

	return (ret_modules, ret_hooks)

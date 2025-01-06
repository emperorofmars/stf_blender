import sys
from types import ModuleType
from .stf_module import STF_Module

"""
Utils to retrieve all existing STF processors.
"""

def get_stf_modules_from_pymodule(module: ModuleType) -> dict[str, STF_Module]:
	ret = {}
	if(stf_processor_list := getattr(module, "register_stf_modules", None)):
		if(isinstance(stf_processor_list, list)):
			for stf_processor in stf_processor_list:
				ret[stf_processor.stf_type] = stf_processor
	return ret


def _merge_entries(base: dict[str, STF_Module], merge: dict[str, STF_Module]) -> dict[str, STF_Module]:
	return base | merge # TODO actually compare priority


def get_stf_modules(modules: list[ModuleType]) -> list[STF_Module]:
	ret = {}
	for module in modules:
		ret = _merge_entries(ret, get_stf_modules_from_pymodule(module))
	return list(ret.values())


def get_stf_modules(modules: list[str]) -> list[STF_Module]:
	ret = {}
	for module_str in modules:
		if(module_str in sys.modules):
			ret = _merge_entries(ret, get_stf_modules_from_pymodule(sys.modules[module_str]))
	return list(ret.values())


def get_all_stf_modules() -> list[STF_Module]:
	ret = {}
	for _, module in sys.modules.items():
		ret = _merge_entries(ret, get_stf_modules_from_pymodule(module))
	return list(ret.values())

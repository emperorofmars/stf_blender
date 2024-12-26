import sys
from types import ModuleType
from .stf_processor import STF_Processor


def get_stf_processors_from_module(module: ModuleType) -> dict[str, STF_Processor]:
	ret = {}
	if(stf_processor_list := getattr(module, "register_stf_processors", None)):
		if(isinstance(stf_processor_list, list)):
			for stf_processor in stf_processor_list:
				ret[stf_processor.stf_type] = stf_processor
	return ret


def _merge_entries(base: dict[str, STF_Processor], merge: dict[str, STF_Processor]) -> dict[str, STF_Processor]:
	return base | merge


def get_stf_processors(modules: list[ModuleType]) -> list[STF_Processor]:
	ret = {}
	for module in modules:
		ret = _merge_entries(ret, get_stf_processors_from_module(module))
	return list(ret.values())


def get_stf_processors(modules: list[str]) -> list[STF_Processor]:
	ret = {}
	for module_str in modules:
		if(module_str in sys.modules):
			ret = _merge_entries(ret, get_stf_processors_from_module(sys.modules[module_str]))
	return list(ret.values())


def get_all_stf_processors() -> list[STF_Processor]:
	ret = {}
	for _, module in sys.modules.items():
		ret = _merge_entries(ret, get_stf_processors_from_module(module))
	return list(ret.values())

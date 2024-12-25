import sys
from types import ModuleType
from .stf_processor import STF_Processor


def get_stf_processors_from_module(module: ModuleType) -> dict[str, STF_Processor]:
	ret = {}
	if(stf_processor_list := getattr(module, "register_stf_processors", None)):
		if(isinstance(stf_processor_list, list)):
			for stf_processor in stf_processor_list:
				ret[stf_processor.stf_type] = stf_processor
		else:
			print("FOOO")
	return ret


def get_stf_processors(modules: list[ModuleType]) -> dict[str, STF_Processor]:
	ret = {}
	for module in modules:
		ret = ret | get_stf_processors_from_module(module)
	return ret


def get_stf_processors(modules: list[str]) -> dict[str, STF_Processor]:
	ret = {}
	for module_str in modules:
		if(module_str in sys.modules):
			ret = ret | get_stf_processors_from_module(sys.modules[module_str])
	return ret


def get_all_stf_processors() -> dict[str, STF_Processor]:
	ret = {}
	for _, module in sys.modules.items():
		ret = ret | get_stf_processors_from_module(module)
	return ret

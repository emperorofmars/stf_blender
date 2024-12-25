from typing import Callable


class STF_Processor:
	stf_type: str
	stf_kind: str
	understood_types: list = []
	import_func: Callable[[any, dict, str], any]
	export_func: Callable[[any, any], tuple[dict, str]]


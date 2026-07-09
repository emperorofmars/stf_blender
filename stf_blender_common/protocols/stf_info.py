from typing import Protocol

from ..protocols import PSTF_Component_Ref


class PSTF_Info(Protocol):
	"""Basic STF properties"""
	stf_id: str
	stf_name: str
	stf_name_source_of_truth: bool
	stf_components: list[PSTF_Component_Ref]
	stf_active_component_index: int

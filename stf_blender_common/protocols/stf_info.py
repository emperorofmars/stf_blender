import bpy

from typing import Protocol
from collections.abc import Callable

from ..protocols import PSTF_Component_Ref


class PSTF_Info(Protocol):
	"""Basic STF properties"""
	stf_id: str
	stf_name: str
	stf_name_source_of_truth: bool
	stf_components: list[PSTF_Component_Ref]
	stf_active_component_index: int

	id_data: bpy.types.ID | None
	rna_ancestors: Callable[[], list[bpy.types.bpy_struct]]

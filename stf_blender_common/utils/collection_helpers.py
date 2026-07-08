import bpy
from typing import Callable

from ..operators import OP_Edit_Component_Collection
from ..protocols import PSTF_DataResourceBase, PSTF_ComponentResourceBase


def create_add_button(layout: bpy.types.UILayout, blender_id_type: str | bool, blender_property_name: str, component_id: str, component_property: str, text: str = "Add", icon: str | None = "ADD") -> bpy.types.OperatorProperties:
	ret = layout.operator(OP_Edit_Component_Collection, text=text, icon=icon) # pyright: ignore[reportArgumentType]
	if(type(blender_id_type) is str):
		ret.blender_id_type = blender_id_type
		ret.scene_collection = False
	else:
		ret.blender_id_type = ""
		ret.scene_collection = True
	ret.blender_property_name = blender_property_name
	ret.component_id = component_id
	ret.component_property = component_property
	ret.op = "add"
	return ret

def create_remove_button(layout: bpy.types.UILayout, blender_id_type: str | bool, blender_property_name: str, component_id: str, component_property: str, index: int, text: str = "", icon: str | None = "X") -> bpy.types.OperatorProperties:
	ret = layout.operator(OP_Edit_Component_Collection, text=text, icon=icon) # pyright: ignore[reportArgumentType]
	if(type(blender_id_type) is str):
		ret.blender_id_type = blender_id_type
		ret.scene_collection = False
	else:
		ret.blender_id_type = ""
		ret.scene_collection = True
	ret.blender_property_name = blender_property_name
	ret.component_id = component_id
	ret.component_property = component_property
	ret.index = index
	ret.op = "remove"
	return ret

def draw_list(layout: bpy.types.UILayout, blender_id_type: str | bool, resource: PSTF_ComponentResourceBase | PSTF_DataResourceBase, attr: str, blender_property_name: str, draw_func: Callable):
	col = layout.column(align=True)
	for index_element, element in enumerate(getattr(resource, attr)):
		layout_remove_btn = draw_func(col, element)
		create_remove_button(layout_remove_btn, blender_id_type, blender_property_name, resource.stf_id, attr, index_element)
	create_add_button(layout, blender_id_type, blender_property_name, resource.stf_id, attr)

import bpy

from ....base.blender_grr.stf_node_path_selector import NodePathSelector

class ConstraintSource(bpy.types.PropertyGroup):
	weight: bpy.props.FloatProperty(name="Weight", default=0.5, subtype="FACTOR", soft_min=0, soft_max=1) # type: ignore
	source: bpy.props.PointerProperty(name="Source", type=NodePathSelector) # type: ignore


import bpy

from collections.abc import Sequence

from ..stfblender_common import STF_Component_Ref, STF_Data_Ref
from ..stfblender_common.blender_grr import STFDataResourceReference
from ..stfblender_common.resource.stf_registry import find_eligible_export_handlers
from ..stfblender_common.utils.armature_bone import ArmatureBone


def _poll_stf_types(self, context: bpy.types.Context, text: str) -> list[tuple[str, str]]:
	context_type = self.id_data
	if(len(self.rna_ancestors()) > 0 and type(self.rna_ancestors()[len(self.rna_ancestors()) - 1]) is bpy.types.Bone):
		context_type = ArmatureBone(self.id_data, self.rna_ancestors()[len(self.rna_ancestors()) - 1].name)
	ret = []
	for handler in find_eligible_export_handlers(context_type):
		ret.append((handler[0].stf_type))
	return ret

class STF_Info(bpy.types.PropertyGroup):
	"""Basic STF properties for Blender structs that represent stf-node or stf-data resources"""
	determine_type: bpy.props.EnumProperty(name="Usage", description="Determine the STF type", default="auto", items=(("auto", "Auto", "Automatically determine the STF resource type"), ("none", "Ignore", "Do not export this resource"), ("manual", "Manual", "Manually specify the STF type")), options=set())
	use_as: bpy.props.StringProperty(name="Use as", description="STF type which represents this Blender resource", default="", search=_poll_stf_types, options=set())

	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID", options=set())
	stf_name: bpy.props.StringProperty(name="STF Name", description="Optional Name for STF export", options=set())
	stf_name_source_of_truth: bpy.props.BoolProperty(name="STF Name Is Source Of Truth", description="Use Blender name or specify one manually", options=set())
	stf_components: bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components", options=set())
	stf_active_component_index: bpy.props.IntProperty(name="Selected Component", options=set())


def _poll_stf_instance_types(self, context: bpy.types.Context, text: str) -> list[tuple[str, str]]:
	context_resources = []
	if(context.object.stf_instance.determine_type == "fallback"):
		context_resources.append((context.object, context.object.stf_json_fallback_instance))
	elif(context.object.data is not None):
		context_resources.append((context.object, context.object.data))

	ret = []
	for context_resource in context_resources:
		for handler in find_eligible_export_handlers(context_resource):
			ret.append((handler[0].stf_type))
	return ret

class STF_Instance(bpy.types.PropertyGroup):
	"""Basic STF properties for resources that represent instantiates on Objects"""
	determine_type: bpy.props.EnumProperty(name="Usage", description="Determine the STF type", default="auto", items=(("auto", "Auto", "Automatically determine the STF resource type"), ("none", "Ignore", "Do not export this resource"), ("fallback", "Fallback Instance", "Instantiates fallback resource"), ("manual", "Manual", "Manually specify the STF type")), options=set())
	use_as: bpy.props.StringProperty(name="Use as", description="STF type which represents this Blender resource", default="", search=_poll_stf_instance_types, options=set())

	stf_id: bpy.props.StringProperty(name="ID", options=set())
	stf_name: bpy.props.StringProperty(name="Name", options=set())
	enabled: bpy.props.BoolProperty(name="Enabled", default=True, options=set())


# TODO add more if relevant!
# Feel free to create a new issue or PR if you need more!
_blender_types: Sequence[type] = [
	bpy.types.Action,
	bpy.types.Armature,
	bpy.types.Bone,
	bpy.types.Brush,
	bpy.types.Camera,
	bpy.types.Collection,
	bpy.types.Curve,
	bpy.types.Curves,
	bpy.types.GreasePencil,
	bpy.types.Image,
	bpy.types.Key,
	bpy.types.Lattice,
	bpy.types.Library,
	bpy.types.Light,
	bpy.types.LightProbe,
	bpy.types.Mask,
	bpy.types.Material,
	bpy.types.Mesh,
	bpy.types.MetaBall,
	bpy.types.MovieClip,
	bpy.types.NodeTree,
	bpy.types.Object,
	bpy.types.PaintCurve,
	bpy.types.Palette,
	bpy.types.PointCloud,
	bpy.types.Scene,
	bpy.types.Screen,
	bpy.types.Sound,
	bpy.types.Speaker,
	bpy.types.Text,
	bpy.types.TextCurve,
	bpy.types.Texture,
	bpy.types.Volume,
	bpy.types.WindowManager,
	bpy.types.WorkSpace,
	bpy.types.World,
]
blender_types: Sequence[type] = _blender_types + [ArmatureBone]
"""List all Blender types that can be used as STF resources."""


def register():
	# STF-Data modules are stored on Collections
	bpy.types.Collection.stf_data_refs = bpy.props.CollectionProperty(type=STF_Data_Ref, name="STF Data Refs", options=set())
	bpy.types.Collection.stf_data_ref_selected = bpy.props.IntProperty(options=set())

	bpy.types.Object.stf_instance = bpy.props.PointerProperty(type=STF_Instance, options=set())

	for blender_type in _blender_types:
		blender_type.stf_info = bpy.props.PointerProperty(type=STF_Info, name="STF Info", options=set())


def unregister():
	for blender_type in _blender_types:
		if(hasattr(blender_type, "stf_info")):
			del blender_type.stf_info

	if hasattr(bpy.types.Object, "stf_instance"):
		del bpy.types.Object.stf_instance

	# STF-Data modules are stored on Collections
	if hasattr(bpy.types.Collection, "stf_data_ref_selected"):
		del bpy.types.Collection.stf_data_ref_selected
	if hasattr(bpy.types.Collection, "stf_data_refs"):
		del bpy.types.Collection.stf_data_refs

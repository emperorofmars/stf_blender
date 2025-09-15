import bpy

from .....base.stf_module_data import STF_BlenderDataResourceBase, STF_BlenderDataModule, STF_Data_Ref
from .....exporter.stf_export_context import STF_ExportContext
from .....importer.stf_import_context import STF_ImportContext
from .....utils.data_resource_utils import add_resource, export_data_resource_base, get_components_from_data_resource, import_data_resource_base


_stf_type = "dev.vrm.blendshape_pose"
_blender_property_name = "dev_vrm_blendshape_pose"


class Edit_VRM_Blendshape_Pose_Target(bpy.types.Operator):
	bl_idname = "stf.edit_vrm_blendshape_pose_target"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	use_scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	resource_id: bpy.props.StringProperty() # type: ignore

	op: bpy.props.BoolProperty() # type: ignore
	index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		collection = context.scene.collection if self.use_scene_collection else context.collection
		# let resource
		for resource in collection.dev_vrm_blendshape_pose:
			if(resource.stf_id == self.resource_id):
				break
		else:
			self.report({"ERROR"}, "Couldn't find resource")
			return {"CANCELLED"}
		if(self.op):
			resource.targets.add()
		else:
			resource.targets.remove(self.index)
		return {"FINISHED"}


class Edit_VRM_Blendshape_Pose_Value(bpy.types.Operator):
	bl_idname = "stf.edit_vrm_blendshape_pose_value"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	use_scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	resource_id: bpy.props.StringProperty() # type: ignore
	target_index: bpy.props.IntProperty() # type: ignore

	op: bpy.props.BoolProperty() # type: ignore
	index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		collection = context.scene.collection if self.use_scene_collection else context.collection
		# let resource
		for resource in collection.dev_vrm_blendshape_pose:
			if(resource.stf_id == self.resource_id):
				break
		else:
			self.report({"ERROR"}, "Couldn't find resource")
			return {"CANCELLED"}
		
		if(self.op):
			resource.targets[self.target_index].values.add()
		else:
			resource.targets[self.target_index].values.remove(self.index)
		return {"FINISHED"}


class VRM_Blendshape_Pose_Value(bpy.types.PropertyGroup):
	blendshape_name: bpy.props.StringProperty(name="Name") # type: ignore
	blendshape_value: bpy.props.FloatProperty(name="Value", default=0, soft_min=0, soft_max=1, subtype="FACTOR") # type: ignore

class VRM_Blendshape_Pose_Target(bpy.types.PropertyGroup):
	mesh_instance: bpy.props.PointerProperty(type=bpy.types.Object, name="Meshinstance", poll=lambda _, o: o.data and type(o.data) == bpy.types.Mesh) # type: ignore
	values: bpy.props.CollectionProperty(type=VRM_Blendshape_Pose_Value) # type: ignore

class VRM_Blendshape_Pose(STF_BlenderDataResourceBase):
	targets: bpy.props.CollectionProperty(type=VRM_Blendshape_Pose_Target) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Data_Ref, context_object: bpy.types.Collection, resource: VRM_Blendshape_Pose):
	add_button = layout.operator(Edit_VRM_Blendshape_Pose_Target.bl_idname, text="Add Target")
	add_button.use_scene_collection = context_object == context.scene.collection
	add_button.resource_id = resource.stf_id
	add_button.op = True
	for index, target in enumerate(resource.targets):
		box = layout.box()
		inner_row = box.row()
		inner_row.prop(target, "mesh_instance", text="")

		remove_button = inner_row.operator(Edit_VRM_Blendshape_Pose_Target.bl_idname, text="", icon="X")
		remove_button.use_scene_collection = context_object == context.scene.collection
		remove_button.resource_id = resource.stf_id
		remove_button.op = False
		remove_button.index = index

		row = box.row()
		row.label(text="Blendshapes")
		if(target.mesh_instance and type(target.mesh_instance.data) == bpy.types.Mesh):
			add_value_button = row.operator(Edit_VRM_Blendshape_Pose_Value.bl_idname, icon="PLUS", text="Add Value")
			add_value_button.use_scene_collection = context_object == context.scene.collection
			add_value_button.resource_id = resource.stf_id
			add_value_button.op = True
			add_value_button.target_index = index
			for value_index, value in enumerate(target.values):
				row = box.row(align=True)
				row.prop_search(value, "blendshape_name", target.mesh_instance.data.shape_keys, "key_blocks", text="")
				row.prop(value, "blendshape_value", text="")

				remove_button = row.operator(Edit_VRM_Blendshape_Pose_Value.bl_idname, text="", icon="X")
				remove_button.use_scene_collection = context_object == context.scene.collection
				remove_button.resource_id = resource.stf_id
				remove_button.op = False
				remove_button.target_index = index
				remove_button.index = value_index


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Collection) -> any:
	resource_ref, resource = add_resource(context.get_root_collection(), _blender_property_name, stf_id, _stf_type)
	import_data_resource_base(resource, json_resource)

	def _handle():
		for target_id, values in json_resource.get("targets", {}).items():
			if(meshinstance := context.get_imported_resource(target_id)):
				target = resource.targets.add()
				target.mesh_instance = meshinstance
				for blendshape_name, blendshape_value in values.items():
					value = target.values.add()
					value.blendshape_name = blendshape_name
					value.blendshape_value = blendshape_value

	context.add_task(_handle)

	return resource


def _stf_export(context: STF_ExportContext, resource: VRM_Blendshape_Pose, context_object: bpy.types.Collection) -> tuple[dict, str]:
	ret = export_data_resource_base(context, _stf_type, resource)

	target_dict: dict[str, dict[str, float]] = {}
	ret["targets"] = target_dict

	def _handle():
		for target in resource.targets:
			target: VRM_Blendshape_Pose_Target = target # Because syntax highlighting, srsly how vibecoded is all of this tooling? The type annotations are all there!
			if(target.mesh_instance):
				value_dict: dict[str, float] = {}
				if(target.mesh_instance.stf_info.stf_id not in target_dict):
					target_dict[target.mesh_instance.stf_info.stf_id] = value_dict
				else:
					value_dict = target_dict[target.mesh_instance.stf_info.stf_id]
				for value in target.values:
					value: VRM_Blendshape_Pose_Value = value # ffs
					if(value.blendshape_name and value.blendshape_name not in value_dict):
						value_dict[value.blendshape_name] = value.blendshape_value

	context.add_task(_handle)

	return ret, resource.stf_id


class STF_Module_VRM_Blendshape_Pose(STF_BlenderDataModule):
	stf_type = _stf_type
	stf_kind = "data"
	understood_application_types = [VRM_Blendshape_Pose]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	draw_resource_func = _draw_component
	get_components_func = get_components_from_data_resource


register_stf_modules = [
	STF_Module_VRM_Blendshape_Pose,
]


def register():
	bpy.types.Collection.dev_vrm_blendshape_pose = bpy.props.CollectionProperty(type=VRM_Blendshape_Pose) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "dev_vrm_blendshape_pose"):
		del bpy.types.Collection.dev_vrm_blendshape_pose

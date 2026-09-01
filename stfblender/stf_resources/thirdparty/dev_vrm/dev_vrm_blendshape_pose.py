import bpy
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STF_Category, STFReport, STF_NonNativeResourceBase, STF_Handler_NonNative, STF_NonNativeResource_Ref, add_nonnative_resource, export_nonnative_resource_base, get_components_from_nonnative_resource, import_nonnative_resource_base
from .....stfblender_common.helpers import register_exported_resource


_stf_type = "dev.vrm.blendshape_pose"
_blender_property_name = "dev_vrm_blendshape_pose"


class Edit_VRM_Blendshape_Pose_Target(bpy.types.Operator):
	bl_idname = "stf.edit_vrm_blendshape_pose_target"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	use_scene_collection: bpy.props.BoolProperty(default=False)
	resource_id: bpy.props.StringProperty()

	op: bpy.props.BoolProperty()
	index: bpy.props.IntProperty()

	def execute(self, context) -> set:
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

	use_scene_collection: bpy.props.BoolProperty(default=False)
	resource_id: bpy.props.StringProperty()
	target_index: bpy.props.IntProperty()

	op: bpy.props.BoolProperty()
	index: bpy.props.IntProperty()

	def execute(self, context) -> set:
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
	blendshape_name: bpy.props.StringProperty(name="Name", options=set())
	blendshape_value: bpy.props.FloatProperty(name="Value", default=0, soft_min=0, soft_max=1, subtype="FACTOR", options=set())

class VRM_Blendshape_Pose_Target(bpy.types.PropertyGroup):
	mesh_instance: bpy.props.PointerProperty(type=bpy.types.Object, name="Meshinstance", poll=lambda _, o: o.data and type(o.data) is bpy.types.Mesh, options=set())
	values: bpy.props.CollectionProperty(type=VRM_Blendshape_Pose_Value, options=set())

class VRM_Blendshape_Pose(STF_NonNativeResourceBase):
	targets: bpy.props.CollectionProperty(type=VRM_Blendshape_Pose_Target, options=set())


class Handler_VRM_Blendshape_Pose(STF_Handler_NonNative):
	"""Define a blendshape pose. This is useful for VR/V-Tubing avatars that get will get converted to VRM, since VRM doesn't support animations"""
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	understood_blender_types = [VRM_Blendshape_Pose]
	blender_property_name = _blender_property_name

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, resource_ref: STF_NonNativeResource_Ref, context_resource: bpy.types.Collection, resource: VRM_Blendshape_Pose):
		add_button = layout.operator(Edit_VRM_Blendshape_Pose_Target.bl_idname, text="Add Target", icon="ADD")
		add_button.use_scene_collection = context_resource == context.scene.collection
		add_button.resource_id = resource.stf_id
		add_button.op = True
		for index, target in enumerate(resource.targets):
			box = layout.box()
			inner_row = box.row(align=True)
			inner_row.prop(target, "mesh_instance", text="Mesh Instance", icon="MESH_DATA")

			remove_button = inner_row.operator(Edit_VRM_Blendshape_Pose_Target.bl_idname, text="", icon="X")
			remove_button.use_scene_collection = context_resource == context.scene.collection
			remove_button.resource_id = resource.stf_id
			remove_button.op = False
			remove_button.index = index

			row = box.row()
			row.label(text="Blendshapes")
			if(target.mesh_instance and type(target.mesh_instance.data) is bpy.types.Mesh):
				add_value_button = row.operator(Edit_VRM_Blendshape_Pose_Value.bl_idname, icon="ADD", text="Add Value")
				add_value_button.use_scene_collection = context_resource == context.scene.collection
				add_value_button.resource_id = resource.stf_id
				add_value_button.op = True
				add_value_button.target_index = index

				col = box.column(align=True)
				for value_index, value in enumerate(target.values):
					row = col.row(align=True)
					row.prop_search(value, "blendshape_name", target.mesh_instance.data.shape_keys, "key_blocks", text="")
					row.prop(value, "blendshape_value", text="")

					remove_button = row.operator(Edit_VRM_Blendshape_Pose_Value.bl_idname, text="", icon="X")
					remove_button.use_scene_collection = context_resource == context.scene.collection
					remove_button.resource_id = resource.stf_id
					remove_button.op = False
					remove_button.target_index = index
					remove_button.index = value_index

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: bpy.types.Collection) -> Any | STFReport:
		resource_ref, resource = add_nonnative_resource(context.get_root_collection(), cls.blender_property_name, stf_id, cls.stf_type)
		import_nonnative_resource_base(resource, json_resource)

		def _handle():
			for target_id_index_as_str_because_its_a_json_key, values in json_resource.get("targets", {}).items():
				target_id_index = int(target_id_index_as_str_because_its_a_json_key)
				meshinstance = context.import_resource(json_resource, target_id_index, STF_Category.NODE)
				if(type(meshinstance) is bpy.types.Object and type(meshinstance.data) is bpy.types.Mesh):
					target = resource.targets.add()
					target.mesh_instance = meshinstance
					for blendshape_name, blendshape_value in values.items():
						value = target.values.add()
						value.blendshape_name = blendshape_name
						value.blendshape_value = blendshape_value

		context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return resource

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: VRM_Blendshape_Pose, context_resource: bpy.types.Collection) -> tuple[dict, str] | STFReport:
		ret = export_nonnative_resource_base(context, cls.stf_type, component)

		target_dict: dict[str, dict[str, float]] = {}
		ret["targets"] = target_dict

		def _handle():
			for target in component.targets:
				target: VRM_Blendshape_Pose_Target = target # Because syntax highlighting
				if(target.mesh_instance):
					value_dict: dict[str, float] = {}
					mesh_id_index = register_exported_resource(ret, target.mesh_instance.stf_info.stf_id)
					if(mesh_id_index not in target_dict):
						target_dict[mesh_id_index] = value_dict  # pyright: ignore[reportArgumentType]
					else:
						value_dict = target_dict[mesh_id_index]
					for value in target.values:
						value: VRM_Blendshape_Pose_Value = value # Because syntax highlighting
						if(value.blendshape_name and value.blendshape_name not in value_dict):
							value_dict[value.blendshape_name] = value.blendshape_value

		context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return ret, component.stf_id

	get_components = get_components_from_nonnative_resource


def register():
	setattr(bpy.types.Collection, Handler_VRM_Blendshape_Pose.blender_property_name, bpy.props.CollectionProperty(type=VRM_Blendshape_Pose, options=set()))

def unregister():
	if hasattr(bpy.types.Collection, Handler_VRM_Blendshape_Pose.blender_property_name):
		delattr(bpy.types.Collection, Handler_VRM_Blendshape_Pose.blender_property_name)

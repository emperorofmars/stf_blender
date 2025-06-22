import json
import bpy

from .....exporter.stf_export_context import STF_ExportContext
from .....importer.stf_import_context import STF_ImportContext
from .....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base


_stf_type = "vrc.physbone"
_blender_property_name = "vrc_physbone"

# todo: this is quite jank, make this able to select the object/armature->bone/component etc..
class PhysboneReference(bpy.types.PropertyGroup):
	id: bpy.props.StringProperty(name="ID") # type: ignore

class VRC_Physbone(STF_BlenderComponentBase):
	ignores: bpy.props.CollectionProperty(type=PhysboneReference, name="Ignored Children") # type: ignore
	colliders: bpy.props.CollectionProperty(type=PhysboneReference, name="Colliders") # type: ignore
	values: bpy.props.StringProperty(name="Json Values") # type: ignore


class Edit_VRC_Physbone(bpy.types.Operator):
	bl_idname = "stf.edit_vrc_physbone"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore
	blender_bone: bpy.props.BoolProperty() # type: ignore

	op: bpy.props.StringProperty() # type: ignore
	property: bpy.props.StringProperty() # type: ignore
	index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		if(self.op == "add"):
			if(not self.blender_bone):
				for pb in context.object.vrc_physbone:
					if(pb.stf_id == self.component_id):
						getattr(pb, self.property).add()
						return {"FINISHED"}
			else:
				for pb in context.bone.vrc_physbone:
					if(pb.stf_id == self.component_id):
						getattr(pb, self.property).add()
						return {"FINISHED"}
		elif(self.op == "remove"):
			if(not self.blender_bone):
				for pb in context.object.vrc_physbone:
					if(pb.stf_id == self.component_id):
						getattr(pb, self.property).remove(self.index)
						return {"FINISHED"}
			else:
				for pb in context.bone.vrc_physbone:
					if(pb.stf_id == self.component_id):
						getattr(pb, self.property).remove(self.index)
						return {"FINISHED"}
		self.report({"ERROR"}, "Couldn't edit Physbone")
		return {"CANCELLED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: VRC_Physbone):
	box = layout.box()

	row = box.row()
	row.label(text="Colliders")
	add_button = row.operator(Edit_VRC_Physbone.bl_idname, text="Add")
	add_button.blender_bone = type(component.id_data) == bpy.types.Armature
	add_button.component_id = component.stf_id
	add_button.op = "add"
	add_button.property = "colliders"
	
	for index, collider in enumerate(component.colliders):
		row = box.row()
		row.prop(collider, "id")
		add_button = row.operator(Edit_VRC_Physbone.bl_idname, text="", icon="X")
		add_button.blender_bone = type(component.id_data) == bpy.types.Armature
		add_button.component_id = component.stf_id
		add_button.op = "remove"
		add_button.index = index
		add_button.property = "colliders"

	row = box.row()
	row.label(text="Ignores")
	add_button = row.operator(Edit_VRC_Physbone.bl_idname, text="Add")
	add_button.blender_bone = type(component.id_data) == bpy.types.Armature
	add_button.component_id = component.stf_id
	add_button.op = "add"
	add_button.property = "ignores"
	for index, ignore in enumerate(component.ignores):
		row = box.row()
		row.prop(ignore, "id")
		add_button = row.operator(Edit_VRC_Physbone.bl_idname, text="", icon="X")
		add_button.blender_bone = type(component.id_data) == bpy.types.Armature
		add_button.component_id = component.stf_id
		add_button.op = "remove"
		add_button.index = index
		add_button.property = "ignores"

	layout.prop(component, "values")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)
	component.values = json.dumps(json_resource["values"])

	for ignore in json_resource.get("ignores", []):
		new_ignore = component.ignores.add()
		new_ignore.id = ignore

	for collider in json_resource.get("colliders", []):
		new_collider = component.colliders.add()
		new_collider.id = collider

	return component


def _stf_export(context: STF_ExportContext, component: VRC_Physbone, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, component)
	ret["values"] = component.values

	ignores = []
	for ignore in component.ignores:
		ignores.append(ignore.id)
	ret["ignores"] = ignores

	colliders = []
	for collider in component.colliders:
		colliders.append(collider.id)
	ret["colliders"] = colliders

	return ret, component.stf_id


class STF_Module_VRC_Physbone(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["secondary_motion"]
	understood_application_types = [VRC_Physbone]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_VRC_Physbone
]


def register():
	bpy.types.Object.vrc_physbone = bpy.props.CollectionProperty(type=VRC_Physbone) # type: ignore
	bpy.types.Bone.vrc_physbone = bpy.props.CollectionProperty(type=VRC_Physbone) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "vrc_physbone"):
		del bpy.types.Object.vrc_physbone
	if hasattr(bpy.types.Bone, "vrc_physbone"):
		del bpy.types.Bone.vrc_physbone


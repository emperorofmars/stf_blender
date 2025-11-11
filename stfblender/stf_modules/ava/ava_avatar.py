import bpy

from ...base.stf_task_steps import STF_TaskSteps
from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base
from ...utils.misc import SetActiveObjectOperator
from ...utils.reference_helper import register_exported_resource, import_resource


_stf_type = "ava.avatar"
_blender_property_name = "stf_ava_avatar"


def _poll_armature_instance(self, blender_object: bpy.types.Object) -> bool:
	return blender_object.data and type(blender_object.data) == bpy.types.Armature
def _poll_mesh_instance(self, blender_object: bpy.types.Object) -> bool:
	return blender_object.data and type(blender_object.data) == bpy.types.Armature

class AVA_Avatar(STF_BlenderComponentBase):
	viewport: bpy.props.PointerProperty(type=bpy.types.Object, name="Viewport", description="This Object's location will be used to determine the viewport location", options=set()) # type: ignore
	primary_armature_instance: bpy.props.PointerProperty(type=bpy.types.Object, name="Main Armature Instance", description="Armature instance for humanoid IK, eye-rotations, ...", options=set(), poll=_poll_armature_instance) # type: ignore
	primary_mesh_instance: bpy.props.PointerProperty(type=bpy.types.Object, name="Main Mesh Instance", description="Mesh instance for facial visemes", options=set(), poll=_poll_mesh_instance) # type: ignore


class CreateViewportObjectOperator(bpy.types.Operator):
	"""Create a viewport object"""
	bl_idname = "ava.ava_avatar_create_viewport_object"
	bl_label = "Create Viewport Object"
	bl_options = {"REGISTER", "UNDO"}

	blender_collection: bpy.props.StringProperty() # type: ignore
	component_id: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		target_object = bpy.data.collections[self.blender_collection]
		if("$ViewportFirstPerson" in bpy.data.objects):
			viewport_object = bpy.data.objects["$ViewportFirstPerson"]
		else:
			viewport_object = bpy.data.objects.new("$ViewportFirstPerson", None)
			viewport_object.empty_display_size = 0.1
			viewport_object.empty_display_type = "SINGLE_ARROW"
			target_object.objects.link(viewport_object)
		for avatar_component in target_object.stf_ava_avatar:
			if(avatar_component.stf_id == self.component_id):
				avatar_component.viewport = viewport_object
				break

		return {"FINISHED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: AVA_Avatar):
	layout.use_property_split = True
	if(component.viewport):
		layout.prop(component, "viewport")
		row = layout.row()
		row.alignment = "RIGHT"
		row.operator(SetActiveObjectOperator.bl_idname, text="Select Viewport Object", icon="EYEDROPPER").target_name = "$ViewportFirstPerson"
	else:
		create_viewport_button = layout.operator(CreateViewportObjectOperator.bl_idname, text="Create Viewport Object", icon="ADD")
		create_viewport_button.blender_collection = parent_application_object.name
		create_viewport_button.component_id = component.stf_id

	layout.prop(component, "primary_armature_instance", icon="ARMATURE_DATA")
	if(component.primary_armature_instance and (not component.primary_armature_instance.data or type(component.primary_armature_instance.data) != bpy.types.Armature)):
		layout.label(text="Warning! The Object doesn't instantiate an Armature!")

	layout.prop(component, "primary_mesh_instance", icon="MESH_DATA")
	if(component.primary_mesh_instance and (not component.primary_mesh_instance.data or type(component.primary_mesh_instance.data) != bpy.types.Mesh)):
		layout.label(text="Warning! The Object doesn't instantiate a Mesh!")



def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)
	import_component_base(context, component, json_resource)

	if("viewport" in json_resource):
		def _handle_viewport():
			component.viewport = import_resource(context, json_resource, json_resource["viewport"], "node")
		context.add_task(STF_TaskSteps.DEFAULT, _handle_viewport)

	if("primary_armature_instance" in json_resource):
		def _handle_primary_armature_instance():
			component.primary_armature_instance = import_resource(context, json_resource, json_resource["primary_armature_instance"], "node")
		context.add_task(STF_TaskSteps.DEFAULT, _handle_primary_armature_instance)

	if("primary_mesh_instance" in json_resource):
		def _handle_primary_mesh_instance():
			component.primary_mesh_instance = import_resource(context, json_resource, json_resource["primary_mesh_instance"], "node")
		context.add_task(STF_TaskSteps.DEFAULT, _handle_primary_mesh_instance)

	return component


def _stf_export(context: STF_ExportContext, component: AVA_Avatar, parent_application_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)

	if(component.viewport):
		def _handle_viewport():
			ret["viewport"] = register_exported_resource(ret, context.get_resource_id(component.viewport))
		context.add_task(STF_TaskSteps.DEFAULT, _handle_viewport)

	if(component.primary_armature_instance and component.primary_armature_instance.data and type(component.primary_armature_instance.data) == bpy.types.Armature):
		def _handle_primary_armature_instance():
			ret["primary_armature_instance"] = register_exported_resource(ret, context.get_resource_id(component.primary_armature_instance))
		context.add_task(STF_TaskSteps.DEFAULT, _handle_primary_armature_instance)

	if(component.primary_mesh_instance and component.primary_mesh_instance.data and type(component.primary_mesh_instance.data) == bpy.types.Mesh):
		def _handle_primary_mesh_instance():
			ret["primary_mesh_instance"] = register_exported_resource(ret, context.get_resource_id(component.primary_mesh_instance))
		context.add_task(STF_TaskSteps.DEFAULT, _handle_primary_mesh_instance)

	return ret, component.stf_id


class STF_Module_AVA_Avatar(STF_BlenderComponentModule):
	"""Represents a VR & V-tubing avatar model"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_Avatar]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_AVA_Avatar
]


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=AVA_Avatar))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)

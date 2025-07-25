import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base
from ....utils.op_utils import SetActiveObjectOperator
from ....utils.reference_helper import export_resource


_stf_type = "ava.avatar"
_blender_property_name = "stf_ava_avatar"


class AVA_Avatar(STF_BlenderComponentBase):
	viewport: bpy.props.PointerProperty(type=bpy.types.Object, name="Viewport") # type: ignore
	primary_armature_instance: bpy.props.PointerProperty(type=bpy.types.Object, name="Primary Armature Instance") # type: ignore
	primary_mesh_instance: bpy.props.PointerProperty(type=bpy.types.Object, name="Primary Mesh Instance") # type: ignore


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
	if(component.viewport):
		layout.prop(component, "viewport")
		layout.operator(SetActiveObjectOperator.bl_idname, text="Select Viewport Object").target_name = "$ViewportFirstPerson"
	else:
		create_viewport_button = layout.operator(CreateViewportObjectOperator.bl_idname, text="Create Viewport Object")
		create_viewport_button.blender_collection = parent_application_object.name
		create_viewport_button.component_id = component.stf_id
	
	layout.prop(component, "primary_armature_instance")
	if(component.primary_armature_instance and (not component.primary_armature_instance.data or type(component.primary_armature_instance.data) != bpy.types.Armature)):
		layout.label(text="Warning! The Object isn't an Armature!")
	
	layout.prop(component, "primary_mesh_instance")
	if(component.primary_mesh_instance and (not component.primary_mesh_instance.data or type(component.primary_mesh_instance.data) != bpy.types.Mesh)):
		layout.label(text="Warning! The Object isn't an Mesh!")



def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)
	import_component_base(component, json_resource)

	if("viewport" in json_resource):
		def _handle_viewport():
			component.viewport = context.get_imported_resource(json_resource["viewport"])
		context.add_task(_handle_viewport)

	if("primary_armature_instance" in json_resource):
		def _handle_primary_armature_instance():
			component.primary_armature_instance = context.get_imported_resource(json_resource["primary_armature_instance"])
		context.add_task(_handle_primary_armature_instance)

	if("primary_mesh_instance" in json_resource):
		def _handle_primary_mesh_instance():
			component.primary_mesh_instance = context.get_imported_resource(json_resource["primary_mesh_instance"])
		context.add_task(_handle_primary_mesh_instance)

	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_Avatar, parent_application_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, application_object)

	if(application_object.viewport):
		def _handle_viewport():
			ret["viewport"] = export_resource(ret, context.get_resource_id(application_object.viewport))
		context.add_task(_handle_viewport)
		
	if(application_object.primary_armature_instance and application_object.primary_armature_instance.data and type(application_object.primary_armature_instance.data) == bpy.types.Armature):
		def _handle_primary_armature_instance():
			ret["primary_armature_instance"] = export_resource(ret, context.get_resource_id(application_object.primary_armature_instance))
		context.add_task(_handle_primary_armature_instance)
		
	if(application_object.primary_mesh_instance and application_object.primary_mesh_instance.data and type(application_object.primary_mesh_instance.data) == bpy.types.Mesh):
		def _handle_primary_mesh_instance():
			ret["primary_mesh_instance"] = export_resource(ret, context.get_resource_id(application_object.primary_mesh_instance))
		context.add_task(_handle_primary_mesh_instance)

	return ret, application_object.stf_id


class STF_Module_AVA_Avatar(STF_BlenderComponentModule):
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
	bpy.types.Collection.stf_ava_avatar = bpy.props.CollectionProperty(type=AVA_Avatar) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "stf_ava_avatar"):
		del bpy.types.Collection.stf_ava_avatar


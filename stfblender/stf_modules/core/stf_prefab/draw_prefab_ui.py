import bpy

from ....utils.id_utils import draw_stf_id_ui
from ....utils.component_ui import draw_components_ui, set_stf_component_filter
from ....utils.data_resource_ui import draw_data_resources_ui
from ....base.stf_meta import draw_meta_editor
from ....utils.misc import OpenWebpage, draw_slot_link_warning
from ....utils.dev_utils import draw_dev_tools


def draw_prefab_ui(layout: bpy.types.UILayout, context: bpy.types.Context, collection: bpy.types.Collection, operator_set_as_root: str, operator_set_id: str, operator_add_component: str, operator_remove_component: str, operator_edit_component_id: str):
	set_stf_component_filter(bpy.types.Collection)

	if(collection.stf_use_collection_as_prefab):
		draw_slot_link_warning(layout)

		# Export Functionality
		from ....exporter.exporter import ExportSTF
		if(context.scene.stf_root_collection == collection or collection == context.scene.collection and context.scene.stf_root_collection == None):
			layout.operator(operator=ExportSTF.bl_idname, text="Export as STF", icon="EXPORT")
		else:
			layout.operator(operator_set_as_root)
			if(collection == context.scene.collection):
				layout.operator(operator=ExportSTF.bl_idname, text="Export this Scene as STF root prefab", icon="EXPORT").scene_collection_as_root = True
			else:
				layout.operator(operator=ExportSTF.bl_idname, text="Export this Collection as STF", icon="EXPORT").current_collection_as_root = True

		# Set ID
		layout.separator(factor=1, type="SPACE")
		draw_stf_id_ui(layout, context, collection, collection.stf_info, operator_set_id)

		# Asset metadata editor
		layout.separator(factor=1, type="SPACE")
		header, body = layout.panel("stf.prefab_meta", default_closed = True)
		header.label(text="Asset Metadata")
		if(body): draw_meta_editor(body.box(), collection, collection == context.scene.collection)

		# Components
		layout.separator(factor=3, type="LINE")
		header, body = layout.panel("stf.prefab_components", default_closed = False)
		header.label(text="STF Components", icon="GROUP")
		if(body): draw_components_ui(layout, context, collection.stf_info, collection, operator_add_component, operator_remove_component, operator_edit_component_id)

		# Data Resources
		layout.separator(factor=3, type="LINE")
		header, body = layout.panel("stf.prefab_data_resources", default_closed = False)
		header.label(text="STF Data Resources", icon="GROUP")
		if(body): draw_data_resources_ui(layout, context, collection)

	# Dev Options
	layout.separator(factor=3, type="LINE")
	dev_header, dev_body = layout.panel("stf.devtools_collection", default_closed = True)
	dev_header.label(text="Devtools")
	if(dev_body): draw_dev_tools(dev_body)

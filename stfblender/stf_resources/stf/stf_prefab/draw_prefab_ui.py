import bpy


def draw_prefab_ui(layout: bpy.types.UILayout, context: bpy.types.Context, collection: bpy.types.Collection, operator_set_as_root: str, operator_set_id: str, operator_add_component: str, operator_remove_component: str, operator_edit_component_id: str):
	from .....stfblender_common.helpers import draw_slot_link_warning
	from .....stfblender_common.slot_link import get_slot_link_data_model_version
	from ....ui.stf_meta import draw_meta_editor
	from ....ui import draw_components_ui, draw_stf_id_ui

	draw_slot_link_warning(layout)

	# Export Functionality
	from ....io.exporter.exporter import ExportSTF
	if(context.scene.stf_root_collection == collection or collection == context.scene.collection and context.scene.stf_root_collection is None):
		layout.operator(operator=ExportSTF.bl_idname, text="Export as STF", icon="EXPORT")
	else:
		layout.operator(operator_set_as_root)
		if(collection == context.scene.collection):
			layout.operator(operator=ExportSTF.bl_idname, text="Export Scene as STF", icon="EXPORT").scene_collection_as_root = True
		else:
			layout.operator(operator=ExportSTF.bl_idname, text="Export Collection as STF", icon="EXPORT").current_collection_as_root = True

	# Set ID
	layout.separator(factor=1, type="SPACE")
	draw_stf_id_ui(layout, context, collection, collection.stf_info, operator_set_id)

	# Asset metadata editor
	layout.separator(factor=1, type="SPACE")
	header, body = layout.panel("stf.prefab_meta", default_closed = True)
	header.label(text="Asset Metadata")
	if(body): draw_meta_editor(body, collection, collection == context.scene.collection)

	# Animation handling
	slot_link_version = get_slot_link_data_model_version()
	if(slot_link_version is not None and (slot_link_version[0] > 0 or slot_link_version[1] >= 2)):
		layout.separator(factor=1, type="SPACE")

		actions_valid: list[bpy.types.Action] = []
		actions_invalid: list[bpy.types.Action] = []
		for action in bpy.data.actions:
			if(action.stf_animation.exclude or action.is_action_legacy or action.slot_link.target_collection is not None and collection != context.scene.collection and action.slot_link.target_collection is not collection or len(action.slot_link.links) == 0):
				actions_invalid.append(action)
			else:
				actions_valid.append(action)

		header, body = layout.panel("stf.prefab_animations", default_closed = True)
		header.label(text=f"Animations To Export ({len(actions_valid)}/{len(bpy.data.actions)})")
		if(body):
			if(len(actions_invalid) > 0):
				body.label(text=f"Invalid Animations ({len(actions_invalid)})", icon="X")
				for action in actions_invalid:
					split = body.split(factor=0.05)
					split.separator()
					row = split.row()
					row.label(text=action.name)
					if(action.stf_animation.exclude):
						row.label(text="(Action is manually excluded)")
					elif(action.is_action_legacy):
						row.label(text="(Legacy Actions are not supported)")
					elif(action.slot_link.target_collection is not None and collection != context.scene.collection and action.slot_link.target_collection is not collection):
						row.label(text="(Action targets a different Collection)")
					elif(len(action.slot_link.links) == 0):
						row.label(text="(Action has no Slot Link targets)")
			if(len(actions_valid) > 0):
				body.label(text=f"Valid Animations ({len(actions_valid)})", icon="CHECKMARK")
				for action in actions_valid:
					split = body.split(factor=0.05)
					split.separator()
					row = split.row()
					row.label(text=action.name)

	# Components
	layout.separator(factor=3, type="LINE")
	header, body = layout.panel("stf.prefab_components", default_closed = False)
	header.label(text="STF Components (" + str(len(collection.stf_info.stf_components)) + ")", icon="GROUP")
	if(body): draw_components_ui(layout, context, collection.stf_info, collection, operator_add_component, operator_remove_component, operator_edit_component_id)

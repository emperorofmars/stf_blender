import bpy


def draw_component_info(layout: bpy.types.UILayout, component_holder: any, component_ref_holder: any, component_id: str):
	# let component_ref
	for component_ref in component_ref_holder.stf_components:
		if(component_ref.stf_id == component_id):
			break
	# let component
	for component in getattr(component_holder, component_ref.blender_property_name):
		if(component.stf_id == component_id):
			break

	if(component):
		if(layout.use_property_split):
			split = layout.split(factor=0.4)
			split.row()
			row = split.row()
			row.label(text=component_ref.stf_type + " - " + (component.stf_name if component.stf_name and len(component.stf_name) > 0 else "Unnamed"))
		else:
			layout.label(text=component_ref.stf_type + " - " + (component.stf_name if component.stf_name and len(component.stf_name) > 0 else "Unnamed"))

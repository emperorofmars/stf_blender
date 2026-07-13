from . import stf_dependency_import


def register():
	if(stf_dependency_import.selected_stf_extension):
		from . import template_stf_data_resource
		from . import template_stf_component_resource
		template_stf_data_resource.register()
		template_stf_component_resource.register()

def unregister():
	if(stf_dependency_import.selected_stf_extension):
		from . import template_stf_data_resource
		from . import template_stf_component_resource
		template_stf_data_resource.unregister()
		template_stf_component_resource.unregister()


if(stf_dependency_import.selected_stf_extension):
	from .template_stf_data_resource import CustomSTFBrushHandler
	from .template_stf_component_resource import MyCustomSTFSqueakComponentHandler
	register_stf_handlers = [CustomSTFBrushHandler, MyCustomSTFSqueakComponentHandler]


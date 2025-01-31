from . import stf_dependency_import


def register():
	if(stf_dependency_import.selected_stf_extension):
		from . import template_stf_data_module
		from . import template_stf_component_module
		template_stf_data_module.register()
		template_stf_component_module.register()

def unregister():
	if(stf_dependency_import.selected_stf_extension):
		from . import template_stf_data_module
		from . import template_stf_component_module
		template_stf_data_module.unregister()
		template_stf_component_module.unregister()


if(stf_dependency_import.selected_stf_extension):
	from . import template_stf_data_module
	from . import template_stf_component_module
	register_stf_modules = template_stf_data_module.register_stf_modules + template_stf_component_module.register_stf_modules # + any other array of STF_Module


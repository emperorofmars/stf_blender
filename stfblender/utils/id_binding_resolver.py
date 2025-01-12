from typing import Callable


class STF_Blender_BindingResolver():
	"""Extension to STF_Module which also associates a function to draw the component in Blender's UI"""
	target_blender_binding_types = list[any]
	resolve_id_binding_func: Callable[[any, str], any]


def resolve_id_binding(context: any, blender_object: any, id_binding: list[str]) -> any:
	potential_modules = []
	for app_type, hook in context._state._modules.items():
		potential_modules.append((app_type, hook))
	for app_type, hooklist in context._state._hooks.items():
		for hook in hooklist:
			potential_modules.append((app_type, hook))

	resolver_modules: dict[any, list[STF_Blender_BindingResolver]] = {}
	for _, module in potential_modules:
		if(isinstance(module, STF_Blender_BindingResolver) or hasattr(module, "resolve_id_binding_func")):
			for app_type in module.target_blender_binding_types:
				if(not app_type in resolver_modules): resolver_modules[app_type] = []
				resolver_modules[app_type].append(module)

	cur_object = blender_object
	for id in id_binding:
		resolved = False
		for resolver in resolver_modules[type(cur_object)]:
			resolver_ret = resolver.resolve_id_binding_func(cur_object, id)
			if(resolver_ret):
				cur_object = resolver_ret
				resolved = True
				break
		if(not resolved):
			return None
	return cur_object

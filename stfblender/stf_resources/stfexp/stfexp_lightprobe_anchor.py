import bpy
from typing import Any

from bpy.types import Context, UILayout

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, STFReport, add_component, export_component_base, import_component_base
from ....stfblender_common.helpers import register_exported_resource


class STFEXP_LightprobeAnchor(STF_ComponentResourceBase):
	anchor_object: bpy.props.PointerProperty(type=bpy.types.Object, name="Anchor Object", options=set())
	anchor_bone: bpy.props.StringProperty(name="Anchor Bone", options=set())


class Handler_STFEXP_LightprobeAnchor(STF_Handler_Component):
	"""Define a object/bone from which a game-engine will sample lightprobe values"""
	stf_type = "stfexp.lightprobe_anchor"
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [STFEXP_LightprobeAnchor]
	like_types = ["lightprobe_anchor"]
	blender_property_name = "stfexp_lightprobe_anchor"
	single = True
	filter = [bpy.types.Object]
	pretty_name_template = "Lightprobe Anchor"

	@classmethod
	def draw(cls, layout: UILayout, context: Context, component_ref: STF_Component_Ref, context_resource: Any, component: Any) -> None:
		layout.use_property_split = True
		layout.prop(component, "anchor_object")
		if(component.anchor_object and type(component.anchor_object.data) is bpy.types.Armature):
			layout.prop_search(component, "anchor_bone", component.anchor_object.data, "bones")

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any | None) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		if("anchor" in json_resource):
			if(len(json_resource["anchor"]) == 1):
				def _handle_target_object():
					anchor_object = context.import_resource(json_resource, json_resource["anchor"][0], STF_Category.NODE)
					if(type(anchor_object) is bpy.types.Object):
						component.anchor_object = anchor_object
				context.add_task(STF_TaskSteps.DEFAULT, _handle_target_object)
			elif(len(json_resource["anchor"]) == 3):
				def _handle_target_object():
					anchor_object = context.import_resource(json_resource, json_resource["anchor"][0], STF_Category.NODE)
					if(type(anchor_object) is bpy.types.Object):
						component.anchor_object = anchor_object
					if(bone := context.import_resource(json_resource, json_resource["anchor"][2], STF_Category.NODE)):
						component.anchor_bone = bone.name
				context.add_task(STF_TaskSteps.DEFAULT, _handle_target_object)

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: Any, context_resource: Any | None) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)

		if(component.anchor_object):
			def _handle():
				if(type(component.anchor_object.data) is bpy.types.Armature and component.anchor_bone):
					ret["anchor"] = [register_exported_resource(ret, component.anchor_object.stf_info.stf_id), "instance", register_exported_resource(ret, component.anchor_object.data.bones[component.anchor_bone].stf_info.stf_id)]
				else:
					ret["anchor"] = [register_exported_resource(ret, component.anchor_object.stf_info.stf_id)]

			context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return ret, component.stf_id


def register():
	setattr(bpy.types.Object, Handler_STFEXP_LightprobeAnchor.blender_property_name, bpy.props.CollectionProperty(type=STFEXP_LightprobeAnchor))

def unregister():
	if hasattr(bpy.types.Object, Handler_STFEXP_LightprobeAnchor.blender_property_name):
		delattr(bpy.types.Object, Handler_STFEXP_LightprobeAnchor.blender_property_name)

import bpy
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_Handler_ComponentHolder, STF_Handler_BlenderNative, STF_ImportContext, STFReport, STFReportSeverity, STF_Category, STF_Handler_BlenderNative, boilerplate_register, boilerplate_unregister, get_components_from_object, ensure_stf_id
from .stf_image_ops import STFAddImageComponentOperator, STFEditImageComponentIdOperator, STFImageFixColorspace, STFRemoveImageComponentOperator, STFSetImageIDOperator


_stf_type = "stf.image"


class STF_Image(bpy.types.PropertyGroup):
	is_normal_map: bpy.props.BoolProperty(name="Use as Normal-Map", default=False, options=set()) # type: ignore


class Handler_STF_Image(STF_Handler_BlenderNative, STF_Handler_ComponentHolder):
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	like_types = ["image"]
	understood_blender_types = [bpy.types.Image]

	operator_set_stf_id = STFSetImageIDOperator.bl_idname

	@staticmethod
	def draw(layout: bpy.types.UILayout, context: bpy.types.Context, blender_resource: tuple[bpy.types.Object, bpy.types.Mesh]) -> None:
		layout.prop(context.edit_image.stf_image, "is_normal_map")

		if(context.edit_image.stf_image.is_normal_map and context.edit_image.colorspace_settings.name != "Non-Color"):
			warn_row = layout.row()
			warn_row.alert = True
			warn_row.label(text="Invalid Color Space!", icon="WARNING_LARGE")
			warn_row.operator(STFImageFixColorspace.bl_idname)
			layout.label(text="A Normal-Maps Color Space must be Non-Color!", icon="INFO_LARGE")

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		blender_image = bpy.data.images.new(json_resource.get("name", "STF Image"), 8, 8)
		blender_image.stf_info.stf_id = stf_id
		if(json_resource.get("name")):
			blender_image.stf_info.stf_name = json_resource["name"]
			blender_image.stf_info.stf_name_source_of_truth = True

		try:
			image_buffer = context.import_buffer(json_resource, json_resource["buffer"])
			blender_image.pack(data=image_buffer, data_len=len(image_buffer)) # pyright: ignore[reportArgumentType]
			blender_image.source = "FILE"

			if("data_type" in json_resource):
				match(json_resource["data_type"]):
					case "color":
						blender_image.colorspace_settings.name = "sRGB"
					case "non_color":
						blender_image.colorspace_settings.name = "Non-Color"
					case "normal":
						blender_image.colorspace_settings.name = "Non-Color"
						blender_image.stf_image.is_normal_map = True

				if(json_resource["data_type"] == "non_color"):
					blender_image.colorspace_settings.name = "Non-Color"

			return blender_image
		except Exception as error:
			return STFReport("Could not import image", STFReportSeverity.Error, stf_id, _stf_type)

	@staticmethod
	def export_resource(context: STF_ExportContext, application_object: Any, context_object: Any) -> tuple[dict, str] | STFReport:
		blender_image: bpy.types.Image = application_object
		ensure_stf_id(context, blender_image)

		try:
			## let image_bytes: bytes
			if(blender_image.packed_file):
				image_bytes = blender_image.packed_file.data
			else:
				import pathlib
				image_bytes = pathlib.Path(bpy.path.abspath(blender_image.filepath)).resolve().read_bytes()

			ret = {
				"type": _stf_type,
				"name": blender_image.stf_info.stf_name if blender_image.stf_info.stf_name_source_of_truth else blender_image.name,
				"format": blender_image.file_format.lower(),
				"data_type": "non_color" if blender_image.colorspace_settings.name == "Non-Color" else "color"
			}
			ret["buffer"] = context.serialize_buffer(ret, image_bytes)

			if(blender_image.stf_image.is_normal_map):
				ret["data_type"] = "normal"
			else:
				match blender_image.colorspace_settings.name:
					case "sRGB": ret["data_type"] = "color"
					case "Non-Color": ret["data_type"] = "non_color"
					case _: ret["data_type"] = None

			return ret, blender_image.stf_info.stf_id
		except Exception as error:
			return STFReport("Could not export image: " + str(blender_image.filepath), STFReportSeverity.Error, blender_image.stf_info.stf_id, _stf_type, blender_image)

	get_components = get_components_from_object
	operator_component_add = STFAddImageComponentOperator.bl_idname
	operator_component_remove = STFRemoveImageComponentOperator.bl_idname
	operator_component_edit = STFEditImageComponentIdOperator.bl_idname


def register():
	boilerplate_register(bpy.types.Image)
	bpy.types.Image.stf_image = bpy.props.PointerProperty(type=STF_Image, options=set())


def unregister():
	if hasattr(bpy.types.Image, "stf_image"):
		del bpy.types.Image.stf_image
	boilerplate_unregister(bpy.types.Image)

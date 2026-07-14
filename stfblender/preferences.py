import bpy
import addon_utils

from ..stfblender_common.helpers import draw_slot_link_warning, draw_multiline_text
from .package_key import package_key


class STF_Extension_Preferences(bpy.types.AddonPreferences):
	bl_idname = package_key

	#enable_dev_mode: bpy.props.BoolProperty(name="Enable Development Mode", default=False) # type: ignore

	def draw(self, context: bpy.types.Context):
		layout = self.layout
		draw_slot_link_warning(layout)

		this_extensions_handlers: list[object] = []
		stf_extensions: dict[str, tuple[str, tuple, bool, list[object]]] = {}

		import sys
		for mod in addon_utils.modules(): # pyright: ignore[reportGeneralTypeIssues]
			try:
				python_module = sys.modules[mod.__name__]
				if(not hasattr(python_module, "register_stf_handlers")):
					continue
				elif(mod.__name__.endswith(".stf_blender")):
					this_extensions_handlers = getattr(python_module, "register_stf_handlers")
				else:
					stf_extensions[mod.__name__] = (mod.bl_info.get("name"), mod.bl_info.get("version"), addon_utils.check(mod.__name__)[1], getattr(python_module, "register_stf_handlers"))
			except Exception:
				continue

		layout.separator(factor=0.5, type="SPACE")
		header, body = layout.panel("stf.list_handlers", default_closed = True)
		header.label(text="Default Resource Handlers (" + str(len(this_extensions_handlers)) + ")")
		if(body):
			split = body.split(factor=0.02)
			split.column()
			col = split.column()
			draw_handler_list(col, context, this_extensions_handlers)
		layout.separator(factor=2, type="LINE")

		layout.label(text="Detected STF Extensions (" + str(len(stf_extensions)) + ")")
		for extension_module, extension in stf_extensions.items():
			header, body = layout.box().panel("stf.extensions_list_item_" + extension_module, default_closed = True)
			row = header.row()
			if(extension_module.endswith(".stf_blender")):
				row.label(icon="HEART")
			else:
				if(extension[2]):
					row.operator("preferences.addon_disable", text="", icon="CHECKBOX_HLT", emboss=False).module = extension_module
				else:
					row.operator("preferences.addon_enable", text="", icon="CHECKBOX_DEHLT", emboss=False).module = extension_module
			row_l = row.row()
			row_l.alignment = "LEFT"
			row_l.label(text=extension[0])
			row_lr = row_l.row()
			row_lr.active = False
			row_lr.alignment = "RIGHT"
			row_lr.label(text="v" + ".".join([str(v) for v in extension[1]]) + "")
			row.row() # padding
			row_r = row.row()
			row_r.active = False
			row_r.alignment = "RIGHT"
			row_r.label(text=extension_module)
			if(body):
				split = body.split(factor=0.02)
				split.column()
				col = split.column(align=True)
				col.label(text="Detected STF Resource Handlers:")
				col.separator(factor=2)

				draw_handler_list(col, context, extension[3])


def draw_handler_list(layout: bpy.types.UILayout, context: bpy.types.Context, handlers: list):
	row = layout.row(align=True)
	row.active = False
	row.label(text="Class")
	row.label(text="STF Type")
	row.label(text="STF Category")
	row.label(text="Blender Types")

	layout.separator(factor=1, type="LINE")
	col = layout.column(align=True)
	for handler_idx, handler in enumerate(handlers):
		is_valid = hasattr(handler, "stf_type") and handler.stf_type and hasattr(handler, "stf_category") and handler.stf_category and hasattr(handler, "understood_application_types") and handler.understood_application_types

		row_outer = col.row(align=True)
		col_l = row_outer.column(align=True)
		col_r = row_outer.column(align=True)
		row = col_l.row(align=True)
		row_doc = col_l.row(align=True)

		row.label(text=handler.__name__)
		if(is_valid):
			row.label(text=handler.stf_type)
			row.label(text=handler.stf_category.capitalize())
			for t in handler.understood_application_types:
				col_r.label(text=t.__name__)
				row_inner = col_r.row()
				row_inner.active = False
				row_inner.scale_x = row_inner.scale_y = 0.6
				row_inner.label(text=t.__module__)
		else:
			if(hasattr(handler, "hook_target_application_types") and handler.hook_target_application_types):
				row.label(text="")
				row.label(text="Hook")
				for t in handler.hook_target_application_types:
					col_r.label(text=t.__name__)
					row_inner = col_r.row()
					row_inner.active = False
					row_inner.scale_x = row_inner.scale_y = 0.6
					row_inner.label(text=t.__module__)
			elif(hasattr(handler, "stf_category") and handler.stf_category):
				row.label(text="Fallback")
				row.label(text=handler.stf_category.capitalize())
				row.label(text="")
			else:
				row.label(text="Unknown")
				row.label(text="Unknown")
				row.label(text="")
		if(handler.__doc__):
			row = row_doc
			row.active = False
			row.scale_x = row.scale_y = 0.6
			draw_multiline_text(row, handler.__doc__, 120, None)
		if(handler_idx < len(handlers) - 1):
			col.separator(factor=1, type="LINE")

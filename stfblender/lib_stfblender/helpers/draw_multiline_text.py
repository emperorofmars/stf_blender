import bpy
import textwrap

def draw_multiline_text(layout: bpy.types.UILayout, text: str, width: int = 80, icon: str | None = "INFO_LARGE", alert: bool = False) -> bpy.types.UILayout:
	wrap = textwrap.TextWrapper(width=width)
	row = layout.row()
	if(alert):
		row.alert = True
	if(icon):
		row.column().label(text="", icon=icon)
	col_r = row.column()
	if(not text.endswith(".")):
		text += "."
	for actual_line in text.split("\n"):
		for line in wrap.wrap(text=actual_line):
			col_r.label(text=line)
	return col_r

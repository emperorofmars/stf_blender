import bpy
import textwrap

def draw_multiline_text(layout: bpy.types.UILayout, text: str, width: int = 80):
	wrap = textwrap.TextWrapper(width=width)
	row = layout.row()
	row.column().label(text="", icon="INFO_LARGE")
	col_r = row.column()
	if(not text.endswith(".")):
		text += "."
	for line in wrap.wrap(text=text):
		col_r.label(text=line)

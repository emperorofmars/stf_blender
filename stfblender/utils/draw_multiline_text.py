import bpy

def draw_multiline_text(layout: bpy.types.UILayout, text: str):
	row = layout.row()
	row.column().label(text="", icon="INFO_LARGE")
	col_r = row.column()
	if(not text.endswith(".")):
		text += "."
	for line in text.split("\n"): # Todo more intelligent splitting
		remaining = line
		while(len(remaining) > 80):
			col_r.label(text=remaining[:80])
			remaining = remaining[80:]
		col_r.label(text=remaining)

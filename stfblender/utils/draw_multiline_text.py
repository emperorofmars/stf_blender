import bpy

def draw_multiline_text(layout: bpy.types.UILayout, text: str):
	first = True
	if(not text.endswith(".")):
		text += "."
	for line in text.split("\n"):
		remaining = line
		while(len(remaining) > 80):
			layout.label(text=remaining[:80], icon="INFO_LARGE" if first else "NONE")
			remaining = remaining[80:]
			first = False
		layout.label(text=remaining, icon="INFO_LARGE" if first else "NONE")
		first = False

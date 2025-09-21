import bpy


"""
Blender Resource Reference

Bringing polymorphism to Blender
"""


blender_type_values = (
	("ACTION","Action",""),
	("ARMATURE","Armature",""),
	("BRUSH","Brush",""),
	("CAMERA","Camera",""),
	("COLLECTION","Collection",""),
	("CURVE","Curve",""),
	("CURVES","Curves",""),
	("GREASEPENCIL","Greasepencil",""),
	("GREASEPENCIL_V3","Greasepencil V3",""),
	("IMAGE","Image",""),
	("KEY","Key","Shapekey / Blendshape"),
	("LATTICE","Lattice",""),
	("LIBRARY","Library",""),
	("LIGHT","Light",""),
	("LIGHT_PROBE","Lightprobe",""),
	("LINESTYLE","Linestyle",""),
	("MASK","Mask",""),
	("MATERIAL","Material",""),
	("MESH","Mesh",""),
	("META","Meta",""),
	("MOVIECLIP","Movieclip",""),
	("NODETREE","Nodetree",""),
	("OBJECT","Object",""),
	("PAINTCURVE","Paintcurve",""),
	("PALETTE","Palette",""),
	("PARTICLE","Particle",""),
	("POINTCLOUD","Pointcloud",""),
	("SCENE","Scene",""),
	("SCREEN","Screen",""),
	("SOUND","Sound",""),
	("SPEAKER","Speaker",""),
	("TEXT","Text",""),
	("TEXTURE","Texture",""),
	("VOLUME","Volume",""),
	("WINDOWMANAGER","Windowmanager",""),
	("WORKSPACE","Workspace",""),
	("WORLD","World",""),
)

class BlenderResourceReference(bpy.types.PropertyGroup):
	blender_type: bpy.props.EnumProperty(name="Type", items=blender_type_values) # type: ignore

	action: bpy.props.PointerProperty(type=bpy.types.Action, name="Action") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	brush: bpy.props.PointerProperty(type=bpy.types.Brush, name="Brush") # type: ignore
	camera: bpy.props.PointerProperty(type=bpy.types.Camera, name="Camera") # type: ignore
	collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Collection") # type: ignore
	curve: bpy.props.PointerProperty(type=bpy.types.Curve, name="Curve") # type: ignore
	curves: bpy.props.PointerProperty(type=bpy.types.Curves, name="Curves") # type: ignore
	greasepencil: bpy.props.PointerProperty(type=bpy.types.GreasePencil, name="Greasepencil") # type: ignore
	greasepencil_v3: bpy.props.PointerProperty(type=bpy.types.GreasePencilv3, name="Greasepencil V3") # type: ignore
	image: bpy.props.PointerProperty(type=bpy.types.Image, name="Image") # type: ignore
	key: bpy.props.PointerProperty(type=bpy.types.Key, name="Key") # type: ignore

	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Action, name="Armature") # type: ignore

	scene: bpy.props.PointerProperty(type=bpy.types.Scene, name="Scene") # type: ignore
	object: bpy.props.PointerProperty(type=bpy.types.Object, name="Object") # type: ignore

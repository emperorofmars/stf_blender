import bpy

"""
Blender Resource Reference

Bringing polymorphism to Blender
"""

blender_type_values = (
	("ACTION","Action","","ACTION",0),
	("ARMATURE","Armature","","ARMATURE_DATA",1),
	("BRUSH","Brush","","BRUSH_DATA",2),
	("CAMERA","Camera","","CAMERA_DATA",3),
	("COLLECTION","Collection","","OUTLINER_COLLECTION",4),
	("CURVE","Curve","","CURVE_DATA",5),
	("CURVES","Curves","","CURVES",6),
	("GREASEPENCIL","Greasepencil","","OUTLINER_DATA_GREASEPENCIL",7),
	("GREASEPENCIL_V3","Greasepencil V3","","OUTLINER_DATA_GREASEPENCIL",8),
	("IMAGE","Image","","IMAGE_DATA",9),
	("KEY","Key","Shapekey / Blendshape","SHAPEKEY_DATA",10),
	("LATTICE","Lattice","","LATTICE_DATA",11),
	("LIBRARY","Library","","LIBRARY_DATA_DIRECT",12),
	("LIGHT","Light","","LIGHT_DATA",13),
	("LIGHT_PROBE","Lightprobe","","OUTLINER_DATA_LIGHTPROBE",14),
	("MASK","Mask","","MOD_MASK",15),
	("MATERIAL","Material","","MATERIAL",16),
	("MESH","Mesh","","OUTLINER_DATA_MESH",17),
	("META","Meta","","META_DATA",18),
	("MOVIECLIP","Movieclip","","FILE_MOVIE",19),
	("NODETREE","Nodetree","","NODETREE",20),
	("OBJECT","Object","","OBJECT_DATA",21),
	("PAINTCURVE","Paintcurve","","CURVE_BEZCURVE",22),
	("PALETTE","Palette","","NONE",23),
	("POINTCLOUD","Pointcloud","","POINTCLOUD_DATA",24),
	("SCENE","Scene","","SCENE",25),
	("SCREEN","Screen","","",26),
	("SOUND","Sound","","SOUND",27),
	("SPEAKER","Speaker","","SPEAKER",28),
	("TEXT","Text","","TEXT",29),
	("TEXTURE","Texture","","TEXTURE",30),
	("VOLUME","Volume","","VOLUME_DATA",31),
	("WINDOWMANAGER","Windowmanager","","",32),
	("WORKSPACE","Workspace","","WORKSPACE",33),
	("WORLD","World","","WORLD",34),
)


class BlenderResourceReference(bpy.types.PropertyGroup):
	blender_type: bpy.props.EnumProperty(name="Type", items=blender_type_values) # type: ignore

	action: bpy.props.PointerProperty(type=bpy.types.Action, name="Action") # type: ignore
	armature: bpy.props.PointerProperty(type=bpy.types.Armature, name="Armature") # type: ignore
	brush: bpy.props.PointerProperty(type=bpy.types.Brush, name="Brush") # type: ignore
	camera: bpy.props.PointerProperty(type=bpy.types.Camera, name="Camera") # type: ignore
	collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Collection") # type: ignore
	curve: bpy.props.PointerProperty(type=bpy.types.Curve, name="Curve") # type: ignore
	curves: bpy.props.PointerProperty(type=bpy.types.Curves, name="Curves") # type: ignore
	greasepencil: bpy.props.PointerProperty(type=bpy.types.GreasePencil, name="Greasepencil") # type: ignore
	greasepencil_v3: bpy.props.PointerProperty(type=bpy.types.GreasePencilv3, name="Greasepencil V3") # type: ignore
	image: bpy.props.PointerProperty(type=bpy.types.Image, name="Image") # type: ignore
	key: bpy.props.PointerProperty(type=bpy.types.Key, name="Key") # type: ignore
	lattice: bpy.props.PointerProperty(type=bpy.types.Lattice, name="Lattice") # type: ignore
	library: bpy.props.PointerProperty(type=bpy.types.Library, name="Library") # type: ignore
	light: bpy.props.PointerProperty(type=bpy.types.Light, name="Light") # type: ignore
	light_probe: bpy.props.PointerProperty(type=bpy.types.LightProbe, name="Lightprobe") # type: ignore
	mask: bpy.props.PointerProperty(type=bpy.types.Mask, name="Mask") # type: ignore
	material: bpy.props.PointerProperty(type=bpy.types.Material, name="Material") # type: ignore
	mesh: bpy.props.PointerProperty(type=bpy.types.Mesh, name="Mesh") # type: ignore
	meta: bpy.props.PointerProperty(type=bpy.types.MetaBall, name="Meta") # type: ignore
	movieclip: bpy.props.PointerProperty(type=bpy.types.MovieClip, name="Movieclip") # type: ignore
	nodetree: bpy.props.PointerProperty(type=bpy.types.NodeTree, name="Nodetree") # type: ignore
	object: bpy.props.PointerProperty(type=bpy.types.Object, name="Object") # type: ignore
	paintcurve: bpy.props.PointerProperty(type=bpy.types.PaintCurve, name="Paintcurve") # type: ignore
	palette: bpy.props.PointerProperty(type=bpy.types.Palette, name="Palette") # type: ignore
	pointcloud: bpy.props.PointerProperty(type=bpy.types.PointCloud, name="Pointcloud") # type: ignore
	scene: bpy.props.PointerProperty(type=bpy.types.Scene, name="Scene") # type: ignore
	screen: bpy.props.PointerProperty(type=bpy.types.Screen, name="Screen") # type: ignore
	sound: bpy.props.PointerProperty(type=bpy.types.Sound, name="Sound") # type: ignore
	speaker: bpy.props.PointerProperty(type=bpy.types.Speaker, name="Speaker") # type: ignore
	text: bpy.props.PointerProperty(type=bpy.types.Text, name="Text") # type: ignore
	texture: bpy.props.PointerProperty(type=bpy.types.Texture, name="Texture") # type: ignore
	volume: bpy.props.PointerProperty(type=bpy.types.Volume, name="Volume") # type: ignore
	windowmanager: bpy.props.PointerProperty(type=bpy.types.WindowManager, name="Windowmanager") # type: ignore
	workspace: bpy.props.PointerProperty(type=bpy.types.WorkSpace, name="Workspace") # type: ignore
	world: bpy.props.PointerProperty(type=bpy.types.World, name="World") # type: ignore


def draw_blender_resource_reference(layout: bpy.types.UILayout, brr: BlenderResourceReference):
	layout.prop(brr, "blender_type")
	if(brr.blender_type and hasattr(brr, brr.blender_type.lower())):
		layout.prop(brr, brr.blender_type.lower())

def resolve_blender_resource_reference(brr: BlenderResourceReference) -> bpy.types.ID | None:
	if(brr.blender_type and hasattr(brr, brr.blender_type.lower())):
		return getattr(brr, brr.blender_type.lower())
	return None

def validate_blender_resource_reference(brr: BlenderResourceReference) -> bool:
	return brr and resolve_blender_resource_reference(brr)

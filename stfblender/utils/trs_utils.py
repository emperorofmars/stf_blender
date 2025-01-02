import bpy
import mathutils

def to_trs(t: mathutils.Vector, r: mathutils.Quaternion, s: mathutils.Vector) -> list[list[float]]:
	# TODO actual conversion
	return [
		[t.x, t.y, t.z],
		[r.x, r.y, r.z, r.w],
		[s.x, s.y, s.z]
	]


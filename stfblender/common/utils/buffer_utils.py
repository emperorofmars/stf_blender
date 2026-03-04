from io import BytesIO
import struct


def determine_indices_width(length: int) -> int:
	if(length <= 2**8):
		return 1
	elif(length <= 2**16):
		return 2
	elif(length <= 2**32):
		return 4
	elif(length <= 2**64):
		return 8


def determine_pack_format_int(width: int) -> str:
	if(width <= 1): return "<b"
	elif(width <= 2): return "<h"
	elif(width <= 4): return "<i"
	elif(width <= 8): return "<q"

def determine_pack_format_uint(width: int) -> str:
	if(width <= 1): return "<B"
	elif(width <= 2): return "<H"
	elif(width <= 4): return "<I"
	elif(width <= 8): return "<Q"

def determine_pack_format_float(width: int) -> str:
	#if(width <= 2): return "<e"
	if(width <= 4): return "<f"
	elif(width <= 8): return "<d"


def serialize_int(value: int, width: int = 4) -> bytes:
	return struct.pack(determine_pack_format_int(width), value)

def serialize_uint(value: int, width: int = 4) -> bytes:
	return struct.pack(determine_pack_format_uint(width), value)

def serialize_float(value: float, width: int = 4) -> bytes:
	return struct.pack(determine_pack_format_float(width), value)


def parse_int(buffer: BytesIO, width: int = 4) -> int:
	return struct.unpack(determine_pack_format_int(width), buffer.read(width))[0]

def parse_uint(buffer: BytesIO, width: int = 4) -> int:
	return struct.unpack(determine_pack_format_uint(width), buffer.read(width))[0]

def parse_float(buffer: BytesIO, width: int = 4) -> float:
	return struct.unpack(determine_pack_format_float(width), buffer.read(width))[0]

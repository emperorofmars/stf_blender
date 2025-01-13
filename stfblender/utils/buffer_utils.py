from io import BytesIO
import struct


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
	if(width <= 2): return "<e"
	elif(width <= 4): return "<f"
	elif(width <= 8): return "<d"

def serialize_int(value: int, width: int = 4) -> bytes:
	return struct.pack(determine_pack_format_int(width), value)

def serialize_uint(value: int, width: int = 4) -> bytes:
	return struct.pack(determine_pack_format_uint(width), value)

def serialize_float(value: float, width: int = 4) -> bytes:
	return struct.pack(determine_pack_format_float(width), value)


def parse_int(buffer: BytesIO, width: int = 4) -> int:
	return int.from_bytes(buffer.read(width), byteorder="little", signed=True)

def parse_uint(buffer: BytesIO, width: int = 4) -> int:
	return int.from_bytes(buffer.read(width), byteorder="little", signed=False)

def parse_float(buffer: BytesIO, width: int = 4) -> int:
	return struct.unpack(determine_pack_format_float(width), buffer.read(width))[0]

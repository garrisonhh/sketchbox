import os
import zlib
import struct
import pygame as pg
import math

"""
https://minecraft.gamepedia.com/Region_file_format
"""

REGIONDIR = "/home/garrison/.minecraft/saves/PYTHON/region"

def get_region(x, y):
	f = open(os.path.join(REGIONDIR, "r.%i.%i.mca" % (x, y)), "rb")
	region = f.read()
	f.close()
	return region

def signed(data, start, bytesize):
	return int.from_bytes(data[start:start + bytesize], "big", signed = True)

# returns (payload, byte size)
def next_nbt_item(data, tag, start):
	if tag == 1: # byte
		return int(data[start]), 1
	elif tag == 2: # short
		return signed(data, start, 2), 2
	elif tag == 3: # int/int32
		return signed(data, start, 4), 4
	elif tag == 4: # long/int64
		return signed(data, start, 8), 8
	elif tag == 5: # float/float32
		return struct.unpack('f', data[start:start + 4]), 4 # TODO this feels hacky as fuck, find a cleaner solution maybe?
	elif tag == 6: # double/float64
		return struct.unpack('f', data[start:start + 8]), 8
	elif tag == 7: # ByteArray
		length = signed(data, start, 4)
		return data[start + 4:start + 4 + length], 4 + length
	elif tag == 8: # string
		length = int.from_bytes(data[start:start + 2], "big", signed = False)
		return data[start + 2:start + 2 + length].decode(), 2 + length
	elif tag == 9: # List
		list_tag = int(data[start])
		length = signed(data, start + 1, 4)
		nbt_list = []
		item_start = start + 5
		for i in range(length):
			item = size = None
			if list_tag == 10:
				item, item_end = nbt_compound(data, item_start)
				size = item_end - item_start + 1
			else:
				item, size = next_nbt_item(data, list_tag, item_start)
			nbt_list.append(item)
			item_start += size
		return nbt_list, item_start - start
	elif tag == 10: # Compound
		raise Exception("attempted to parse compound tag in next_nbt_item")
	elif tag == 11: # Int_Array
		length = signed(data, start, 4)
		return [signed(data, start + 4 * (i + 1), 4) for i in range(length)], 4 * (length + 1)
	elif tag == 12: # Long_Array
		length = signed(data, start, 4)
		return [signed(data, start + 4 + i * 8, 8) for i in range(length)], 4 + length * 8 

def nbt_compound(data, index):
	tree = {}
	while index < len(data) and (tag := data[index]):
		namelen = int.from_bytes(data[index + 1:index + 3], "big")
		name = data[index + 3:index + 3 + namelen].decode()
		if tag == 10: # compound
			tree[name], index = nbt_compound(data, index + 3 + namelen)
			index += 1
		else:
			tree[name], size = next_nbt_item(data, tag, index + 3 + namelen)
			index += 3 + namelen + size

	return tree, index

def nbt_tree_from(data):
	return nbt_compound(data, 3)[0] # 3 bytes to skip root NBT_Compound tag

def main():
	region = get_region(0, 0)
	ch_loc = region[:4096] # chunk locations
	ch_time = region[4096:8192] # last update of chunks
	decompressor = zlib.decompressobj()
	chunks = []

	for z in range(16):
		for x in range(16):
			# header data
			offset = 4 * ((x & 31) + (z & 31) * 32) # byte offset of chunk data in header
			loc = 4096 * int.from_bytes(ch_loc[offset:offset + 3], "big")
			sectors = int(ch_loc[offset + 3])

			# nbt data
			length = int.from_bytes(region[loc:loc + 4], "big")
			data = decompressor.decompress(region[loc + 5:loc + 4 + length])
			
			chunks.append(nbt_tree_from(data))

	"""
	TEST RENDER
	"""
	sections = chunks[0]["Level"]["Sections"]
	val = math.sin(math.pi / 4)
	to_iso = lambda x, y, z: ((x - z) * val, (x + z - y) * val)

	pg.init()
	screen = pg.display.set_mode((800, 600))

	for section in sections:
		if section['Y'] != 0:
			continue
		
		pal = [(0, 0, 0), (50, 50, 50), (200, 200, 200)]
		blockstates = section['BlockStates']

		for y in range(16):
			for z in range(16):
				for x in range(16):
					nibble = (blockstates[y * 16 + z] >> x * 4) & 0xF
					if nibble:
						cube = []
						for by in (0, 1):
							for bz in (0, 1):
								for bx in (0, 1):
									sx, sy = to_iso(x + bx, y + by, z + bz)
									sx *= 20
									sy *= 20
									sx += 400
									sy += 200
									cube.append((sx, sy))

						for face in [[6, 7, 3, 2], [7, 5, 1, 3], [4, 5, 7, 6]]:
							ptlist = [cube[pt] for pt in face]
							pg.draw.polygon(screen, pal[nibble], ptlist)
							pg.draw.polygon(screen, pal[0], ptlist, 3)

	while True:
		for e in pg.event.get():
			if e.type == pg.QUIT:
				pg.quit()
				exit(0)

		pg.display.flip()

if __name__ == "__main__":
	main()


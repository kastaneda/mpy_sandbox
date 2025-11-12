#!/usr/bin/env python3

from PIL import Image
from cfg_grid import *
from cfg_fonts import *
import json
import binascii

def print_vlsb(out_bits):
    for y in range(line_dots_y):
        line = ''
        for c in out_bits:
            if c & 1<<y:
                line += '##'
            else:
                line += '  '
        print(line)

font = {'remap': font_remap, 'glyph': {}}

for font_file in font_files:
    img = Image.open(font_file['filename']).convert('RGB')
    line = 0
    for glyphs in font_file['glyphs']:
        dot_x = 0
        for glyph in glyphs:
            print('Reading glyph ', glyph)
            glyph_bits = b''
            glyph_end = False
            while not glyph_end:
                glyph_bit = 0
                for dot_y in range(line_dots_y):
                    x, y = dot_coord(line, dot_x, dot_y)
                    color = img.getpixel((x, y))
                    hex_color =  '#%02x%02x%02x' % color[:3]
                    if hex_color == color_bg:
                        glyph_end = True
                    elif hex_color == color_off:
                        pass
                    elif hex_color == color_on:
                        glyph_bit |= 1 << dot_y 
                    else:
                        raise ValueError('Wrong color');
                if not glyph_end:
                    glyph_bits += glyph_bit.to_bytes(1)
                dot_x += 1
            print_vlsb(glyph_bits)
            font['glyph'][glyph] = binascii.hexlify(glyph_bits).decode()
        line += 1

with open('font.json', 'w', encoding='utf-8') as file:
    json.dump(font, file, ensure_ascii=False, indent=4)

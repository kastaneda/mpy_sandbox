#!/usr/bin/python3

import sys
import json

try:
    msg = sys.argv[1]
except IndexError:
    msg = 'Hello, world!'

with open('font.json', 'r') as file:
    font = json.load(file)

out = b''
for c in msg:
    try:
        c = font['remap'][c]
    except KeyError:
        pass

    try:
        glyph = font['glyph'][c]
    except KeyError:
        glyph = font['glyph']['▯']

    glyph = bytearray.fromhex(glyph)

    if out:
        left = out[-1]
        right = glyph[0]
        if left&right or (left>>1)&right or left&(right>>1):
            out += b'\x00' + glyph
        else:
            out += glyph
    else:
        out = glyph

for y in range(8):
    line = ''
    for c in out:
        if c & 1<<y:
            line += '##'
        else:
            line += '  '
    print(line)

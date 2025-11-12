#!/usr/bin/env python3

from PIL import Image, ImageDraw
from config import *

dot_full_size = dot_size + dot_gap
line_width = dot_full_size * line_dots_x
line_height = dot_full_size * line_dots_y
lines_height = line_height*lines + line_gap*(lines-1)
img_width = img_padding*2 + line_width
img_height = img_padding*2 + lines_height

img = Image.new('RGB', (img_width, img_height), color_bg)
draw = ImageDraw.Draw(img)

for line in range(lines):
    line_start_x = img_padding
    line_start_y = img_padding + (line_height+line_gap)*line
    for dot_x in range(line_dots_x):
        x1 = line_start_x + dot_full_size*dot_x
        x2 = x1 + dot_size - 1
        for dot_y in range(line_dots_y):
            y1 = line_start_y + dot_full_size*dot_y
            y2 = y1 + dot_size - 1
            color = color_off
            if line == 0 and dot_x == 0 and dot_y == 0:
                color = color_on
            draw.rectangle([x1, y1, x2, y2], fill=color)

img.save('template.png', 'PNG')

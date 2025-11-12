#!/usr/bin/env python3

from PIL import Image, ImageDraw
from cfg_grid import *

img = Image.new('RGB', (img_width, img_height), color_bg)
draw = ImageDraw.Draw(img)

for line in range(lines):
    for dot_x in range(line_dots_x):
        for dot_y in range(line_dots_y):
            x1, y1 = dot_coord(line, dot_x, dot_y)
            x2, y2 = x1+dot_size-1, y1+dot_size-1
            color = color_off
            if line == 0 and dot_x == 0 and dot_y == 0:
                color = color_on
            draw.rectangle([x1, y1, x2, y2], fill=color)

img.save('template.png', 'PNG')

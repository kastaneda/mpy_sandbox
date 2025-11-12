#!/usr/bin/env python3

from PIL import Image
from config import *

img = Image.open('font.png').convert('RGB')
hex_color =  '#%02x%02x%02x' % img.getpixel((28, 20))[:3]
print(hex_color)

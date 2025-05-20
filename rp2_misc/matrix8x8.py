from machine import Pin
import neopixel
import time
import random
import colorsys

pin = Pin(14, Pin.OUT)
num_leds = 64
np = neopixel.NeoPixel(pin, num_leds)
dots = [(0,(0,0,0)) for i in range(13)]

try:
    while True:
        time.sleep(0.05 + random.random()**3 / 4)
        # a random pixel
        dot_addr = random.randrange(len(np))
        rgb = colorsys.hsv_to_rgb(random.random(), 1, random.uniform(.01, .04))
        rgb_int = [int(color*255) for color in rgb]
        dot = (dot_addr, rgb_int)
        dots = dots[1:] + [dot]
        print(dot)
        # update
        for i in range(len(np)):
            np[i] = (0, 0, 0)
        for dot in dots:
            np[dot[0]] = dot[1]
        np.write()
except KeyboardInterrupt:
    # clear
    for i in range(len(np)):
        np[i] = (0, 0, 0)
    np.write()

from machine import Pin
import neopixel
import time
import random

pin = Pin(14, Pin.OUT)
num_leds = 64
np = neopixel.NeoPixel(pin, num_leds)
dots = [(0,(0,0,0)) for i in range(12)]

try:
    while True:
        time.sleep(0.05)
        # a random pixel
        dot_addr = random.randrange(len(np))
        dot_r = random.randrange(45)
        dot_g = random.randrange(20)
        dot_b = random.randrange(80)
        dot = (dot_addr, (dot_r, dot_g, dot_b))
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

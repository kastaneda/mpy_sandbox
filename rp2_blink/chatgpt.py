# Importing required modules
from machine import Pin
import neopixel
import time

# Configure the NeoPixel pin and number of LEDs
pin = Pin(15, Pin.OUT)  # Change pin number as per your wiring
num_leds = 1            # Number of LEDs connected

# Initialize the NeoPixel strip
np = neopixel.NeoPixel(pin, num_leds)

# Function to set the NeoPixel to a specific color
def set_color(r, g, b):
    np[0] = (r, g, b)  # Set the first LED (use np[i] for more LEDs)
    np.write()

# Function to generate colors from the color wheel
def color_wheel(pos):
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

# Blinking loop
try:
    while True:
        for i in range(256):  # Iterate through the color wheel
            color = color_wheel(i)
            set_color(*color)
            time.sleep(0.05)  # Short delay to create a smooth transition
except KeyboardInterrupt:
    set_color(0, 0, 0)        # Turn off on exit

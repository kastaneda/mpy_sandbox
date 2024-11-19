import machine, time, neopixel

# RP2040-Zero with single onboard WS2812
pixel = neopixel.NeoPixel(machine.Pin(16), 1)

def gradient(r, g, b, d, dr, dg, db):
    for i in range(d):
        pixel[0] = (r + i*dr, g + i*dg, b + i*db)
        pixel.write()
        time.sleep_ms(5)

try:
    while True:
        gradient(63, 0, 0, 64, -1, 1, 0)
        gradient(0, 64, 0, 64, 0, -1, 1)
        gradient(0, 0, 63, 64, 1, 0, -1)
except KeyboardInterrupt:
    pixel[0] = (0, 0, 0)
    pixel.write()

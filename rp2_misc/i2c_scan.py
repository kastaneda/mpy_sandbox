from machine import Pin, I2C

i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400_000)

devices = i2c.scan()

if devices:
    for d in devices:
        print(hex(d))

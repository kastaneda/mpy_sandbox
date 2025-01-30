# https://github.com/kapetan/MicroPython_VL53L0X

from machine import Pin, I2C
import time
import vl53l0x

# Initialize I2C bus and sensor.
i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400_000)
vl53 = vl53l0x.VL53L0X(i2c)

# Optionally set the timing budget. A timing budget of 20 milliseconds
# results in faster but less accurate measurements.
# For more accuracy set the timing budget to 200 milliseconds.
# The default is around 33 milliseconds.
vl53.measurement_timing_budget = 20000 # microseconds

# Optionally start continuous measurement mode.
vl53.start_continuous()

while True:
    print("Range: {0}mm".format(vl53.range))
    time.sleep(1)


# https://github.com/chrisb2/pyb_ina219

from ina219 import INA219
from machine import Pin, I2C

i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400_000)

SHUNT_OHMS = 100  # Check value of shunt used with your INA219

ina = INA219(SHUNT_OHMS, i2c)
ina.configure()
print("Bus Voltage: %.3f V" % ina.voltage())
print("Current: %.3f mA" % ina.current())
print("Power: %.3f mW" % ina.power())

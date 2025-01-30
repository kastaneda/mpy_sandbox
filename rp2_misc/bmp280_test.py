from machine import Pin, I2C
from bmp280 import *

i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400_000)

bmp = BMP280(i2c)
bmp.use_case(BMP280_CASE_WEATHER)
bmp.oversample(BMP280_OS_HIGH)
bmp.temp_os = BMP280_TEMP_OS_8
bmp.press_os = BMP280_PRES_OS_4
bmp.iir = BMP280_IIR_FILTER_2

bmp.force_measure()
result = { 'temperature': bmp.temperature, 'pressure': bmp.pressure }

print(result)

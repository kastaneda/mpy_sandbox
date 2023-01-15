import math
from machine import ADC, Pin

class VoltageDivider:
    serialR = 10000         # Voltage divider resistor (10K Ohm)
    def getResistance(self, adc_u16):
        return self.serialR / (65535 / adc_u16 - 1)

class ThermistorNTC:
    NTC_beta = 3950         # Thermistor (NTC) beta coefficient
    nominalR = 10000        # Thermistor nominal resistance (10K Ohm)
    nominalT = 25           # Thermistor nominal temperature (25 C)
    def getTemp(self, resistance):
        r_r0 = resistance / self.nominalR
        steinhart = math.log(r_r0) / self.NTC_beta
        inv_t0 = 1 / (self.nominalT + 273.15)
        return 1 / (steinhart + inv_t0) - 273.15

class ThermalSensor:
    def __init__(self, adc, ctrl):
        self.vd = VoltageDivider()
        self.ntc = ThermistorNTC()
        self.adc = adc
        self.ctrl = ctrl
        ctrl.off()
    def readADC_u16(self):
        self.ctrl.on()
        adc_u16 = self.adc.read_u16()
        self.ctrl.off()
        return adc_u16
    def readResistance(self):
        adc_u16 = self.readADC_u16()
        return self.vd.getResistance(adc_u16)
    def readTemp(self):
        return self.ntc.getTemp(self.readResistance())

sensor1 = ThermalSensor(ADC(Pin(26, Pin.IN)), Pin(20, Pin.OUT))
sensor1.vd.serialR = 10426
sensor1.ntc.nominalR = 10350
print(sensor1.readTemp())

sensor2 = ThermalSensor(ADC(Pin(27, Pin.IN)), Pin(21, Pin.OUT))
sensor2.vd.serialR = 9950
sensor2.ntc.nominalR = 9400
print(sensor2.readTemp())

def test(num=10000):
    avg = 0
    for x in range(num):
        t1=sensor1.readTemp()
        t2=sensor2.readTemp()
        d=(t2-t1)/t1
        avg+=d
    return avg

# from test import *
# sensor1.readTemp(); sensor2.readTemp()


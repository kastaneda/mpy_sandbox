import machine

# WeMos board: D7 (GPIO13), SPI MOSI
# 74HC595: DS (Serial data input)
dataPin = machine.Pin(13, machine.Pin.OUT)

# WeMos board: D5 (GPIO14), SPI SCLK
# 74HC595: SH_CP (Shift register clock pin)
clockPin = machine.Pin(14, machine.Pin.OUT)

# WeMos board: D8 (GPIO15), SPI CS
# 74HC595: ST_CP (Storage register clock pin)
latchPin = machine.Pin(15, machine.Pin.OUT)

# Can I use hardware SPI? Yes.
#spi = machine.SPI(1, baudrate=80000000, polarity=1, phase=0)
# Beware: if I define the hardware SPI, I will be not able to use bitbang version

# Or I can use SoftSPI
# Dunno why I cannot just say miso=None there
spi = machine.SoftSPI(baudrate=100000, polarity=0, phase=0, sck=clockPin, mosi=dataPin, miso=machine.Pin(12))

def write74HC595_spi(data, num_bits=8):
    spi.write(data.to_bytes(num_bits >> 3, 'big'))
    latchPin.value(1)
    latchPin.value(0)

def write74HC595_bitbang(data, num_bits=8):
    for i in range(num_bits-1, -1, -1):
        dataPin.value((data >> i) & 1)
        clockPin.value(1)
        clockPin.value(0)
    latchPin.value(1)
    latchPin.value(0)


write74HC595 = write74HC595_spi

#def write74HC595_test(data, num_bits=16):
#    # default format_spec is '016b'
#    print(format(data, '0%db' % num_bits))

# write74HC595 = write74HC595_test

# NameError: name 'format' isn't defined
# MicroPython v1.23.0 on 2024-06-02; ESP module with ESP8266

# On start, set all that to zeroes
clockPin.value(0)
latchPin.value(0)
write74HC595(0, 16)


import machine, time

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
# Beware: if I use hardware SPI, I will be not able to use bitbang version
#spi = machine.SPI(1, baudrate=80000000, polarity=1, phase=0)

# Damn, I cannot just say miso=None there :(
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

# Just to test hardware SPI, software SPI and my bit-bang versions works equally
def write74HC595(data, num_bits=8):
    write74HC595_spi(data, num_bits)
    #write74HC595_bitbang(data, num_bits)

def hello(iterations=10):
    for j in range(iterations):
        for i in range(15, -1, -1):
            write74HC595(0b00000000000000001111111111111111 >> i, 16)
            time.sleep_ms(100)
        for i in range(15, -1, -1):
            write74HC595(0b11111111111111110000000000000000 >> i, 16)
            time.sleep_ms(100)
    write74HC595(0, 16)

def hello2(iterations=10):
    for j in range(iterations):
        for i in range(16):
            print(1 << i)
            write74HC595(1 << i, 16)
            time.sleep_ms(100)
        for i in range(15, -1, -1):
            print(1 << i)
            write74HC595(1 << i, 16)
            time.sleep_ms(100)
    write74HC595(0, 16)

# hello()
clockPin.value(0)
latchPin.value(0)
write74HC595(0, 16)


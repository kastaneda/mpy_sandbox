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

spi = machine.SPI(1, baudrate=20000000, polarity=0, phase=0)
#spi = machine.SoftSPI(baudrate=100000, polarity=0, phase=0, sck=clockPin, mosi=dataPin, miso=machine.Pin(12))

def write74HC595_spi(data, num_bits=8):
    spi.write(data.to_bytes(num_bits >> 3, 'big'))
    latchPin.value(1)
    latchPin.value(0)

def write74HC595_bitbang(data, num_bits=8):
    for i in range(num_bits-1, -1, -1):
        print((data >> i) & 1, end='')
        dataPin.value((data >> i) & 1)
        clockPin.value(1)
        clockPin.value(0)
    latchPin.value(1)
    latchPin.value(0)
    print('')

write74HC595 = write74HC595_spi

clockPin.value(0)
latchPin.value(0)
write74HC595(0, 16)

class MyStepper:
    outputBits = 0
    stepActual = 0
    stepTarget = 0
    _delta = 0
    def __init__(self, stepBitMask):
        assert len(stepBitMask) == 4
        self.stepBitMask = stepBitMask
    def target(self, target):
        self.stepTarget = target
        self._delta = 1 if self.stepActual < self.stepTarget else -1
    def update(self):
        if (self.stepActual == self.stepTarget):
            self.outputBits = 0
            return
        if (self.outputBits):
            self.stepActual += self._delta
        self.outputBits = self.stepBitMask[self.stepActual & 3]

# my 2x SN74HC595 + 2x ULN2003AN scheme, version 4c:
#
#  bit: 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
# coil: C4 C3 C2 C1 -- B4 B3 -- B2 B1 -- A4 A3 A2 A1 --

motor1 = MyStepper([ 0b1100 << 1, 0b0110 << 1, 0b0011 << 1, 0b1001 << 1 ])
motor2 = MyStepper([ 0b11000 << 6, 0b01010 << 6, 0b00011 << 6, 0b10001 << 6 ])
motor3 = MyStepper([ 0b1100 << 12, 0b0110 << 12, 0b0011 << 12, 0b1001 << 12 ])

def oneStep():
    motor1.update()
    motor2.update()
    motor3.update()
    bitmask = motor1.outputBits | motor2.outputBits | motor3.outputBits
    write74HC595(bitmask, 16)

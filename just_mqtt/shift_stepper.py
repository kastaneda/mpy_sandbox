import machine

# WeMos board: D7 (GPIO13), SPI MOSI
# 74HC595: DS (Serial data input)
data_pin = machine.Pin(13, machine.Pin.OUT)

# WeMos board: D5 (GPIO14), SPI SCLK
# 74HC595: SH_CP (Shift register clock pin)
clock_pin = machine.Pin(14, machine.Pin.OUT)

# WeMos board: D8 (GPIO15), SPI CS
# 74HC595: ST_CP (Storage register clock pin)
latch_pin = machine.Pin(15, machine.Pin.OUT)

spi = machine.SPI(1, baudrate=20000000, polarity=0, phase=0)
#spi = machine.SoftSPI(baudrate=100000, polarity=0, phase=0, sck=clock_pin, mosi=data_pin, miso=machine.Pin(12))

def write74HC595_spi(data, num_bits=8):
    spi.write(data.to_bytes(num_bits >> 3, 'big'))
    latch_pin.value(1)
    latch_pin.value(0)

def write74HC595_bitbang(data, num_bits=8):
    for i in range(num_bits-1, -1, -1):
        print((data >> i) & 1, end='')
        data_pin.value((data >> i) & 1)
        clock_pin.value(1)
        clock_pin.value(0)
    latch_pin.value(1)
    latch_pin.value(0)
    print('')

write74HC595 = write74HC595_spi

clock_pin.value(0)
latch_pin.value(0)
write74HC595(0, 16)

class MyStepper:
    output = 0
    step_actual = 0
    step_target = 0
    _delta = 0

    def __init__(self, step_bitmask):
        assert len(step_bitmask) == 4
        self._step_bitmask = step_bitmask

    def target(self, target):
        self.step_target = int(target)
        self._delta = 1 if self.step_actual < self.step_target else -1

    def update(self):
        if (self.step_actual == self.step_target):
            self.output = 0
            return
        if (self.output):
            self.step_actual += self._delta
        self.output = self._step_bitmask[self.step_actual & 3]

# my 2x SN74HC595 + 2x ULN2003AN scheme, version 4c:
#
#  bit: 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
# coil: C4 C3 C2 C1 -- B4 B3 -- B2 B1 -- A4 A3 A2 A1 --

motor1 = MyStepper([ 0b1100 << 1, 0b0110 << 1, 0b0011 << 1, 0b1001 << 1 ])
motor2 = MyStepper([ 0b11000 << 6, 0b01010 << 6, 0b00011 << 6, 0b10001 << 6 ])
motor3 = MyStepper([ 0b1100 << 12, 0b0110 << 12, 0b0011 << 12, 0b1001 << 12 ])

def load_position(position):
    try:
        motor1.step_actual = position['motor1_actual']
        motor2.step_actual = position['motor2_actual']
        motor3.step_actual = position['motor3_actual']
    except (KeyError, TypeError):
        pass

def save_position():
    return {
        'motor1_actual': motor1.step_actual,
        'motor2_actual': motor2.step_actual,
        'motor3_actual': motor3.step_actual
    }

def set_direction(dir_config):
    if dir_config.get('motor1'):
        motor1._step_bitmask.reverse()
    if dir_config.get('motor2'):
        motor2._step_bitmask.reverse()
    if dir_config.get('motor3'):
        motor3._step_bitmask.reverse()

def one_step():
    motor1.update()
    motor2.update()
    motor3.update()
    bitmask = motor1.output | motor2.output | motor3.output
    write74HC595(bitmask, 16)

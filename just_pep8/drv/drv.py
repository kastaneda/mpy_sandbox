import machine

def write74HC595(data, num_bytes=2):
    spi.write(data.to_bytes(num_bytes, 'big'))
    latch.value(1)
    latch.value(0)

class MyStepper:
    actual = 0
    target = 0
    output = 0
    _delta = 0

    def __init__(self, step_bitmask):
        assert len(step_bitmask) == 4
        self._step_bitmask = step_bitmask

    def go(self, new_target):
        self.target = int(new_target)
        self._delta = 1 if self.actual < self.target else -1

    def up(self):
        if (self.actual == self.target):
            self.output = 0
            return
        if (self.output):
            self.actual += self._delta
        self.output = self._step_bitmask[self.actual & 3]

def init():
    global latch, spi, m1, m2, m3, tim
    latch = machine.Pin(15, machine.Pin.OUT)
    spi = machine.SPI(1, baudrate=20000000, polarity=0, phase=0)
    write74HC595(0, 2)

    m1 = MyStepper([0b1100 << 1, 0b0110 << 1, 0b0011 << 1, 0b1001 << 1])
    m2 = MyStepper([0b11000 << 6, 0b01010 << 6, 0b00011 << 6, 0b10001 << 6])
    m3 = MyStepper([0b1100 << 12, 0b0110 << 12, 0b0011 << 12, 0b1001 << 12])

    tim = machine.Timer(-1)
    tim.init(
        callback=one_step,
        freq=400,
        mode=machine.Timer.PERIODIC)

def one_step(t=None):
    m1.up()
    m2.up()
    m3.up()
    write74HC595(m1.output | m2.output | m3.output, 2)

def deinit():
    tim.deinit()


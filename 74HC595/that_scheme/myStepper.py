from myShiftRegister import write74HC595

class MyStepper:
    outputBits = 0                  # part of 74HC595 output
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
            self.outputBits = 0     # turn the coils off after last step
            return

        if (self.outputBits):       # if the coils is already turned on
            self.stepActual += self._delta
        # else: turn on the coils at last position, wait one step cycle

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


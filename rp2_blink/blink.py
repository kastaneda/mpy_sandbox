import machine, time, rp2

print('Hello world!')
print('Press Ctrl-C to stop the loop')

led = machine.Pin(25, machine.Pin.OUT)

sequenceNumber = buttonPrev = -1
allSequences = [
    [0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 0, 1, 1],
    [0, 1],
    [0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
]

while True:
    buttonNow = rp2.bootsel_button()
    if buttonNow > buttonPrev:
        sequenceNumber = (sequenceNumber + 1) % len(allSequences)
        sequence = allSequences[sequenceNumber]
        stepInSequence = 0
        print('Sequence number', sequenceNumber, ' value =', sequence)
    buttonPrev = buttonNow 

    led.value(sequence[stepInSequence])
    time.sleep_ms(100)
    stepInSequence = (stepInSequence + 1) % len(sequence)

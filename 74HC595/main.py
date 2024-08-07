import test, time

#test.hello2(1)
#test.hello(1)
#test.hello2(1)

test.write74HC595(0b1111, 16)

# Full-step
step_mask = [ 0b1100, 0b0110, 0b0011, 0b1001 ]

# Wave drive
#step_mask = [ 0b1000, 0b0100, 0b0010, 0b0001 ]
#step_mask = [ 0b0111, 0b1011, 0b1101, 0b1110 ]

def set_stepper(bitmask):
    test.write74HC595(bitmask << 1, 16)

def stepper(steps = 1024):
    for i in range(steps):
        #print(step_mask[i % 4])
        set_stepper(step_mask[i % 4])
        time.sleep_ms(2)
    set_stepper(0b1111)

stepper(256)

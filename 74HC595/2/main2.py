import test, time

test.write74HC595(0b1111, 16)

# Full-step
# Motors 1 and 3
#step_mask = [ 0b1100, 0b0110, 0b0011, 0b1001 ]

# Motor 2
step_mask = [ 0b110000, 0b010010, 0b000011, 0b100001 ]

# Wave drive
#step_mask = [ 0b1000, 0b0100, 0b0010, 0b0001 ]
#step_mask = [ 0b0111, 0b1011, 0b1101, 0b1110 ]

def set_stepper(bitmask):
    # Motor 1
    #test.write74HC595(bitmask << 1, 16)
    # Motor 2
    test.write74HC595(bitmask << 6, 16)
    # Motor 3
    #test.write74HC595(bitmask << 11, 16)

def stepper(steps = 1024):
    for i in range(steps):
        #print(step_mask[i % 4])
        set_stepper(step_mask[i % 4])
        time.sleep_ms(2)
    set_stepper(0)

stepper(512)


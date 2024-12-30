def m1_invert():
    mask = list(drv.m1._bitmask)
    mask.reverse()
    drv.m1._bitmask = tuple(mask)

# sg90 = machine.PWM(machine.Pin(0, mode=machine.Pin.OUT))

# sg90.init(freq=50, duty_u16=u16)
# sg90.deinit()

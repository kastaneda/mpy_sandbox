from machine import Pin, I2C
import ssd1306
import time

#i2c = I2C(sda=Pin(8), scl=Pin(9))
i2c = I2C(0)
disp = ssd1306.SSD1306_I2C(128, 32, i2c)
disp.contrast(0)

last_msg = ''
def msg(s):
    global disp, last_msg
    if s != last_msg:
        disp.fill(0)
        y=0
        for l in s.split('\n'):
            disp.text(l, 0, y, 1)
            y += 8
        disp.show()
        last_msg = s

def read_cap_pin():
    p = Pin(3, Pin.IN, Pin.PULL_DOWN)
    time.sleep_ms(5)
    p = Pin(3, Pin.IN)
    t0 = time.ticks_us()
    dt = -1
    while not p.value():
        t1 = time.ticks_us()
        dt = time.ticks_diff(t1, t0)
        if dt > 10000:
            p = Pin(3, Pin.OUT, value=0)
            return False
    p = Pin(3, Pin.OUT, value=0)
    return dt

while True:
    reading = read_cap_pin()
    if not reading:
        msg('-')
    else:
        msg('+\n\ndt = ' + str(reading / 1000) + ' ms')
    #time.sleep_ms(50)


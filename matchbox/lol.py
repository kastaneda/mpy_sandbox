import machine
import time
import ssd1306

try:
    ssd_gnd = machine.Pin(0, machine.Pin.OPEN_DRAIN, value=0)
    ssd_vcc = machine.Pin(1, machine.Pin.OUT, value=1)
    i2c = machine.SoftI2C(scl=machine.Pin(2) , sda=machine.Pin(3))
    disp = ssd1306.SSD1306_I2C(128, 32, i2c)
    disp.contrast(0)
    disp.text('Hello, World!', 0, 0, 1)
    disp.text('wake_reason = ' + str(machine.wake_reason()), 0, 8, 1)
    disp.show()

    rtc = machine.RTC()
    mem = rtc.memory().decode()
    disp.text('RTC memory = ' + mem, 0, 16, 1)
    disp.show()

    try:
        mem = str(int(mem) + 1)
    except ValueError:
        mem = '1'

    rtc.memory(mem.encode())
    disp.text('New RTC mem = ' + mem, 0, 24, 1)
    disp.show()
except Exception:
    pass

led = machine.Pin(8, machine.Pin.OUT)

for i in range(20):
    led.toggle()
    time.sleep_ms(500)

# pin_D2 = machine.Pin(4, machine.Pin.IN)
# esp32.wake_on_ext0(pin_D2, esp32.WAKEUP_ANY_HIGH)

machine.deepsleep(10000)

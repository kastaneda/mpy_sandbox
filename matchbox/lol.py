import machine
import time
import ssd1306
import esp32

pin_D2 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_DOWN)

try:
    i2c = machine.SoftI2C(scl=machine.Pin(0), sda=machine.Pin(1))
    disp = ssd1306.SSD1306_I2C(128, 32, i2c)
    disp.contrast(0)
    disp.fill(0)
    disp.text('Hello, World!', 0, 0, 1)
    disp.text('wake_reason = ' + str(machine.wake_reason()), 0, 8, 1)
    disp.show()

    def my_invert(pin):
        disp.invert(pin.value())

    pin_D2.irq(
        trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING,
        handler=my_invert)

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

# https://github.com/micropython/micropython/pull/17518

esp32.wake_on_gpio([pin_D2], esp32.WAKEUP_ANY_HIGH)

machine.deepsleep(10000)

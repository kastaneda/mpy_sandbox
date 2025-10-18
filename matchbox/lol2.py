import machine
import time
import esp32

# built-in LED on ESP32-C3 "Super Mini"
led = machine.Pin(8, machine.Pin.OUT)

# GPIO4 <-----> button <-----> R 10K <-----> 3V3
btn = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_DOWN)

for i in range(10):
    led.toggle()
    time.sleep_ms(500)

# https://github.com/micropython/micropython/pull/17518
esp32.wake_on_gpio([btn], esp32.WAKEUP_ANY_HIGH)

machine.deepsleep(10000)

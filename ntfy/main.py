import machine
import time
import network
import urequests

t0 = time.ticks_ms()

cfg_essid = '...'
cfg_password = '...'
cfg_endpoint = 'http://192.168.0.82/ding.php?from=Some+special+name'

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(cfg_essid, cfg_password)

# GPIO 2 == pin D4 == built-in LED
# the LED is inverted, HIGH = no light, LOW = bright blue
led = machine.Pin(2, machine.Pin.OUT)
led.value(1)

# wait for network, blink while wait
while not sta_if.isconnected():
    led.value(0)
    time.sleep_ms(50)
    led.value(1)
    time.sleep_ms(50)

t1 = time.ticks_ms()
print('Connected in', t1 - t0, 'ms')

print(urequests.get(cfg_endpoint).content)

print('Going to deep sleep in 5 seconds...')
time.sleep(5)

print('Sweet dreams')
machine.deepsleep()

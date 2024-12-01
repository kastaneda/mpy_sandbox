import time
import machine
import ssd1306
import network
import urequests

cfg_essid = '...'
cfg_password = '...'
cfg_endpoint = 'http://192.168.0.34/hello_ssd1306.php'

i2c = machine.I2C(sda=machine.Pin(4), scl=machine.Pin(5))

disp = ssd1306.SSD1306_I2C(128, 32, i2c)
disp.contrast(0)

def msg(s):
    disp.fill(0)
    y = 0
    for line in s.split('\n'):
        disp.text(line, 0, y, 1)
        y += 8
    disp.show()

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(cfg_essid, cfg_password)

c = 0
while not sta_if.isconnected():
    c = (c + 1) % 4
    msg('Connecting\n' + ('.' * c))
    time.sleep_ms(100)

msg('Connected\nLoading...')

msg(urequests.get(cfg_endpoint).content.decode('ascii'))

time.sleep(5) # Chance to press Ctrl-C in REPL
machine.deepsleep()

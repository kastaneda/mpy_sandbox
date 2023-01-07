import machine
import network
import time
import urequests
from bmp280 import *
import config

def wifi_setup():
    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.scan()
    sta_if.connect(config.wifi_essid, config.wifi_password)

def wifi_wait_connect(timeout_ms=2500):
    while timeout_ms:
        if (sta_if.isconnected()):
            return True
        time.sleep_ms(250)
        timeout_ms = timeout_ms - 250
    return sta_if.isconnected()

def i2c_setup():
    global i2c
    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))

def bmp_setup():
    global bmp
    bmp = BMP280(i2c)
    bmp.use_case(BMP280_CASE_WEATHER)
    bmp.oversample(BMP280_OS_HIGH)
    bmp.temp_os = BMP280_TEMP_OS_8
    bmp.press_os = BMP280_PRES_OS_4
    bmp.iir = BMP280_IIR_FILTER_2

def bmp_measure():
    bmp.force_measure()
    result = { 'temperature': bmp.temperature, 'pressure': bmp.pressure }
    bmp.sleep()
    return result

def send_measurements(bmp_data):
    bmp_data['station'] = config.station_id
    response = urequests.post(config.endpoint_url, json=bmp_data)
    return response.status_code

def setup_rtc_alarm(timeout_ms=60000):
    global rtc
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, timeout_ms)

def go_deepsleep():
    machine.deepsleep()

def main_main():
    d4.value(0) # Turn LED on
    wifi_setup()
    if wifi_wait_connect():
        i2c_setup()
        bmp_setup()
        send_measurements(bmp_measure())
    else:
        if devMode:
            print('[devMode] Error: cannot connect to Wi-Fi')
    d4.value(1) # Turn LED off

# D4 / GPIO2 / LED
d4 = machine.Pin(2, machine.Pin.OUT)

# D5 / GPIO14
d5 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

# value 1 == pin D5 not connected, use it for development mode
# value 0 == pin D5 connected to G, so it's safe to use deep sleep
devMode = (d5.value() != 0)

if devMode:
    print('Pin D5 is not grounded, app in development mode')
    print('[devMode] Not setting RTC alarm')
    main_main()
    print('[devMode] Not going to the deep sleep mode')
else:
    try:
        setup_rtc_alarm()
        main_main()
    except:
        pass
    finally:
        go_deepsleep()

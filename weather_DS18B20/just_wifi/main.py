import config, connect, machine, time, urequests
import onewire, ds18x20
#from bmp280 import *

#def i2c_setup():
#    global i2c
#    i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))

#def bmp_setup():
#    global bmp
#    bmp = BMP280(i2c)
#    bmp.use_case(BMP280_CASE_WEATHER)
#    bmp.oversample(BMP280_OS_HIGH)
#    bmp.temp_os = BMP280_TEMP_OS_8
#    bmp.press_os = BMP280_PRES_OS_4
#    bmp.iir = BMP280_IIR_FILTER_2

#def bmp_measure():
#    bmp.force_measure()
#    result = { 'temperature': bmp.temperature, 'pressure': bmp.pressure }
#    bmp.sleep()
#    return result

def send_measurements(weather_data):
    if weather_data:
        weather_data['station'] = config.board_id
        response = urequests.post(connect.wifi('endpoint'), json=weather_data)
        return response.status_code

def ds18b20_init(ds_pin):
    global ds18b20_sensor, ds18b20_roms
    ds18b20_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
    ds18b20_roms = ds18b20_sensor.scan()

def ds18b20_start_measure():
    global ds18b20_t_start
    ds18b20_sensor.convert_temp()
    ds18b20_t_start = time.ticks_ms()

def ds18b20_measure():
    global ds18b20_t_start
    if ds18b20_roms:
        try:
            ds18b20_t_start
        except NameError:
            ds18b20_start_measure()
        delta_t = time.ticks_diff(time.ticks_ms(), ds18b20_t_start)
        if (delta_t < 750):
            time.sleep_ms(750 - delta_t)
        temp = ds18b20_sensor.read_temp(ds18b20_roms[0])
        result = { 'temperature': temp }
        return result
    else:
        return False

def main_main():
    d4.value(0) # Turn LED on
    ds18b20_init(d6)
    ds18b20_start_measure()
    connect.loadRTC()
    connect.setupWifi()
    if connect.connected():
        #i2c_setup()
        #bmp_setup()
        #send_measurements(bmp_measure())
        send_measurements(ds18b20_measure())
    else:
        if devMode:
            print('[devMode] Error: cannot connect to Wi-Fi')
    d4.value(1) # Turn LED off

# D4 / GPIO2 / LED
d4 = machine.Pin(2, machine.Pin.OUT)

# D5 / GPIO14
d5 = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

# D6 / GPIO12
d6 = machine.Pin(12)

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
        main_main()
    except:
        pass
    finally:
        connect.deepsleep(5 * 60)


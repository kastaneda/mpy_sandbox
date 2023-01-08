import machine, time, onewire, ds18x20

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

d6 = machine.Pin(12)
ds18b20_init(d6)
print(ds18b20_measure())

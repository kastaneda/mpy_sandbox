import machine, time, umqtt.robust, gc, micropython, asyncio
import config, connect, shift_stepper

def topic(suffix):
    return (config.board_id + '/' + suffix).encode('ascii')

connect.loadRTC()
shift_stepper.loadPosition(connect.rtcm.get('motor'))
connect.setupWifi()

# https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/README.rst
# keepalive=1 is VERY small period; for real life it should be >= 5 sec
client = umqtt.robust.MQTTClient(config.board_id, connect.wifi('mqtt'), keepalive=1)
client.set_last_will(topic('status'), b'0')
client.connect()
client.publish(topic('status'), b'1')

vcc = machine.ADC(1)

led = machine.Pin(2, machine.Pin.OUT)
led.value(1)
# The onboard LED is inverted: value(0) means ON, 1 means OFF
# It's more practical to invert it here, on the device's side

def report_led():
    client.publish(topic('led'), str(1-led.value()))

async def led_blink(times):
    for i in range(times):
        led.value(0)
        report_led()
        await asyncio.sleep_ms(250)
        led.value(1)
        report_led()
        await asyncio.sleep_ms(250)

topic_callbacks = {
    topic('led/set'): lambda m: led.value(0 if m == b'1' else 1),
    topic('motor1/set'): shift_stepper.motor1.target,
    topic('motor2/set'): shift_stepper.motor2.target,
    topic('motor3/set'): shift_stepper.motor3.target,
    topic('sleep/set'): connect.deepSleep
}

def mqtt_callback(topicName, msg):
    fn = topic_callbacks.get(topicName, lambda x: None)
    fn(msg)

client.set_callback(mqtt_callback)
client.subscribe(topic('+/set'))

crontab = []
def cron(fn, **kwargs):
    global crontab
    # https://docs.micropython.org/en/latest/reference/isr_rules.html#using-micropython-schedule
    # kwargs['callback'] = lambda t: micropython.schedule(fn, t)
    kwargs['callback'] = fn
    kwargs['mode'] = machine.Timer.PERIODIC
    t = machine.Timer(-1)
    t.init(**kwargs)
    crontab.append(t)

recentReports = {}
recentReportsCount = {}
def reportIfChanged(name, value, factor=100):
    global recentReports, recentReportsCount
    if recentReports.get(name, False) == value:
        count = recentReportsCount.get(name, 0)
        if count < factor:
            recentReportsCount[name] = count+1
            return
    client.publish(topic(name), str(value))
    recentReportsCount[name] = 0
    recentReports[name] = value

async def every100ms():
    while True:
        reportIfChanged('motor1', shift_stepper.motor1.stepActual)
        reportIfChanged('motor2', shift_stepper.motor2.stepActual)
        reportIfChanged('motor3', shift_stepper.motor3.stepActual)
        connect.rtcm.update(motor=shift_stepper.savePosition())
        await asyncio.sleep_ms(100)

async def every1s():
    while True:
        client.ping()
        print('.', end='')
        await asyncio.sleep_ms(1000)

async def every20s():
    while True:
        report_led()
        client.publish(topic('status'), b'1')
        client.publish(topic('vcc'), str(vcc.read()))
        await asyncio.sleep_ms(20_000)

# The one and only task that really must be run on timer
cron(lambda t: shift_stepper.oneStep(), freq=400)

async def mqtt_loop():
    while True:
        client.check_msg()
        await asyncio.sleep_ms(50)

try:
    print('Start MQTT main loop, press Ctrl-C to stop')
    asyncio.create_task(mqtt_loop())
    asyncio.create_task(every100ms())
    asyncio.create_task(every1s())
    asyncio.create_task(every20s())
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    print('\nStopped')
finally:
    client.disconnect()
    asyncio.get_event_loop().stop()
    for t in crontab:
        t.deinit()
    connect.saveRTC()

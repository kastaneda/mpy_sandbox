import machine, time, umqtt.robust, gc, micropython
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
client.publish(topic('led'), str(1-led.value()))

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
    kwargs['callback'] = lambda t: micropython.schedule(fn, t)
    kwargs['mode'] = machine.Timer.PERIODIC
    t = machine.Timer(-1)
    t.init(**kwargs)
    crontab.append(t)

cron(lambda t: client.ping(), period=1000)
cron(lambda t: client.publish(topic('vcc'), str(vcc.read())), period=5000)
# Optional: periodic updates to synchronize device and Node-RED
cron(lambda t: client.publish(topic('status'), b'1'), period=20000)
cron(lambda t: client.publish(topic('led'), str(1-led.value())), period=20000)
# Hmmm, dunno if I really need it
cron(lambda t: gc.collect(), period=600000)
# Debug things
cron(lambda t: print('.', end=''), period=1000)
# The motors
cron(lambda t: shift_stepper.oneStep(), freq=400)
cron(lambda t: client.publish(topic('motor1'), str(shift_stepper.motor1.stepActual)), period=500)
cron(lambda t: client.publish(topic('motor2'), str(shift_stepper.motor2.stepActual)), period=500)
cron(lambda t: client.publish(topic('motor3'), str(shift_stepper.motor3.stepActual)), period=500)
cron(lambda t: connect.rtcm.update(motor=shift_stepper.savePosition()), period=200)

try:
    print('Start MQTT main loop, press Ctrl-C to stop')
    while True:
        client.wait_msg()
except KeyboardInterrupt:
    print('\nStopped')
    for t in crontab:
        t.deinit()
    connect.saveRTC()

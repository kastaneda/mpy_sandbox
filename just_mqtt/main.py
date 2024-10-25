import config, connect, machine, time, umqtt.robust, gc, micropython
from shift_stepper import motor1, motor2, motor3, oneStep

def topic(suffix):
    return (config.board_id + '/' + suffix).encode('ascii')

def motor_fromRTC():
    try:
        position = connect.rtcm['motor']
        motor1.stepActual = position['motor1_actual']
        motor2.stepActual = position['motor2_actual']
        motor3.stepActual = position['motor3_actual']
    except KeyError:
        pass

def motor_toRTC(t):
    connect.rtcm['motor'] = {
        'motor1_actual': motor1.stepActual,
        'motor2_actual': motor2.stepActual,
        'motor3_actual': motor3.stepActual
    }

connect.loadRTC()
motor_fromRTC()

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
    topic('motor1/set'): motor1.target,
    topic('motor2/set'): motor2.target,
    topic('motor3/set'): motor3.target,
    topic('sleep/set'): connect.deepSleep
}

def mqtt_callback(topicName, msg):
    fn = topic_callbacks.get(topicName, lambda x: None)
    fn(msg)

client.set_callback(mqtt_callback)
client.subscribe(topic('+/set'))

# Debug thing: count loops per second
dbg_loop_counter = 0

def dbg_report_loops(t):
    global dbg_loop_counter
    client.publish(topic('lps'), str(dbg_loop_counter))
    dbg_loop_counter = 0

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
cron(lambda t: client.publish(topic('motor1'), str(motor1.stepActual)), period=500)
cron(lambda t: client.publish(topic('motor2'), str(motor2.stepActual)), period=500)
cron(lambda t: client.publish(topic('motor3'), str(motor3.stepActual)), period=500)
# Optional: periodic updates to synchronize device and Node-RED
cron(lambda t: client.publish(topic('status'), b'1'), period=20000)
cron(lambda t: client.publish(topic('led'), str(1-led.value())), period=20000)
# Hmmm, dunno if I really need it
cron(lambda t: gc.collect(), period=600000)
# Debug things
cron(lambda t: print('.', end=''), period=1000)
cron(dbg_report_loops, period=1000)
cron(motor_toRTC, period=200)
cron(lambda t: oneStep(), freq=400)

try:
    print('Start MQTT main loop, press Ctrl-C to stop')
    while True:
        dbg_loop_counter += 1
        if client.check_msg() == None:
            time.sleep_ms(10)
except KeyboardInterrupt:
    print('\nStopped')
    for t in crontab:
        t.deinit()
    connect.saveRTC()


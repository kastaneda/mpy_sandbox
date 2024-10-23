import config, connect, machine, time, umqtt.robust, gc
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
def cron(ms, fn):
    global crontab
    t = machine.Timer(-1)
    t.init(mode=machine.Timer.PERIODIC, period=ms, callback=fn)
    crontab.append(t)

cron(1000, lambda t: client.ping()),
cron(5000, lambda t: client.publish(topic('vcc'), str(vcc.read()))),
cron(500, lambda t: client.publish(topic('motor1'), str(motor1.stepActual))),
cron(500, lambda t: client.publish(topic('motor2'), str(motor2.stepActual))),
cron(500, lambda t: client.publish(topic('motor3'), str(motor3.stepActual))),
# Optional: periodic updates to synchronize device and Node-RED
cron(20000, lambda t: client.publish(topic('status'), b'1')),
cron(20000, lambda t: client.publish(topic('led'), str(1-led.value()))),
# Hmmm, dunno if I really need it
cron(600000, lambda t: gc.collect()),
# Debug things
cron(1000, lambda t: print('.', end='')),
cron(1000, dbg_report_loops)
cron(200, motor_toRTC)

stepperTimer = machine.Timer(-1)
stepperTimer.init(freq=400, mode=machine.Timer.PERIODIC, callback=lambda t: oneStep())
crontab.append(stepperTimer)

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

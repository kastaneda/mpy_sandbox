import config, connect, machine, time, umqtt.robust, gc
from shift_stepper import motor1, motor2, motor3, oneStep

def topic(suffix):
    return (config.board_id + '/' + suffix).encode('ascii')

connect.loadRTC()
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

def mqtt_callback(topicName, msg):
    if topicName == topic('led/set'):
        led.value(0 if msg == b'1' else 1)
    if topicName == topic('motor1/set'):
        motor1.target(int(msg))
    if topicName == topic('motor2/set'):
        motor2.target(int(msg))
    if topicName == topic('motor3/set'):
        motor3.target(int(msg))
    if topicName == topic('sleep/set'):
        connect.deepSleep(int(msg))

client.set_callback(mqtt_callback)
client.subscribe(topic('+/set'))

class CronJob:
    def __init__(self, periodMs, callback):
        self._lastRun = 0
        self._periodMs = periodMs
        self._callback = callback
    def run(self):
        timeNow = time.ticks_ms()
        timeDiff = timeNow - self._lastRun
        if timeDiff > self._periodMs:
            self._lastRun = timeNow
            self._callback()

# Debug thing: count loops per second
dbg_loop_counter = 0

def dbg_report_loops():
    global dbg_loop_counter
    client.publish(topic('lps'), str(dbg_loop_counter))
    dbg_loop_counter = 0

crontab = [
    CronJob(1000, lambda: client.ping()),
    CronJob(5000, lambda: client.publish(topic('vcc'), str(vcc.read()))),
    CronJob(500, lambda: client.publish(topic('motor1'), str(motor1.stepActual))),
    CronJob(500, lambda: client.publish(topic('motor2'), str(motor2.stepActual))),
    CronJob(500, lambda: client.publish(topic('motor3'), str(motor3.stepActual))),
    # Optional: periodic updates to synchronize device and Node-RED
    CronJob(20000, lambda: client.publish(topic('status'), b'1')),
    CronJob(20000, lambda: client.publish(topic('led'), str(1-led.value()))),
    # Hmmm, dunno if I really need it
    CronJob(600000, lambda: gc.collect()),
    # Debug things
    CronJob(1000, lambda: print('.', end='')),
    CronJob(1000, dbg_report_loops)
]

tim = machine.Timer(-1)
tim.init(freq=400, mode=machine.Timer.PERIODIC, callback=lambda t: oneStep())

print('MQTT main loop')
while True:
    dbg_loop_counter += 1
    if client.check_msg() == None:
        time.sleep_ms(10)
    for job in crontab:
        job.run()


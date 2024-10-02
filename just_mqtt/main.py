import config, connect, machine, time, umqtt.robust

# Small shorthand for topic names
def t(suffix):
    return (config.board_id + '/' + suffix).encode('ascii')

connect.loadRTC()
connect.setupWifi()

# https://github.com/micropython/micropython-lib/blob/master/micropython/umqtt.simple/README.rst
client = umqtt.robust.MQTTClient(config.board_id, connect.wifi('mqtt'), keepalive=1)
client.set_last_will(t('status'), b'0')
client.connect()
client.publish(t('status'), b'1')

vcc = machine.ADC(1)

led = machine.Pin(2, machine.Pin.OUT)
led.value(1)
client.publish(t('led'), str(led.value()))

def mqtt_callback(topic, msg):
    #print('\nTopic:', topic, 'message:', msg)
    if topic == t('led/set'):
        led.value(1 if msg == b'1' else 0)

client.set_callback(mqtt_callback)
client.subscribe(t('+/set'))

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

crontab = [
    CronJob(1000, lambda: print('.', end='')),
    CronJob(1000, lambda: client.ping()),
    CronJob(2500, lambda: client.publish(t('vcc'), str(vcc.read()))),
    # Optional: periodic updates to synchronize device and Node-RED
    CronJob(20000, lambda: client.publish(t('status'), b'1')),
    CronJob(20000, lambda: client.publish(t('led'), str(led.value())))
]

print('MQTT main loop')
while True:
    if client.check_msg() == None:
        time.sleep_ms(50)
    for job in crontab:
        job.run()


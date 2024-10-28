import config, connect, machine, time, umqtt.robust, gc

def topic(suffix):
    return (config.board_id + '/' + suffix).encode('ascii')

connect.loadRTC()
connect.setupWifi()

client = umqtt.robust.MQTTClient(config.board_id, connect.wifi('mqtt'), keepalive=1)
client.set_last_will(topic('status'), b'0')
client.connect()
client.publish(topic('status'), b'1')

led = machine.Pin(8, machine.Pin.OUT)
led.value(1)
client.publish(topic('led'), str(1-led.value()))

def btn_callback(btn_pin):
    led.value(1-led.value())
    client.publish(topic('led'), str(1-led.value()))

btn = machine.Pin(9, machine.Pin.IN)
btn.irq(trigger=machine.Pin.IRQ_FALLING, handler=btn_callback)

def mqtt_callback(topicName, msg):
    if topicName == topic('led/set'):
        led.value(0 if msg == b'1' else 1)
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

crontab = [
    CronJob(1000, lambda: client.ping()),
    CronJob(20000, lambda: client.publish(topic('status'), b'1')),
    CronJob(20000, lambda: client.publish(topic('led'), str(1-led.value()))),
    CronJob(600000, lambda: gc.collect()),
    CronJob(1000, lambda: print('.', end=''))
]

print('MQTT main loop')
while True:
    if client.check_msg() == None:
        time.sleep_ms(10)
    for job in crontab:
        job.run()
